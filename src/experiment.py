import os
import numpy as np
from text_cue_widget import TextCueWidget
from text_image_cue_widget import TextImageCueWidget
from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtTest

import time
import pandas as pd
from helper import create_message_box

from admin_window import AdminWindow
from subject_window import SubjectWindow
class Experiment():
    def __init__(self, admin_window, subject_window, experiment_info, n_reps_per_task, debug_mode):
        self.admin_window : AdminWindow = admin_window
        self.subject_window : SubjectWindow= subject_window
        self.experiment_info = experiment_info
        self.n_reps_per_task = n_reps_per_task
        self.debug_mode = debug_mode

        task_info = experiment_info['tasks']
        self.task_names = task_info.keys()

        self.remaining_tasks = []
        for task_name in self.task_names:
            self.remaining_tasks.extend([task_name]*n_reps_per_task)
        self.remaining_tasks = np.array(self.remaining_tasks)
        np.random.shuffle(self.remaining_tasks)

        self.n_total_trials = self.remaining_tasks.shape[0]
        self.n_completed_tasks = 0
        self.completed_tasks = []

        self.admin_window.create_task_specific_counter_labels(self.task_names, n_reps_per_task)

        # create a timer object
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTimer)

        self.cue_logs = pd.DataFrame(columns=['time', 'cues'])

        label_trial_counter_text = f'Trials: {len(self.completed_tasks)} of {self.n_total_trials} done'
        self.subject_window.label_trial_counter.setText(label_trial_counter_text)
        self.admin_window.label_trial_counter.setText(label_trial_counter_text)
        


    def resume(self):
        
        # remove intro greeting widget from subject window
        # self.remove_cue_widgets(self.subject_window.vertical_layout_for_task_stages)
            
        for task in self.remaining_tasks:
            #check if pause or stop buttons were pressed during the last trial
            self.check_button_states()

            for stage_info in self.experiment_info['experiment_stages']:
                stage_name, widget_type, stage_duration, cue_display_duration = stage_info

                # create stage and log_cue label
                if stage_name.lower() == 'rest':
                    label = log_label = stage_name
                elif stage_name.lower() == 'cue':
                    label = f'Next Task: {task}'
                    log_label = 'Cue Presented'
                elif stage_name.lower() == 'action':
                    log_label = f'Action:{task}'
                    label = f'Now: {task}'

                # set widgets in subject and admin window
                self.set_subject_window_widget_for_current_task_stage(widget_type, task, label)
                self.admin_window.label_current_stage.setText(label)

                self.add_cue_marker(log_label, time.time())
                self.admin_window.trigger_photosensor_color_change_for_cue()

                # set stage duration in msecs
                stage_duration = 1 if self.debug_mode else stage_duration

                #check if cue needs to be removed after some time
                if cue_display_duration is None:
                    wait_time_to_remove_widget =  stage_duration
                    additional_wait_time = 0
                else:
                    assert stage_duration >= cue_display_duration, 'Cue-display duration is greater than stage duration'
                    wait_time_to_remove_widget = cue_display_duration
                    additional_wait_time = stage_duration - wait_time_to_remove_widget
                
                # wait required time before removing widget 
                QtTest.QTest.qWait(wait_time_to_remove_widget * 1000)
                # self.remove_cue_widgets(self.subject_window.vertical_layout_for_task_stages)
                self.dynamic_widgets[widget_type].label_cue_text.setText('')

                # wait additional time after removing widget
                QtTest.QTest.qWait(additional_wait_time * 1000)

            self.completed_tasks.append(self.remaining_tasks[0])
            np.delete(self.remaining_tasks, 0)

            # update trial counters
            label_trial_counter_text = f'Trials: {len(self.completed_tasks)} of {self.n_total_trials} done'
            self.subject_window.label_trial_counter.setText(label_trial_counter_text)
            self.admin_window.label_trial_counter.setText(label_trial_counter_text)

            #update task specific trial counters in admin window
            label = self.admin_window.task_specific_counter_labels[task]
            text_splits = label.text().split(' ')
            updated_text = [str(int(text_splits[0])+1)]
            updated_text.extend(text_splits[1:])
            new_value = ' '.join(updated_text)
            label.setText(new_value)

        # Set Thank you message of subject window
        cue_widget = self.dynamic_widgets['text_cue']
        cue_widget.label_cue_text.setText('The session has finished! \n Thanks a lot for your participation!')
        cue_widget.show()

        self.admin_window.run_visual_sync_sequence()

        file_dialog = QFileDialog.getSaveFileName(self.admin_window, 
                                                'Select filename to save cue logs', 
                                                os.path.join('..', 'results'),
                                                filter='*.csv')

        if len(file_dialog[0]) == 0:
            ret = create_message_box('The cue log file has not been saved. That data will be lost if application is closed!',
                                QMessageBox.Save, QMessageBox.Close)

            if ret == QMessageBox.Close:
                QCoreApplication.quit()
            else:
                file_dialog = QFileDialog.getSaveFileName(self.admin_window, 
                                        'Select filename to save cue logs', 
                                        os.path.join('..', 'results'),
                                        filter='*.csv')
        if len(file_dialog[0]) > 0:
            self.cue_logs.to_csv(file_dialog[0])
        
        import sys
        sys.exit(0)   

    def set_subject_window_widget_for_current_task_stage(self, widget_type, task, label):
        
        # set all but current widget visibility to False, and current one to True
        for w_type, widget in self.dynamic_widgets.items():
            if w_type == widget_type:
                widget.show()
            else: 
                widget.hide()
    
        # get the widget
        cue_widget = self.dynamic_widgets.get(widget_type)
        doesnt_exist = cue_widget is None
        if widget_type == 'text_cue':
            #create widget
            if doesnt_exist:
                cue_widget = TextCueWidget()

            cue_widget.label_cue_text.setText(label)

        elif widget_type == 'text_image_cue':
            #create widget
            if doesnt_exist:
                cue_widget = TextImageCueWidget()

            dir_path = os.path.join(self.experiment_info['resource_dir_path'], 'images')
            file_name = self.experiment_info['tasks'][task]['image_name']

            pixmap = QPixmap(os.path.join(dir_path, file_name))
            cue_widget.label_cue_image.setPixmap(pixmap)
            cue_widget.label_cue_image.adjustSize()
            cue_widget.label_cue_text.setText(label)
        
        if doesnt_exist:
            self.dynamic_widgets[widget_type] = cue_widget
            self.subject_window.vertical_layout_for_task_stages.addWidget(cue_widget)

    def run(self):
        cue_widget = TextCueWidget()
        cue_widget.label_cue.setText('Please wait for admin to start the experiment')
        # put widget in subject window
        self.subject_window.vertical_layout_for_task_stages.addWidget(cue_widget)  
        self.dynamic_widgets = dict(text_cue=cue_widget)


    def check_button_states(self):
        a=0
        # print('New Trial Started')
        #check state of stop button
        
        #check state of start pause button
        #self.pause_button_pressed

    
    def updateTimer(self):
        
        elapsed_time = time.time() - self.start_time

        # converting time to string
        label_time = self.convert_milliseconds_to_time_(elapsed_time)
  
        # change label
        self.admin_window.label_elapsed_time.setText(f'Elapsed Time: {label_time}')
        self.subject_window.label_elapsed_time.setText(f'Elapsed Time: {label_time}')

    def start_timer(self):
        # update the timer every second
        self.start_time =  time.time()
        self.timer.start(1000)

    def convert_milliseconds_to_time_(self, sec):
        min=sec//60
        h= sec//(60*60)
        sec = sec % 60
        return f'{h:02.0f}:{min:02.0f}:{sec:02.0f}'

    def add_cue_marker(self, cue, timestamp):
        self.cue_logs = self.cue_logs.append(pd.DataFrame([[timestamp, cue]], columns=['time', 'cues']))
        
