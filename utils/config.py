import configparser
import os
import sys


class Config:
    mapper = {
        'common': ['server_addr', 'server_port', 'token'],
        'mc': ['local_port', 'remote_port']
    }

    def __init__(self, path=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "mc.ini")):
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path)
        self.save()

    def update(self, data):
        for key in data.keys():
            if key in [j for i in self.mapper.keys() for j in self.mapper[i]]:
                setattr(self, key, data[key])
        self.save()

    def save(self):
        for key in self.mapper.keys():
            if not self.config.has_section(key):
                self.config.add_section(key)
            for item in self.mapper[key]:
                if not self.config.has_option(key, item):
                    self.config.set(key, item, '')
                    setattr(self, item, '')
                if item in dir(self):
                    self.config.set(key, item, getattr(self, item))
                    setattr(self, item, getattr(self, item))
                else:
                    setattr(self, item, self.config.get(key, item))
        self.config.write(open(self.path, 'w'))


if __name__ == '__main__':
    config = Config()
    config.save()
