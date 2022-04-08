# below code from https://realpython.com/python-pyqt-qthread/
from copy import deepcopy
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from time import sleep
import queue
import numpy as np

class PhotoSensorLabelUpdater(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        sleep(.1)
        self.progress.emit(0)
        self.finished.emit()