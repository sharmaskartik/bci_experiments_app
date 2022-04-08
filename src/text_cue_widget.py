from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt5 import uic
import os

class TextCueWidget(QWidget):
    def __init__(self):
        super(TextCueWidget, self).__init__()
        # Load the UI File
        uic.loadUi(os.path.join('..','ui', 'text_only_cue_widget.ui'), self)

        self.label_cue_text : QLabel = self.findChild(QLabel, 'label_cue') 
