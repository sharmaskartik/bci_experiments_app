from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMessageBox
import sys

def close_app_dialog(event):
    ret = create_message_box(u"Are you sure to close the application?")

    if ret == QMessageBox.Ok:
        event.accept()
        sys.exit(0)
        
    else:
        event.ignore()

def create_message_box(text, b1=None, b2=None):
    Error = QMessageBox()
    Error.setIcon(QMessageBox.Question)
    Error.setWindowTitle('WARNING !!')
    Error.setInformativeText(text)
    if b1 is None:
        b1 = QMessageBox.Ok
    if b2 is None:
        b2 = QMessageBox.Cancel
    Error.setStandardButtons(b1 | b2)
    return Error.exec_()