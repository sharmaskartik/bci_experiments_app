from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout
from PyQt5 import uic
from helper import close_app_dialog
import os

class SubjectWindow(QMainWindow):
    def __init__(self):
        super(SubjectWindow, self).__init__()
        # Load the UI File
        uic.loadUi(os.path.join('..','ui', 'subject_experiment_screen.ui'), self)

        self.label_trial_counter = self.findChild(QLabel, 'label_trial_counter') 
        self.label_elapsed_time = self.findChild(QLabel, 'label_elapsed_time') 
        self.vertical_layout_for_task_stages = self.findChild(QVBoxLayout, 'verticalLayoutForTaskStages')

    #override closeEvent
    def closeEvent(self, event):
        close_app_dialog(event)