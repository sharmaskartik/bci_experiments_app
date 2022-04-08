from PyQt5.QtWidgets import QMainWindow, QApplication, QComboBox, QVBoxLayout, QSpinBox, QPushButton, QCheckBox
from PyQt5 import uic
from PyQt5.QtGui import QScreen

from subject_window import SubjectWindow
from admin_window import AdminWindow
from experiment import Experiment
import sys
import os
import copy


class BCIExperimentApp(QMainWindow):
    def __init__(self, screens):
        super(BCIExperimentApp, self).__init__()

        # Load the UI File
        uic.loadUi(os.path.join('..','ui', 'main_screen.ui'), self)

        # Define widgets
        self.combobox_select_experiment = self.findChild(QComboBox, 'comboBox_select_experiment') 
        # self.combobox_select_experiment.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.layout_task_selection = self.findChild(QVBoxLayout, 'verticalLayout_task_selection')
        self.spinbox_task_reps = self.findChild(QSpinBox, 'spinBox_task_reps')
        self.button_start_experiment = self.findChild(QPushButton, 'pushButton_start_experiment')

        from task_details import EXPERIMENTS    
        experiment_name = 'Finger Classification'
        experiment_name = 'Demo Task'


        self.combobox_select_experiment.addItem(experiment_name)


        self.experiment = EXPERIMENTS[experiment_name]
        self.checkboxes = []
        for task_name, _ in self.experiment['tasks'].items():
            checkbox = QCheckBox(text=task_name, checked=True)
            self.checkboxes.append(checkbox)
            self.layout_task_selection.addWidget(checkbox)


        # button clicked function
        self.button_start_experiment.clicked.connect(lambda: start_experiment())
        self.show()

        def start_experiment():
            keys = []
            for checkbox in self.checkboxes:
                if not checkbox.isChecked():
                    keys.append(checkbox.text())
            
            num_reps = self.spinbox_task_reps.value()
            num_reps = 25
            self.debug_mode = False
            experiment_details_copy = copy.deepcopy(self.experiment)

            for key in keys:
                experiment_details_copy['tasks'].pop(key)

            self.subject_window = SubjectWindow()
            self.admin_window = AdminWindow()
            #check if secondary screen is connected

            self.subject_window.showMaximized()
            self.admin_window.showMaximized()

            #put windows on different monitors
            if len(screens) > 1:
                screen : QScreen = screens[1]
                self.subject_window.move(screen.availableGeometry().left(), screen.availableGeometry().top())
                self.subject_window.resize(screen.availableGeometry().width(), screen.availableGeometry().height())

            screen : QScreen = screens[0]
            self.admin_window.move(screen.availableGeometry().left(), screen.availableGeometry().top())
            self.admin_window.resize(screen.availableGeometry().width(), screen.availableGeometry().height())


            experiment = Experiment(self.admin_window, self.subject_window, experiment_details_copy, num_reps, self.debug_mode)

            #set experiment in admin window
            self.admin_window.set_experiment(experiment)
            AppWindow.hide()
            experiment.run()

#Initialize the app
app = QApplication(sys.argv)
screens = app.screens()
AppWindow = BCIExperimentApp(screens)
sys.exit(app.exec_())