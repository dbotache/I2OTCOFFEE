from configparser import ConfigParser

class Manager:
    def __init__(self, path=""):
        self.configpath = path
        self.config = ConfigParser()


    def load(self):
        self.config.read(self.configpath)
        if len(self.config.sections()) > 0:
            pass
        else:
