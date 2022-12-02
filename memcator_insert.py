#Memcator


import os
import time
import cv2
import sys
import logging
import warnings
import logging
from deepface import DeepFace
from retinaface import RetinaFace
import json

import flow_control
from settings import *



def check_file_extension():
    file_type_valid = False
    try:
        if (sys.argv[1]):
            split_tup = os.path.splitext(sys.argv[1])
            # print(split_tup)
            for image_file_type in image_file_types:
                
                if (split_tup[1] == image_file_type):
                    file_type_valid = True
                    # print("Got true")
                    return True
                    break
            if (file_type_valid == False):
                # print("File type not valid.")
                return False
                quit()    
                sys.exit("Values do not match")       

    except:
        input_image = "test_images/friends1.jpg"

    assert os.path.exists(input_image)

    return False

# =============


def get_detected_face (face):

    fd = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    # face_img = face.copy()
    face_img = cv2.imread(face, 0)
    fr = fd.detectMultiScale(face_img)
    for (x,y,width,height) in fr:
        cv2.rectangle(face_img, (x,y), (x + width, y+height), (255,255,77), 10)  
    croppedFace = face_img[x:x+width,y:y+height]
    return croppedFace


def memcator_init(path , model_name):
    from imageai.Detection import ObjectDetection

    flow_control.log("Memcator")
    t1 = time.time()
    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath( os.path.join(path , model_name ))
    detector.loadModel()
    t2 = time.time()
    string = "Time to load model: " + str(t2-t1) + " seconds"
    flow_control.log(string)
    return detector
    
def memcator_general_detect(path, general_model , input_image , output_image):
    t1 = time.time()
    detections = general_model.detectObjectsFromImage(input_image=os.path.join(path , input_image), output_image_path=os.path.join(path , output_image))
    t2 = time.time()
    string = "Time to perform general detections: " + str(t2-t1) + " seconds"
    flow_control.log(string)
    return detections


def convert_to_list(string):
    li = list(string.split())
    return li

def prepare_json_data_single(object,file_path,json_data):
    json_obj = {}
    
    json_obj["object"] = object # This means to be checked
    json_obj["file_path"] = []
    json_obj["file_path"].append(file_path)

    json_data.append(json_obj)
    return json_data


def update_json_data(objects,json_file_data,img_file_path):

    file_paths = []
    # file_names = []

    # file_name_to_add = os.path.basename(img_file_path)
    file_paths_to_add = img_file_path

    
    for object in objects:
        found_object = False
        json_data_index = 0

        if bool(json_file_data):
            for json_data in json_file_data:
                # print(json_data["object"])
                if json_data["object"] == object:
                    found_object = True
                    # file_names = json_file_data[json_data_index]["file_name"]
                    file_paths = json_file_data[json_data_index]["file_path"]

                    # This is done so that if a string is received, 
                    # it is changed to a list for consistent file types
                    # if type(file_names) is str: 
                    #     file_names = convert_to_list(file_names)
                    # file_names.append(file_name_to_add)

                    if type(file_paths) is str:
                        file_paths = convert_to_list(file_paths)
                    file_paths.append(file_paths_to_add)

                    # json_file_data[json_data_index]["file_name"] = file_names
                    json_file_data[json_data_index]["file_path"] = file_paths

                    # print(type(file_paths))
                    # print(json_file_data)
                    break
                json_data_index = json_data_index + 1

            if (found_object == False):
                    json_file_data = prepare_json_data_single(object,img_file_path,json_file_data)    
        else:
            json_file_data = []
            json_file_data = prepare_json_data_single(object,img_file_path,json_file_data)
            # print("Printing json file=====")
            # print(type(json_file_data))
            # print(json_file_data)
    return json_file_data

def read_json(file_path):
    try:
        with open(file_path) as f:
            data = json.load(f)
        return data

    except:
        # print("File not found.")
        json_obj = {}
    return json_obj

def read_json_with_check(file_path):
    try:
        with open(file_path) as f:
            data = json.load(f)
        return data

    except:
        # print("File not found.")
        return False


def create_or_update_json_file_with_data(path,obj_list):
    try:
        with open(database_file_path,'w') as json_file:
            json.dump(obj_list,json_file,indent=4)
            # print("Saving the file.")
    except:
        print("An error occured while writting the Database.")
        
def update_database_with_objects(img_file_path, object_list): # TODO:   

    if (DATABASE_FORMAT == DatabaseFormat.JSON):
        json_file_data = read_json(database_file_path)
        json_updated_data = update_json_data(object_list,json_file_data,img_file_path)

        # file_name = os.path.basename(img_file_path)
        create_or_update_json_file_with_data(path=database_file_path, obj_list=json_updated_data)

