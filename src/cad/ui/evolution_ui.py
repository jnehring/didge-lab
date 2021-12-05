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

        def generation_started(i_generation, mutant_pool):
            self.mutant_pool=mutant_pool
            if not self.is_initialized:
                self.initialize()
            else:
                self.update()
        App.subscribe("generation_started", generation_started)

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
            "n_segments": len(geo.geo)
        }
        self.info_window.update_dict(self.infos)

        self.peak_window.set_peak(mutant.cadsd_result.peaks.copy())
        self.fft_window.set_fft(mutant.cadsd_result.fft.copy())

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

    # def update_info(self):
    #     if self.mutant_pool==None:
    #         return
        
    #     geo=self.mutant_pool.get(self.visible_mutant_index)
    #     info={
    #         "iteration": App.get_context("i_iteration"),
    #         "didge length": f"{round(geo.geo[-1][0])}mm",
    #         "bell size": f"{round(geo.geo[-1][1])}mm",
    #         "n_segments": len(geo.geo)
    #     }
    #     info_window=DictWindow(info, title="Info", n_columns=2)
    #     if self.index_info<0:
    #         self.index_info=self.ui.add_window(info_window)
    #     else:
    #         self.ui.replace_window(info_window, self.index_info)

    # def update_info(self):
    #     self.mode="showmutant"
    #     self.ui.clear()
        
    #     f=os.path.join(self.pipeline_dir, f"{self.loaded_pipeline}.pkl")
    #     self.mutant_pool=pickle.load(open(f, "rb"))
    #     mutant=self.mutant_pool.get(self.visible_mutant_index)

    #     peak=mutant.cadsd_result.peaks
    #     fft=mutant.cadsd_result.fft
    #     geo=mutant.geo

    #     header=f"showing mutant {self.visible_mutant_index+1}/{self.mutant_pool.len()}\n\n"
    #     self.ui.add_window(StaticTextWindow(header))

    #     info={
    #         "didge length": f"{round(geo.geo[-1][0])}mm",
    #         "bell size": f"{round(geo.geo[-1][1])}mm",
    #         "n_segments": len(geo.geo)
    #     }
    #     self.ui.add_window(DictWindow(info, title="Info", n_columns=1))
    #     self.ui.add_separator()

    #     peak_window=PeakWindow(peak)
    #     self.ui.add_window(peak_window)

    #     self.ui.add_separator()
    #     self.ui.add_separator()
    #     self.ui.add_window(FFTWindow(fft))
        
    #     mw=MenuWindow()

    #     def x(args):
    #         self.visible_mutant_index+=1
    #         self.visible_mutant_index = self.visible_mutant_index%self.mutant_pool.len()
    #         self.show_mutant_mode()
    #     def y(args):
    #         self.visible_mutant_index-=1
    #         if self.visible_mutant_index<0:
    #             self.visible_mutant_index=self.mutant_pool.len()-1
    #         self.show_mutant_mode()
    #     def back(args):
    #         self.pickle_loader_mode()
    #     mw.add_option('x', "next mutant", x)
    #     mw.add_option('y', "last mutant", y)
    #     mw.add_option('.', "go back", back)
    #     self.menu=mw
    #     self.ui.add_window(mw)  
            
    #     self.ui.display()

