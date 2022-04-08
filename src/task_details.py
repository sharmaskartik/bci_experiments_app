import os

RESOURCES_DIR = os.path.join('..', 'experiment_resources')

EXPERIMENTS = {
    'Finger Classification': {
        'resource_dir_path' : 'path_to_dir',
        'tasks' : {
            'Thumb' : {
                'image_name':'',
                'audio_file_name':'',
            },
            'Index Finger': {
                'image_name':'',
                'audio_file_name':'',
            },
            'Middle Finger': {
                'image_name':'',
                'audio_file_name':'',
                'cue': [0.6 * 255, 1, 0]
            },
            'Ring Finger': {
                'image_name':'',
                'audio_file_name':'',
                'cue': [0.8 * 255, 1, 0]
            },
            'Pinky Finger': {
                'image_name':'',
                'audio_file_name':'',
                'cue': [255, 1, 0]
            }
        },
        # 'experiment_stages': [['Rest', 'text_cue', 8], ['Cue', 'text_cue', 4], ['Action', 'text_cue', 4]]
        'experiment_stages': [['Rest', 'text_cue', 1], ['Cue', 'text_image_cue', 1], ['Action', 'text_cue', 1]]
    },


    'Demo Task': {
        'resource_dir_path' : os.path.join(RESOURCES_DIR, 'demo_task'),
        'tasks' : {
            'Perform Movement' : {
                'image_name':'movement.png',
                'audio_file_name':'',
            },
            'Stay Still': {
                'image_name':'stay_still.png',
                'audio_file_name':'',
            }
        },
        'experiment_stages': [['Rest', 'text_cue', 5, None], ['Cue', 'text_image_cue', 3, None], ['Action', 'text_cue', 6 , 1]]
    }
}