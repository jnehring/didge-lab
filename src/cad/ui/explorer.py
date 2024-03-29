from cad.ui.ui import UserInterface, StaticTextWindow, PeakWindow, MenuWindow, DictWindow
from cad.ui.fft_window import FFTWindow
import os
import pickle
from cad.ui.visualization import visualize_mutant_to_files
from cad.common.app import App

class Explorer:

    def __init__(self, pipeline_dir):
        self.pipeline_dir=pipeline_dir
        self.ui=UserInterface()
        self.mode=None
        self.loaded_pipeline=None
        self.pipeline_steps=[]
        self.mutant_pool=None
        self.visible_mutant_index=0

    def load(self, pipeline, mutant_index):
        self.visible_mutant_index=mutant_index
        self.loaded_pipeline=pipeline

    def make_header(self):
        path=self.pipeline_dir
        if self.loaded_pipeline is not None:
            path=os.path.join(path, self.loaded_pipeline + ".pkl")
        self.ui.add_window(StaticTextWindow(f"Explore {path}\n\n"))

    def pickle_loader_mode(self):
        self.mode="pickleloader"
        self.ui.clear()
        self.make_header()
        files=[]
        for f in os.listdir(self.pipeline_dir):
            step=f[0:-4]
            self.pipeline_steps.append(step)
            files.append("* " + step)

        files=sorted(files)
        
        content_str="Select a pipeline step:\n"
        content_str += "\n".join(files)
        content_str += "\n\n" 

        self.ui.add_window(StaticTextWindow(content_str))
        self.ui.display()

    def show_mutant_mode(self):
        self.mode="showmutant"
        self.ui.clear()
        self.make_header()

        f=os.path.join(self.pipeline_dir, f"{self.loaded_pipeline}.pkl")
        self.mutant_pool=pickle.load(open(f, "rb"))
        mutant=self.mutant_pool.get(self.visible_mutant_index)

        peak=mutant.cadsd_result.peaks
        fft=mutant.cadsd_result.fft
        geo=mutant.geo

        header=f"showing mutant {self.visible_mutant_index+1}/{self.mutant_pool.len()}\n\n"
        self.ui.add_window(StaticTextWindow(header))

        info={
            "didge length": f"{round(geo.geo[-1][0])}mm",
            "bell size": f"{round(geo.geo[-1][1])}mm",
            "n_segments": len(geo.geo)
        }
        self.ui.add_window(DictWindow(info, title="Info", n_columns=1))
        self.ui.add_separator()

        peak_window=PeakWindow(peak.copy())
        self.ui.add_window(peak_window)

        self.ui.add_separator()
        self.ui.add_window(FFTWindow(fft.copy()))
        
        mw=MenuWindow()

        def x(args):
            self.visible_mutant_index+=1
            self.visible_mutant_index = self.visible_mutant_index%self.mutant_pool.len()
            self.show_mutant_mode()
        def y(args):
            self.visible_mutant_index-=1
            if self.visible_mutant_index<0:
                self.visible_mutant_index=self.mutant_pool.len()-1
            self.show_mutant_mode()
        mw.add_option('x', "next mutant", x)
        mw.add_option('y', "last mutant", y)

        def savefig(args):
            project_dir=App.get_context("pipeline_dir")
            mutant=self.mutant_pool.get(self.visible_mutant_index)
            f1, f2=visualize_mutant_to_files(mutant, project_dir, str(self.visible_mutant_index))
            geofile=os.path.join(project_dir, f"{self.visible_mutant_index}.geo")
            mutant.geo.write_geo(geofile)
            text=f"... saved files to project_dir " + project_dir
            self.notification_win.set_text(text)
            self.ui.display()

        def savefig_all(args):
            project_dir=App.get_context("pipeline_dir")
            for i in range(self.mutant_pool.len()):
                mutant=self.mutant_pool.get(i)
                f1, f2=visualize_mutant_to_files(mutant, project_dir, str(i))
                geofile=os.path.join(project_dir, f"{i}.geo")
                mutant.geo.write_geo(geofile)
                text=f"... saved files {i+1}/{self.mutant_pool.len()} to {project_dir}"
                self.notification_win.set_text(text)
                self.ui.display()

        mw.add_option('s', "plot this mutant", savefig)
        mw.add_option('d', "plot all mutants", savefig_all)

        def back(args):
            self.pickle_loader_mode()

        mw.add_option('.', "go back", back)
        self.menu=mw
        self.ui.add_window(mw)

        self.notification_win=StaticTextWindow("")
        self.ui.add_window(self.notification_win)

        self.ui.display()

    def input_loop(self):
        while True:
            key=self.ui.wait_for_key()
            key=chr(key)

            if self.mode=="pickleloader":
                if key not in self.pipeline_steps:
                    continue
                self.loaded_pipeline=key
                self.visible_mutant_index=0
                self.show_mutant_mode()

            if self.mode=="showmutant":
                if not self.menu.has_key(key):
                    continue
                self.menu.run_fct(key)
            
    def start_ui(self):
        try:
            self.ui.start()

            if self.loaded_pipeline is None:
                self.pickle_loader_mode()
            else:
                self.show_mutant_mode()
            self.input_loop()
        finally:
            self.ui.end()