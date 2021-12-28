from cad.ui.ui import Window, UserInterface, StaticTextWindow, PeakWindow, MenuWindow, DictWindow
from cad.ui.fft_window import FFTWindow
import os
import pickle
from cad.common.app import App
import threading
import logging

class EvolutionUI:

    def __init__(self):
        self.ui=UserInterface()
        self.visible_mutant_index=0
        self.mutant_pool=None
        self.index_info=-1
        self.is_initialized=False
        self.infos={}
        self.mutant_pool=None

        # subscribe to generation_started event
        def generation_started(i_generation, mutant_pool):
            self.mutant_pool=mutant_pool
            self.mutant_pool.sort()
            if not self.is_initialized:
                self.initialize()
            else:
                self.update()
        App.subscribe("generation_started", generation_started)

        # subscrube to iteration_finished event
        def iteration_finished(i_iteration):
            self.infos["iteration"]=i_iteration
            self.info_window.update_dict(self.infos)
            self.ui.display()
        App.subscribe("iteration_finished", iteration_finished)

    def update(self):
        header_text=f"Evolution Display: Showing mutant {self.visible_mutant_index+1}/{self.mutant_pool.len()}\n"
        self.header.set_text(header_text)

        mutant=self.mutant_pool.get(self.visible_mutant_index)
        geo=mutant.geo
        n_generations=App.get_context("n_generations")
        i_generation=App.get_context("i_generation")
        self.infos={
            "iteration": App.get_context("i_iteration"),
            "generation": f"{i_generation}/{n_generations}",
            "loss": f"{mutant.loss:.2f}",
            "didge length": f"{round(geo.geo[-1][0])}mm",
            "bell size": f"{round(geo.geo[-1][1])}mm",
            "n_segments": len(geo.geo),
            "n_threads": App.get_context("n_threads"),
            "n_generation_size": App.get_context("n_generation_size"),
            "n_poolsize": App.get_context("n_poolsize"),
            "pipelines_dir": App.get_context("pipelines_dir")
        }
        self.info_window.update_dict(self.infos)

        self.peak_window.set_peak(mutant.cadsd_result.peaks.copy())
        self.fft_window.set_fft(mutant.cadsd_result.fft.copy())

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
            try:
                self.ui.start()
                while True:
                    key=self.ui.wait_for_key()
                    key=chr(key)
                    self.ui.print(key + "\n")
                    self.menu_window.key_pressed(key)
            except Exception as e:
                print(e)
                logging.error(e)            
            finally:
                self.ui.end()
        self.ui_thread = threading.Thread(target=thread_fct, args=())
        self.ui_thread.start()

