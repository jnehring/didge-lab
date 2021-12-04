import curses
import numpy as np
from abc import ABC, abstractmethod
import shutil

class UserInterface:

    def __init__(self):
        self.screen=None
        self.is_initialized=False
        self.windows=[]

    def start(self):
        if self.is_initialized:
            return
        self.screen = curses.initscr()
        self.is_initialized=True

    def add_window(self, win):
        self.windows.append(win)

    def clear(self):
        self.windows=[]

    def add_separator(self):
        self.windows.append(StaticTextWindow("\n"))

    def wait_for_key(self):
        return self.screen.getch()

    def render(self):
        content_str=[]
        for w in self.windows:
            content_str.append(w.render())
        content_str="".join(content_str)
        return content_str

    def display(self):
        self.screen.erase()
        self.screen.addstr(self.render())
        self.screen.refresh()

    def print(self, s):
        self.screen.addstr(s)
        

    def end(self):
        if self.is_initialized:
            curses.endwin()
        self.stop=True

class Window(ABC):

    def __init__(self, title=None):
        self.title=title

    def render(self):
        content_str=""
        if self.title is not None:
            content_str+=self.title + "\n"
        content_str += self._render()
        return content_str

    @abstractmethod
    def _render(self):
        pass

class DictWindow(Window):

    def __init__(self, data, n_columns=2, title=None):
        Window.__init__(self, title)
        self.content_str=self.dict_to_table(data, n_columns)

    def dict_to_table(self, data, n_columns):        
        content_str=""
        column_width=int(np.floor((shutil.get_terminal_size().columns)/n_columns))-3

        if column_width>30:
            column_width=30
        labels=list(data.keys())
        n_rows=int(np.ceil(len(labels)/n_columns))

        for y in range(n_rows):
            row=""
            for x in range(n_columns):

                pos=y*n_columns+x
                
                if pos>=len(labels):    

                    continue
                label=str(labels[pos])
                value=str(data[label])

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
            content_str += row 
        return content_str
    
    def _render(self):
        return self.content_str

class StaticTextWindow(Window):

    def __init__(self, static_str):
        Window.__init__(self)
        self.static_str=static_str

    def _render(self):
        return self.static_str

class PeakWindow(Window):

    def __init__(self, peak):

        Window.__init__(self,"Tuning")
        peak.impedance=peak.impedance.apply(lambda x : f"{x:.2e}")
        peak["cent-diff"]=peak["cent-diff"].apply(lambda x : f"{x:.2f}")
        self.content=peak.to_string()

    def _render(self):
        return self.content

class MenuWindow(Window):

    def __init__(self):
        Window.__init__(self)
        self.fcts={}
        self.labels={}

    def add_option(self, key, label, fct):
        self.fcts[key]=fct
        self.labels[key]=label

    def _render(self):
        menu="keys "
        keys=list(self.fcts.keys())
        menu += ", ".join([key + ": " + self.labels[key] for key in keys])
        return menu

    def has_key(self, key):
        return key in self.fcts.keys()

    def run_fct(self, key, args=()):
        self.fcts[key](args)

