from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic
import os

class TextImageCueWidget(QWidget):
    def __init__(self):
        super(TextImageCueWidget, self).__init__()
        # Load the UI File
        uic.loadUi(os.path.join('..','ui', 'text_image_cue_widget.ui'), self)

        self.label_cue_text : QLabel = self.findChild(QLabel, 'label_cue') 
        self.label_cue_image : QLabel = self.findChild(QLabel, 'label_image') 
