from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout
from PyQt5 import uic
from PyQt5.QtCore import QThread, QTimer
import PyQt5.QtGui as qtg
from PyQt5 import QtTest
from helper import close_app_dialog
import os
import time 
import numpy as np
import time
import matplotlib.ticker as ticker

class AdminWindow(QMainWindow):
    def __init__(self):
        super(AdminWindow, self).__init__()
        # Load the UI File
        uic.loadUi(os.path.join('..','ui', 'admin_experiment_screen.ui'), self)

        self.label_trial_counter = self.findChild(QLabel, 'label_trial_counter') 
        self.label_elapsed_time = self.findChild(QLabel, 'label_elapsed_time') 

        def keyPressEvent(event):
            print(event.key())

        self.label_elapsed_time.keyPressEvent = keyPressEvent

        self.label_current_stage = self.findChild(QLabel, 'label_current_stage') 
        self.label_current_stage.hide()
        self.label_photosensor_cue = self.findChild(QLabel, 'label_visual_cue') 
        self.label_photosensor_cue_2 = self.findChild(QLabel, 'label_visual_cue_2') 

        self.start_pause_button = self.findChild(QPushButton, 'pushButton_start_pause_experiment')
        self.start_pause_button.clicked.connect(lambda: start_pause_button_clicked())

        self.stop_button = self.findChild(QPushButton, 'pushButton_stop_experiment')
        self.stop_button.clicked.connect(lambda: stop_button_clicked())

        self.vertical_layout = self.findChild(QVBoxLayout, 'verticalLayout')
        self.layout_task_names = self.findChild(QVBoxLayout, 'verticalLayout_task_specific_labels')
        self.layout_task_counters = self.findChild(QVBoxLayout, 'verticalLayout_task_specific_counters')

        self.label_font = qtg.QFont('MS Shell Dlg 2', 12)

        rda_indices = [-1]
        self.canvas = PlotCanvas(self, rda_indices)
        self.vertical_layout.addWidget(self.canvas)


        def start_pause_button_clicked():
            button_text = self.start_pause_button.text().lower()
            button_state = button_text.split(' ')[0]
            
            # if current state is not started or text is start
            if button_state == 'start':
                # start experiment
                self.run_visual_sync_sequence()
                self.start_pause_button.setText('Pause Experiment')
                self.stop_button.setEnabled(True)
                self.label_current_stage.show()
                #start rda reading worker + setup plot update callbacks
                self.start_rda_reader_thread()

                self.experiment.start_timer()
                self.experiment.add_cue_marker('Experiment Start', time.time())
                self.experiment.resume()
                # change text to pause
            
            # if current state is paused or text is resume
            elif button_state == 'resume':
                # change text to pause
                self.start_pause_button.setText('Pause Experiment')
            
            #if current state is resumed or text is pause
            elif button_state == 'pause':
                # change text to resume
                self.start_pause_button.setText('Resume Experiment')
            else:
                assert False, f'Start/Pause button has unknown text: {button_text}'

        def stop_button_clicked():
            button_text = self.stop_button.text().lower()
            button_state = button_text.split(' ')[0]
            
            # if current state is not started or text is start
            if button_state == 'stop':
                # start experiment
                self.stop_button.setText('Cancel')
                self.start_pause_button.setEnabled(False)
                # change text to pause
            
            # if current state is paused or text is resume
            elif button_state == 'cancel':
                # change text to pause
                self.stop_button.setText('Stop Experiment')
                self.start_pause_button.setEnabled(True)

            else:
                assert False, f'Start/Pause button has unknown text: {button_text}'

    #override closeEvent
    def closeEvent(self, event):
        close_app_dialog(event)



    def run_visual_sync_sequence(self):
        n_reps = 1 if self.experiment.debug_mode else 5
        self.experiment.add_cue_marker('Sync Sequence', time.time())
        for i in range(n_reps):
            self.change_photosensor_label_intensity(255)
            QtTest.QTest.qWait(500)
            self.change_photosensor_label_intensity(0)
            QtTest.QTest.qWait(500)



    def set_experiment(self, experiment):
        self.experiment = experiment
    
    def create_task_specific_counter_labels(self, task_names, n_reps_per_task):
        self.task_specific_counter_labels = {}
        #create task specific labels for admin window
        for task_name in task_names:
            label_task_name = QLabel(text = f'{task_name}:', font= self.label_font)
            self.layout_task_names.addWidget(label_task_name)

            label_task_counter = QLabel(text = f'0 of {n_reps_per_task} done', font= self.label_font)
            self.layout_task_counters.addWidget(label_task_counter)
            self.task_specific_counter_labels[task_name] = label_task_counter

    def change_photosensor_label_intensity(self, intensity):
        self.label_photosensor_cue.setStyleSheet(f"background-color: rgba({intensity}, {intensity}, {intensity}, 1)")
        self.label_photosensor_cue_2.setStyleSheet(f"background-color: rgba({intensity}, {intensity}, {intensity}, 1)")

    def trigger_photosensor_color_change_for_cue(self):
        self.change_photosensor_label_intensity(int(255/5))
        from photosensor_label_update import PhotoSensorLabelUpdater
        
        # below code from https://realpython.com/python-pyqt-qthread/
        
        self.photo_sensor_thread = QThread()
    
        self.photo_sensor_worker = PhotoSensorLabelUpdater()    
        self.photo_sensor_worker.moveToThread(self.photo_sensor_thread)
    
        self.photo_sensor_thread.started.connect(self.photo_sensor_worker.run)
        self.photo_sensor_worker.finished.connect(self.photo_sensor_thread.quit)
        self.photo_sensor_worker.finished.connect(self.photo_sensor_worker.deleteLater)
        self.photo_sensor_thread.finished.connect(self.photo_sensor_thread.deleteLater)
        self.photo_sensor_worker.progress.connect(self.change_photosensor_label_intensity)

        self.timer = QTimer()
        self.timer.timeout.connect(self.draw_canvas)
        self.timer.start(4)

        self.photo_sensor_thread.start()

        
    def keyPressEvent(self, e):

        self.experiment.add_cue_marker(f'key {e.key()}', time.time())

    def start_rda_reader_thread(self):
        from rda import RDAReader
        self.rda_reader_worker = RDAReader(self.canvas)    

        self.plot_updater_thread = QThread()
        self.rda_reader_worker.moveToThread(self.plot_updater_thread)

        self.plot_updater_thread.started.connect(self.rda_reader_worker.run)
        self.rda_reader_worker.finished.connect(self.plot_updater_thread.quit)
        self.rda_reader_worker.finished.connect(self.rda_reader_worker.deleteLater)
        self.plot_updater_thread.finished.connect(self.plot_updater_thread.deleteLater)
        self.rda_reader_worker.progress.connect(self.update_plot)

        # self.rda_reader_worker.finished.connect(lambda: print('worker finished'))
        # self.rda_reader_worker.progress.connect(lambda: print('worker progress emitted'))

        self.plot_updater_thread.start()

    def update_plot(self, inputs):

        # canvas = inputs[0]
        canvas = self.canvas
        data = inputs[1][:, canvas.rda_indices]
        # print(data.shape, canvas.plotdata.shape)
        shift = len(data)
        canvas.plotdata = np.roll(canvas.plotdata, -shift, axis = 0)
        canvas.plotdata[-shift:,:] = data
        ydata = canvas.plotdata.reshape(-1)

        # print('updated', time.time(), ydata.shape[0])
        if canvas.reference_plot is None:
            plot_refs = canvas.axes.plot(ydata, color=(0,1,0.29))
            canvas.reference_plot = plot_refs[0]				
        else:
            canvas.reference_plot.set_ydata(ydata)

        min = np.min(ydata)
        max = np.max(ydata)
        diff = max - min
        canvas.axes.set_ylim(ymin = min - .1*diff, ymax=max + .1*diff)

    def draw_canvas(self):
        self.canvas.draw()

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class PlotCanvas(FigureCanvas):
    def __init__(self, parent, rda_indices, width=5, height=4, dpi=100):

        #CHANGE CODE TO DYNAMICALLY CREATE ROWS AND COLUMNS
        fig, self.axes = plt.subplots(1,1)
        fig.tight_layout()

        super().__init__(fig)
        self.setParent(parent)

        #CHECK WHAT THE LENGTH REALLY MEANS
        length = 1500
        self.rda_indices = rda_indices
        self.plotdata =  np.zeros((length, len(self.rda_indices)))
        self.reference_plot = None


        self.axes.yaxis.grid(True,linestyle='--')
        start, end = self.axes.get_ylim()
        self.axes.yaxis.set_ticks(np.arange(start, end, 0.1))
        self.axes.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))

        self.axes.set_facecolor((0,0,0))

