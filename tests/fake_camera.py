from os import listdir
from os.path import isfile, join


class Camera(object):

    def __init__(self, path):
        self.files = [join(path, f) for f in listdir(path)]
        self.files = sorted([f for f in self.files if isfile(f)])
        self.current = 0

    def reset(self):
        self.current = 0

    def has_next(self):
        return self.current < len(self.files)

    def next(self):
        img = open(self.files[self.current], 'rb').read()
        self.current += 1
        return img
