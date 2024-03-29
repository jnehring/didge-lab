from cad.ui.ui import Window, UserInterface, StaticTextWindow, PeakWindow, MenuWindow, DictWindow
from cad.ui.fft_window import FFTWindow
import os
import pickle
from cad.common.app import App
import threading
import logging
import time
import atexit

# readable string representation of time in seconds 
def format_time(t):
    unit="s"
    units=["m", "h", "d"]
    mults=[60, 60, 24]

    for i in range(len(units)):
        if t>=mults[i]:
            t/=mults[i]
            unit=units[i]
        else:
            break
    return f"{t:.2f}{unit}"

class EvolutionUI:

    def __init__(self):

        self.ui=UserInterface(App.get_config()["hide_ui"])
        self.visible_mutant_index=0
        self.mutant_pool=None
        self.index_info=-1
        self.is_initialized=False
        self.infos={}
        self.mutant_pool=None
        self.start_time=0
        self.evolution_has_started=False

        # subscribe to generation_started event
        def generation_started(i_generation, mutant_pool):
            if i_generation==0:
                self.start_time=time.time()
            else:
                time_elapsed=time.time()-self.start_time
                time_left=App.get_context("n_generations")*time_elapsed/i_generation

                self.infos["time elapsed"] = format_time(time_elapsed)
                self.infos["time left"] = format_time(time_left)

                self.info_window.update_dict(self.infos)

            self.mutant_pool=mutant_pool
            self.mutant_pool.sort()
            
            if not self.is_initialized:
                self.initialize()
            else:
                self.update()

            self.evolution_has_started=True

        if not App.get_config()["hide_ui"]:
            App.subscribe("generation_started", generation_started)

        def update_ui_timer():
            while not self.ui.killed:
                try:

                    if self.evolution_has_started:
                        n_iterations=App.get_context("n_generation_size") * App.get_config()["n_poolsize"]
                        i_iterations=App.get_context("i_iteration")
                        self.infos["iteration"]=f"{i_iterations}/{n_iterations}"
                        time_elapsed=time.time()-self.start_time
                        self.infos["time elapsed"] = format_time(time_elapsed)
                        self.info_window.update_dict(self.infos)
                        self.ui.display()
                    time.sleep(0.2)
                except Exception as e:
                    App.log_exception(e)

        if not App.get_config()["hide_ui"]:
            self.update_ui_thread=threading.Thread(target=update_ui_timer)
            self.update_ui_thread.start()

        # shut down when pipeline is finished
        def shutdown():
            self.ui.end()
        if not App.get_config()["hide_ui"]:
            App.subscribe("pipeline_finished", shutdown)

        # register a shutdown hook to close ui when application closes
        atexit.register(shutdown)

    def update(self):

        header_text=f"Evolution Display: Showing mutant {self.visible_mutant_index+1}/{self.mutant_pool.len()}\n"
        self.header.set_text(header_text)

        mutant=self.mutant_pool.get(self.visible_mutant_index)
        geo=mutant.geo
        i_generation=App.get_context("i_generation")

        pipeline_step=App.get_context("pipeline_step_name")
        pipeline_step += " (" + str(App.get_context("current_pipeline_step")+1)
        pipeline_step += "/" + str(App.get_context("pipeline_length")) + ")"
        
        n_generations=App.get_context("n_generations")
        n_iterations=App.get_context("n_generation_size") * App.get_config()["n_poolsize"]
        i_iterations=App.get_context("i_iteration")
        self.infos={
            "iteration": f"{i_iterations}/{n_iterations}",
            "generation": f"{i_generation+1}/{n_generations}",
            "pipeline step": pipeline_step,
            "pool size": App.get_config()["n_poolsize"],
            "didge length": f"{round(geo.geo[-1][0])}mm",
            "bell size": f"{round(geo.geo[-1][1])}mm",
            "n_segments": len(geo.geo),
            "n_threads": App.get_context("n_threads"),
            "n_generation_size": App.get_context("n_generation_size"),
            "n_poolsize": App.get_context("n_poolsize")
        }
        for key, value in mutant.loss.items():
            self.infos[key]=f"{value:.2f}"
        self.info_window.update_dict(self.infos)

        self.peak_window.set_peak(mutant.geo.get_cadsd().get_notes().copy())

        spektra=mutant.geo.get_cadsd().get_all_spektra_df()
        self.fft_window.set_fft(spektra.copy())

    # build user interface
    def initialize(self):

        self.header=StaticTextWindow("")
        self.ui.add_window(self.header)
        self.ui.add_separator()

        self.info_window=DictWindow(self.infos, n_columns=2)
        self.ui.add_window(self.info_window)
        self.ui.add_separator()

        self.peak_window=PeakWindow()
        self.ui.add_window(self.peak_window)
        self.ui.add_separator()

        self.fft_window=FFTWindow()
        self.ui.add_window(self.fft_window)
    
        self.update()
        self.is_initialized=True

        self.menu_window=MenuWindow()

        def x(args):
            self.visible_mutant_index+=1
            self.visible_mutant_index = self.visible_mutant_index%self.mutant_pool.len()
            self.update()
        def y(args):
            self.visible_mutant_index-=1
            if self.visible_mutant_index<0:
                self.visible_mutant_index=self.mutant_pool.len()-1
            self.update()
        self.menu_window.add_option('x', "next mutant", x)
        self.menu_window.add_option('y', "last mutant", y)
        self.ui.add_window(self.menu_window)  

        # keyboard input thread
        def thread_fct():
            error_count=0
            while True:
                try:
                    self.ui.start()
                    key=self.ui.wait_for_key()
                    if key is None:
                        break
                    key=chr(key)
                    # self.ui.print(key + "\n")
                    self.menu_window.key_pressed(key)
                    error_count=0
                except Exception as e:
                    App.log_exception(e)
        
        if not App.get_config()["hide_ui"]:
            self.ui_thread = threading.Thread(target=thread_fct, args=())
            self.ui_thread.start()

