import curses
import time
import pandas as pd
import shutil
import numpy as np
import threading

class EvolutionDisplay:

    def __init__(self, n_generations, n_generation_size, poolsize, n_threads, pipeline_step):
        self.n_generations=n_generations
        self.n_generation_size=n_generation_size
        self.cache=""
        self.disabled=False
        self.is_initialized=False
        self.i_iteration=0
        self.n_total=n_generations*n_generation_size*poolsize
        self.i_generation=1
        self.start_time=time.time()
        self.cache_didge_geometry=None
        self.visible_mutant_index=None
        self.pool=None
        self.stop=False

        self.infos={
            "generation_size": n_generation_size,
            "pool_size": poolsize,
            "n_threads": n_threads,
            "pipeline_step": pipeline_step
        }

        self.ui_thread = None

    # call this to change iteration counter only
    def update_iteration(self):
        self.i_iteration+=1
        self.visualize()

    def format_timespan(self, time_left):
        unit="seconds"
        if time_left>60: 
            time_left/=60
            unit="minutes"
        if time_left>60:
            time_left/=60
            unit="hours"
        if time_left>24:
            time_left/=24
            unit="days"
        time_left=round(time_left, 2)
        rest_time=str(time_left) + " " + unit
        return rest_time

    # call this when 
    def update_generation(self, i_generation, pool):

        self.i_generation=i_generation
        self.pool=pool

        if self.visible_mutant_index==None:
            self.visible_mutant_index=0

        self.infos["best loss"]=pool.get_best_loss()
        self.infos["mean loss"]=pool.get_mean_loss()
        rest_time="?"
        if i_generation>1:
            elapsed_time=time.time()-self.start_time
            time_left=self.n_generations * elapsed_time / self.i_generation     
            rest_time=self.format_timespan(time_left)
        self.infos["remaining time"]=rest_time

        best_entry=pool.get_best_entry()

        e=pool.get_best_entry()
        geo=e.geo.geo
        self.infos["length"]=f"{geo[-1][0]:.2f} mm"
        self.infos["bell size"]=f"{geo[-1][1]:.2f} mm"
        self.infos["geo n segments"]=f"{len(geo)}"

        cache=""
        if e.cadsd_result != None:
            peaks=e.cadsd_result.peaks.copy()
            peaks.impedance=peaks.impedance.apply(lambda x : f"{x:.2e}")
            peaks["cent-diff"]=peaks["cent-diff"].apply(lambda x : f"{x:.2f}")
            
            cache += self.make_heading("best didge tuning")
            cache += peaks.to_string() + "\n"
            cache += self.make_heading("best didge fft")
            cache += self.fft_chart(e.cadsd_result.fft.copy())

#            self.stdscr.addstr(f"{imp:.2e}")
            
        self.cache=cache

        self.visualize()

    def make_heading(self, label):
        sep=""
        #sep="-"*(shutil.get_terminal_size().columns-1)
        return sep + "\n" + label + "\n"

    def start_ui_thread(self):
        def ui_thread_function(ed:EvolutionDisplay):
            while not ed.stop:
                char = ed.stdscr.getch()
                ed.visible_mutant_index+=1
                ed.visualize()

        self.ui_thread=threading.Thread(target=ui_thread_function, args=(self,))
        self.ui_thread.start()

    def visualize(self):

        if self.disabled:
            return
        if not self.is_initialized:
            self.stdscr = curses.initscr()
            self.is_initialized=True
            self.start_ui_thread()

        self.stdscr.erase()

        # make heading
        heading="mutant: "
        if self.visible_mutant_index==None:
            heading+="not initialized"
        else:
            heading+=f"{self.visible_mutant_index+1}/{self.pool.len()}"
        heading += "\n\n"
        self.stdscr.addstr(heading)

        # make info screen
        n_columns=2
        column_width=int(np.floor((shutil.get_terminal_size().columns)/2))-3

        self.stdscr.addstr("Infos\n")
        #labels=sorted(list(self.infos.keys()))
        labels=list(self.infos.keys())
        n_rows=int(np.ceil(len(labels)/n_columns))
        
        for y in range(n_rows):
            row=""
            for x in range(n_columns):

                pos=y*n_columns+x
                
                if pos>=len(labels):    

                    continue
                label=str(labels[pos])
                value=str(self.infos[label])

                padding=column_width-(len(label)+len(value))

                cell=label
                if padding>0:
                    cell+=" "*padding
                cell+=value
                if len(cell)>column_width:
                    cell=row[0:column_width-3] + "..."
                cell += "  "
                row += cell
            row += "\n" 
            self.stdscr.addstr(row)
                # self.stdscr.addstr(label+"\n")
                # self.stdscr.addstr(label+"\n")

        try:
            self.stdscr.addstr(self.cache)
        except Exception as e:
            pass
        self.stdscr.refresh()

    def fft_chart(self, df):

        width=(shutil.get_terminal_size().columns-1) - len("1.0e+01 | ")
        height=15
        
        bins=[]

        maximum=df.impedance.max()

        df.impedance=np.log2(df.impedance)

        mini=df.impedance.min()

        bin_size=(df.freq.max()-df.freq.min())/width
        freq=df.freq.min()
        for i in range(width):
            y=df[(df.freq>=freq) & (df.freq<freq+bin_size)].impedance.max()
            #y=df[(df.freq>=freq) & (df.freq<freq+bin_size)].impedance.max()
            bins.append(y)
            freq+=bin_size

        bins=np.array(bins)
        bins-=bins.min()
        maxi=bins.max()
        bins=bins*height/maxi
        bins=np.array([round(x) for x in bins])

        
        ticks=[mini, (maxi-mini)/2, maxi]
        ticks=[f"{x:.2e}" for x in ticks]

        chart=""
        for y in range(height):

            row=""
            tick=""

            for x in range(width):
                if bins[x]>=height-y:
                    row+="x"
                    tick=f"{(2^bins[x]):.1e}"
                else:
                    row += " "
            chart += tick + " | "+ row + "\n"

        num_ticks=4
        min_freq=str(int(df.freq.min())) + " "
        max_freq=" " + str(int(df.freq.max()))

        label = " frequency (hz) "
        pad=width - len(min_freq) - len(max_freq) - len(label)
        pad/=2
        pad="-"*int(np.ceil(pad))
        ticks=(" " * (len(tick)+3)) + min_freq + pad + label + pad + max_freq
        chart += ticks + "\n"
        
        return chart

    def end(self):
        if self.is_initialized:
            curses.endwin()
        self.stop=True
