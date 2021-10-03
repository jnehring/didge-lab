import configparser

class App:

    config=None

    @classmethod
    def get_config(cls, path="config.ini"):
        if App.config==None:
            App.config = configparser.ConfigParser()
            App.config.read(path)
        return App.config
