import configargparse
import logging
from threading import Lock
import json
import sys
import os

class App:

    config=None
    context={}
    subscribers={}

    @classmethod
    def set_context(cls, key, value):
        App.context[key]=value

    @classmethod
    def get_context(cls, key, default=None):
        if not key in App.context:
            return default
        val=App.context[key]
        return val

    @classmethod
    def init(cls):
        # add config to context
        for key, value in App.get_config().items():
            App.set_context(key, value)

    @classmethod
    def init_logging(self):
        logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] {%(filename)s:%(lineno)d} %(message)s")
        rootLogger = logging.getLogger()

        log_dir="./"
        fileHandler = logging.FileHandler(os.path.join(log_dir, "log.txt"))
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

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

        # logging.basicConfig(level=logging.INFO, format='%(asctime)s - {%(filename)s:%(lineno)d} - %(levelname)s: %(message)s', filename="log.txt")
        # logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

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
    def full_init(self):
        App.init()
        App.init_logging()
        App.start_message()

    @classmethod
    def get_config(cls, path="config.ini"):
        if App.config==None:
            p = configargparse.ArgParser(default_config_files=['./*.conf'])
            p.add('-no_cache', action='store_true', help='disable pipeline caching. default=False')
            p.add('-n_threads', type=int, default=20, help='number of threads')
            p.add('-n_poolsize', type=int, default=10, help='pool size')
            p.add('-n_generations', type=int, default=1000, help='number of generations')
            p.add('-n_generation_size', type=int, default=30, help='generation size')
            p.add('-pipelines_dir', type=str, default="projects/pipelines/", help='project directory')
            p.add('-pipeline_name', type=str, default="default", help='name of pipeline')
            p.add('-hide_ui', action='store_true', default=False, help='not not show ui.')
            p.add('-log_level', type=str, choices=["info", "error", "debug", "warn"], default="info", help='log level ')

            options = p.parse_args()

            App.config=vars(options)

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