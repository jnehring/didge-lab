import configargparse
import logging
import json
import sys
import os
from datetime import datetime
from multiprocessing import Manager, Lock
#import warnings
#warnings.filterwarnings('error')


class App:

    config=None
    manager=Manager()

    context=manager.dict()
    context_lock=Lock()

    subscribers={}
    output_folder=None

    @classmethod
    def set_context(cls, key, value):
        App.context_lock.acquire()
        try:
            App.context[key]=value
        finally:
            App.context_lock.release()

    @classmethod
    def get_context(cls, key, default=None):
        App.context_lock.acquire()
        try:
            if not key in App.context:
                return default
            val=App.context[key]
            return val
        finally:
           App.context_lock.release()

    @classmethod
    def init(cls):
        # add config to context
        for key, value in App.get_config().items():
            App.set_context(key, value)

        App.set_context("state", "initializing")

    @classmethod
    def init_logging(self, filename="./log.txt"):
        logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] {%(filename)s:%(lineno)d} %(message)s")
        rootLogger = logging.getLogger()

        fileHandler = logging.FileHandler(filename)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

        # print to console only if we have no user interface
        if App.get_config()["hide_ui"]:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            rootLogger.addHandler(consoleHandler)

        level=self.get_config()["log_level"]
        if level == "info":
            rootLogger.setLevel(logging.INFO)
        elif level == "debug":
            rootLogger.setLevel(logging.DEBUG)
        elif level == "error":
            rootLogger.setLevel(logging.ERROR)
        elif level == "warn":
            rootLogger.setLevel(logging.WARN)

    @classmethod
    def start_message(self):
        msg='''
 _____  _     _              _           _     
|  __ \(_)   | |            | |         | |    
| |  | |_  __| | __ _  ___  | |     __ _| |__  
| |  | | |/ _` |/ _` |/ _ \ | |    / _` | '_ \ 
| |__| | | (_| | (_| |  __/ | |___| (_| | |_) |
|_____/|_|\__,_|\__, |\___| |______\__,_|_.__/ 
                 __/ |                         
                |___/                          
'''
        logging.info(msg)

    @classmethod
    def full_init(self, name="default"):
        App.init()
        outfolder=App.get_output_folder()
        log_file=os.path.join(outfolder, "log.txt")
        App.init_logging(filename=log_file)
        App.start_message()

    @classmethod
    def get_config(cls, path="config.ini"):
        if App.config==None:
            p = configargparse.ArgParser(default_config_files=['./*.conf'])
            p.add('-no_cache', action='store_true', help='disable pipeline caching. default=False')
            p.add('-n_threads', type=int, default=20, help='number of threads')
            p.add('-n_poolsize', type=int, default=10, help='pool size')
            p.add('-n_generations', type=int, help='number of generations')
            p.add('-n_generation_size', type=int, help='generation size')
            p.add('-pipelines_dir', type=str, default="projects/pipelines/", help='project directory')
            p.add('-output_folder', type=str, default="output", help='output folder')
            p.add('-pipeline_name', type=str, default="default", help='name of pipeline')
            p.add('-hide_ui', action='store_true', default=False, help='not not show ui.')
            p.add('-log_level', type=str, choices=["info", "error", "debug", "warn"], default="info", help='log level ')

            options = p.parse_args()

            App.config=App.manager.dict()
            for key, value in vars(options).items():
                App.config[key]=value

        return App.config

    @classmethod
    def set_config(cls, key, value):
        App.get_config()
        App.config[key]=value

    @classmethod
    def publish(cls, topic, args=None):

        logging.debug(f"app.publish topic={topic}, args={args}")
        try:
            if topic not in App.subscribers:
                return
            for s in App.subscribers[topic]:
                if args is None:
                    s()
                else:
                    s(*args)
        except Exception as e:
            App.log_exception(e)

    @classmethod
    def subscribe(cls, topic, fct):
        if topic not in App.subscribers:
            App.subscribers[topic]=[]
        App.subscribers[topic].append(fct)

    @classmethod
    def log_exception(cls, e : Exception):
        ctx=json.dumps(App.context)
        logging.error("An exception has occured. App context:\n" + ctx)
        logging.exception(e)

    @classmethod
    def get_output_folder(cls, suffix=""):

        if App.output_folder is None:

            f=App.get_config()["output_folder"]

            if not os.path.exists(f):
                os.mkdir(f)

            my_date = datetime.now()

            folder_name=my_date.strftime('%Y-%m-%dT%H-%M-%S')
            folder_name += "_" + App.get_config()["pipeline_name"]
            if len(suffix)>0:
                folder_name += "_" + suffix

            App.output_folder=os.path.join(f, folder_name)
            os.mkdir(App.output_folder)

        return App.output_folder