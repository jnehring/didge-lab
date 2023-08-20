import logging
import sys
import os
from datetime import datetime
import configargparse

class App:
    
    subscribers = {}
    output_folder = None
    config = None

    services = {}

    # register services in the app to make them available from other parts of the application
    @classmethod
    def register_service(cls, service):
        App.services[type(service)] = service

    @classmethod
    def get_service(cls, service_type):
        if service_type in App.services.keys():
            return App.services[service_type]
        else:
            return None

    @classmethod
    def get_config(cls, path="config.ini"):
        if App.config==None:
            p = configargparse.ArgParser(default_config_files=['./*.conf'])
            p.add('-n_threads', type=int, default=8, help='number of threads', env_var='N_THREADS')
            p.add('-log_level', type=str, choices=["info", "error", "debug", "warn"], default="info", help='log level ')

            options = p.parse_known_args()[0]

            App.config={}
            for key, value in vars(options).items():
                App.config[key]=value

        return App.config

    # publish / subscribe pattern for data exchange between services
    @classmethod
    def publish(cls, topic, args=None):
        logging.debug(f"app.publish topic={topic}, args={args}")
        if topic not in App.subscribers:
            return
        for s in App.subscribers[topic]:
            if args is None:
                s()
            elif type(args) == tuple:
                s(*args)
            else:
                s(args)

    @classmethod
    def subscribe(cls, topic, fct):
        if topic not in App.subscribers:
            App.subscribers[topic]=[]
        App.subscribers[topic].append(fct)


    @classmethod
    def init_logging(self, filename="./log.txt"):
        logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] {%(filename)s:%(lineno)d} %(message)s")
        rootLogger = logging.getLogger()

        fileHandler = logging.FileHandler(filename)
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
        msg += "Starting " + " ".join(sys.argv)
        logging.info(msg)

    @classmethod
    def full_init(self, name="default"):
        outfolder=App.get_output_folder()
        log_file=os.path.join(outfolder, "log.txt")
        App.init_logging(filename=log_file)
        App.start_message()

    @classmethod
    def get_output_folder(cls, suffix=""):

        if App.output_folder is None:

            f = "../evolutions/"

            if not os.path.exists(f):
                os.mkdir(f)

            my_date = datetime.now()

            folder_name=my_date.strftime('%Y-%m-%dT%H-%M-%S')
            if len(suffix)>0:
                folder_name += "_" + suffix

            App.output_folder=os.path.join(f, folder_name)
            os.mkdir(App.output_folder)

        return App.output_folder