def memcator_process_detections(detection_results,image_path):
    objects_found = set()
    for eachObject in detection_results:
        if(int(eachObject["percentage_probability"]) > DETECTION_PROBABILITY):
            objects_found.add(eachObject["name"] )

    return objects_found

def memcator_facial_detect(image_path, objects_set):
    # print("Inside memcator_facial")
    # Separating faces one by one
    
    
    t1 = time.time()
    faces = RetinaFace.extract_faces(img_path = image_path, align = True)
    t2 = time.time()
    string = "Time to extract faces: " + str(t2-t1) + " seconds"
    flow_control.log(string)
    
    # print(type(faces))
    # print(faces)
    face_counter = 0

    for face in faces:
        # print("Faces Found" + str(face_counter))
        face_counter = face_counter + 1
        # cv2.imwrite("face_"+str(face_counter)+".jpg",face)
        for root, dirs, files in os.walk(knwn_ppl_imgs_path):
            for file in files:
                if file.endswith(image_file_types):
                    t1 = time.time()
                    detection_result = DeepFace.verify(img1_path = os.path.join(root, file), 
                    img2_path = face, model_name = model,  
                    distance_metric = metric, enforce_detection=False)
                    t2 = time.time()
                    string = "Time to recognize a face: " + str(t2-t1) + " seconds"
                    flow_control.log(string)

                # print(detection_result)

                if (detection_result["verified"] == True):
                    # split_string = file.split('.')
                    split_string = os.path.splitext(file)
                    person_name = split_string[0]
                    # print("Found person: "+person_name+" in file face: "+file)
                    objects_set.add(person_name)
                
                elif (detection_result["verified"] == False ):
                    pass
                    # print("Person not found in file face: "+ file)
                    

    return objects_set

def find_duplicate_in_db(database_file,image_path_to_check):
    json_file_data = read_json_with_check(database_file)
    if(json_file_data != False):
        if(bool(json_file_data)):
            # print("HERE")
            # print(json_file_data)
            for json_data in json_file_data:
                # print("HERE")
                for json_file_paths in json_data["file_path"]:
                    # print("HERE3")
                    # print(json_file_paths)
                    if (json_file_paths == image_path_to_check):
                        # print("File found in the DB")
                        return True
    
    else:
        return "Not inside the Database."
    # print("File NOT found in the Database.")
    return False
    
    


# =========== Main Function Starts Here ============
def main():
    if (check_file_extension() == False):
        quit()
    personCounter = 0

    if (JUPYTER_NB == 1):
        #input_image = "/home/ubuntu/ameer/photo_index/content-based-photograph-indexing/a1.jpg"
        input_image = "a1.jpg"

    else:
        try:
            if (sys.argv[1]):
                input_image = sys.argv[1]
        except:
            input_image = "test_images/friends1.jpg"

    assert os.path.exists(input_image)


    output_image = "./output_"+str(input_image)+".jpg"
    #output_image = "output_images/"+str(input_image)+"_output.jpg"

    # flow_control.log(input_image)

    # DONE: memcator_init -> loads the detector
    # Done: memcator_general_detect: Takes file name and returns output (list of objects)
    # Done: Creating datasets from the list of objects.
    # TODO: Make a function.

    # execution_path = os.getcwd() # Removed
    execution_path = model_path
    input_image = os.path.abspath(input_image)

    general_model = memcator_init(execution_path , model_name)

    
    files_count = len(sys.argv)
    file_counter = 1
    while(file_counter <= files_count):
        
        input_image = os.path.abspath(sys.argv[file_counter])
        file_counter = file_counter + 1
        if (find_duplicate_in_db(database_file_path,input_image) != True):
            print("Analyzing file: "+ input_image)
            detections = memcator_general_detect(execution_path, general_model , input_image , output_image)
            
            
            objects_set = memcator_process_detections(detections,input_image)

            if(person_string in objects_set): # If a person is found inside the image
                objects_set = memcator_facial_detect(input_image, objects_set)

            # Only proceed forward if there are any objects found
            if(bool(objects_set)):
                update_database_with_objects(input_image, objects_set)

            else:
                # print("Found no objects.")
                pass
        else:
            # print("File already scanned.")
            pass

       


# ============= Calling the main function ==========
if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    logging.getLogger("tensorflow").setLevel(logging.ERROR)
    main()