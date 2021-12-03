import curses
import time
import pandas as pd
import shutil
import numpy as np

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
        self.progress_cache={
            "generation_size": n_generation_size,
            "pool_size": poolsize,
            "n_threads": n_threads,
            "pipeline_step": pipeline_step
        }

    def update_iteration(self):
        self.i_iteration+=1
        self.visualize()

    def update_generation(self, i_generation, pool):

        self.i_generation=i_generation

        self.progress_cache["best loss"]=pool.get_best_loss()
        self.progress_cache["mean loss"]=pool.get_mean_loss()
        rest_time="?"
        if i_generation>1:
            elapsed_time=time.time()-self.start_time
            time_left=self.n_generations * elapsed_time / self.i_generation
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
        self.progress_cache["remaining time"]=rest_time

        best_entry=pool.get_best_entry()

        cache=""

        e=pool.get_best_entry()
        self.new_df()
        self.add("length", f"{e.geo.geo[-1][0]:.2f} mm")
        self.add("bell size", f"{e.geo.geo[-1][1]:.2f} mm")
        cache += self.get_df("best didge geometry")

        if e.cadsd_result != None:
            peaks=e.cadsd_result.peaks.copy()
            peaks.impedance=peaks.impedance.apply(lambda x : f"{x:.2e}")
            peaks["cent-diff"]=peaks["cent-diff"].apply(lambda x : f"{x:.2f}")
            cache += self.make_section(peaks, "best didge tuning", show_header=True)
            cache += self.get_sep()
            cache += "best didge fft\n"
            cache += self.fft_chart(e.cadsd_result.fft.copy())

        self.cache=cache

        self.visualize()

    def new_df(self):
        self.df={"label": [], "value": []}

    def add(self, label, value):
        self.df["label"].append(label)
        self.df["value"].append(value)

    def get_sep(self):
        return "-"*(shutil.get_terminal_size().columns-1) + "\n"

    def get_df(self, header):
        df=pd.DataFrame(self.df)
        header=self.get_sep() + header + "\n" + "\n"
        return header + df.to_string(index=False, header=False) + "\n\n"

    def make_section(self, df, header, show_header=False):
        header=self.get_sep() + header + "\n"  + "\n"
        return header + df.to_string(index=False, header=show_header) + "\n\n"

    def visualize(self):
        if self.disabled:
            return
        if not self.is_initialized:
            self.stdscr = curses.initscr()
            self.is_initialized=True

        self.stdscr.erase()
        #self.stdscr.addstr(f"best loss: {best_loss:.2f}")
        #self.stdscr.addstr(f"generation: {i_generation}")

        self.new_df()
        self.add("iteration", f"{self.i_iteration}/{self.n_total}")
        self.add("generation", f"{self.i_generation}/{self.n_generations}")
        for key, value in self.progress_cache.items():
            self.add(key, value)

        self.stdscr.addstr(self.get_df("evolution progress"))

        try:
            self.stdscr.addstr(self.cache)
        except Exception as e:
            pass
        self.stdscr.refresh()

    def fft_chart(self, df):

        width=(shutil.get_terminal_size().columns-1)
        height=15
        
        bins=[]

        maximum=df.impedance.max()

        df.impedance=np.log2(df.impedance)
        df.impedance -= df.impedance.min()

        bin_size=(df.freq.max()-df.freq.min())/width
        freq=df.freq.min()
        for i in range(width):
            y=df[(df.freq>=freq) & (df.freq<freq+bin_size)].impedance.max()
            bins.append(y)
            freq+=bin_size
        bins=np.array(bins)
        bins-=bins.min()
        bins=bins*height/bins.max()
        bins=np.array([round(x)-1 for x in bins])

        chart=""
        for y in range(height):
            for x in range(width):
                if bins[x]>=height-y:
                    chart+="x"
                else:
                    chart += " "
            chart += "\n"

        num_ticks=4
        min_freq=str(int(df.freq.min())) + " "
        max_freq=" " + str(int(df.freq.max()))

        label = " frequency (hz) "
        pad=width - len(min_freq) - len(max_freq) - len(label)
        pad/=2
        pad="-"*int(pad)
        ticks=min_freq + pad + label + pad + max_freq
        chart += ticks + "\n"
        
        return chart

    def end(self):
        if self.is_initialized:
            curses.endwin()
