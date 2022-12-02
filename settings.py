from enum import Enum
import os
# Modes
DEBUG_MODE = True  
JUPYTER_NB = 0
OS = 1


home_path = os.path.dirname(os.path.abspath(__file__))

# General Model
DETECTION_PROBABILITY = 75
person_string = 'person'
model_name = "resnet50_coco_best_v2.1.0.h5"
model_path = home_path

# Facial Recogniton Model (Deepface)
model = "Facenet512"
metric = "euclidean_l2"

class DatabaseFormat(Enum):
    CSV=1
    INVERTED_INDEX_CSV=2
    MONGODB=3
    JSON=4
    


DATABASE_FORMAT = DatabaseFormat.JSON
# Paths


knwn_ppl_imgs_folder_name = "known_people_images"
knwn_ppl_imgs_path = os.path.join(home_path , knwn_ppl_imgs_folder_name )

database_path = home_path
database_file_name = 'memcator_database.json'
database_file_path = os.path.join(database_path , database_file_name )

filepaths_database_path = ''
# Database Information
to_be_checked_string = "TBC"
image_file_types = ('.jpg','.jpeg','.png','.tiff')

     
classes_in_coco = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
'truck', 'boat', 'traffic light', 'fire hydrant', 
'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 
'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 
'handbag', 'tie', 'suitcase', 'frisbee', 'skis','snowboard', 'sports ball',
'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 
'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 
'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 
'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 
'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

classes_coco_people = classes_in_coco # Contains classes of people and objects

for root, dirs, files in os.walk(knwn_ppl_imgs_path):
    for file in files:
        split_string = os.path.splitext(file)
        person_name = split_string[0]
        classes_coco_people.append(person_name)
   