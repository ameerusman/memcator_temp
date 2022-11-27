import sys
import os
import json
import csv
import time
import pandas as pd
import flow_control
from settings import *


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

INITIAL_MEMORY_RUN = 0

try:
    image_path = sys.argv[1]
    print(sys.argv[1])
except:
    # image_path = '~' # Using this gave an error
    image_path = os.path.expanduser("~")



# gets the paths of all image files in the image directory by the specified image file types.
def get_image_file_paths():
    print("Scan Started.")
    image_file_paths = []
    for root, dirs, files in os.walk(image_path):
        for file in files:
            if file.endswith(image_file_types):
                image_file_paths.append(os.path.join(root, file))
    print("Scan completed.")
    return image_file_paths

# creates a new json file or updates the exisiting file with json data.
def create_or_update_json_file_with_data(path,obj_list):
    try:
        with open(path+'\\'+database_name+'.json','a') as json_file:
            json.dump(obj_list,json_file)
    except:
        print("An error occured while writting JSON")

# creates a new csv file or updates the exisiting file with csv data.
def create_or_update_csv_file_with_data(path,obj_list):
    try:
        with open(path+'\\'+database_name+'.csv','a') as csv_file:
            csv_writter = csv.DictWriter(csv_file, fieldnames= obj_list[0].keys(), lineterminator='\n')
            csv_writter.writeheader()
            for data in obj_list:
                csv_writter.writerow(data)
    except:
        print("An error occured while writting CSV")

def create_or_update_file_with_data(path,obj_list):
    print("Creating Database.")
    create_or_update_csv_file_with_data(path,obj_list)
    create_or_update_json_file_with_data(path,obj_list)
    print("Database created.")

def delete_entry_in_file(database_path_file, file_with_path):
    start_time = time.time()

    df = pd.read_csv(database_path_file+'\\'+database_name+'.csv')
    index_to_drop = df.index[(df['path'] == file_with_path)]
    df.drop(index_to_drop, axis=0, inplace=True)
    df.to_csv(database_path_file+'\\'+database_name+'.csv',index=False)

    duration = time.time() - start_time
    print(duration)



# event handler class for handling directory change events
class DirectoryObserver(FileSystemEventHandler):
    
    def on_created(self, event):
        for image_file_type in image_file_types:
            if image_file_type in (event.src_path):
                print("File created")
                print(event.src_path, event.event_type)
                json_data = prepare_json_data_single(event.src_path)
                create_or_update_file_with_data(database_path, json_data)
        return 
   
    def on_modified(self, event):
        for image_file_type in image_file_types:
            if image_file_type in (event.src_path):
                print("File modified")
                print(event.src_path, event.event_type)       
        return

    def on_deleted(self, event):
        for image_file_type in image_file_types:
            if image_file_type in (event.src_path):
                print("File deleted")
                print(event.src_path, event.event_type)
                delete_entry_in_file(database_path, event.src_path)   
        return


def start_observer():
    event_handler=DirectoryObserver()
    observer = Observer()
    observer.schedule(event_handler, path=image_path, recursive=True)
    print("Monitoring started")
    observer.start()
    try:
        while True:
            time.sleep(1) # TODO: Is this needed?
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
def prepare_json_data_multiple(file_paths):

    json_data = []
    for path in file_paths:
        json_obj = {}
        json_obj["path"] = path
        json_obj["objects"] = to_be_checked_string
        json_data.append(json_obj)
    return json_data

def prepare_json_data_single(file_path):

    json_data = []
    json_obj = {}
    json_obj["path"] = file_path
    json_obj["objects"] = to_be_checked_string # This means to be checked
    json_data.append(json_obj)

    return json_data

def create_json_with_pandas(database_path,json_data):
    df = pd.DataFrame.from_dict(json_data)
    df.to_csv(database_path+"\\"+"filetest.csv",index=True)

def main():
    file_paths = get_image_file_paths()
    json_data = prepare_json_data_multiple(file_paths)
    create_or_update_file_with_data(database_path,json_data)
    create_json_with_pandas(database_path,json_data)

    start_observer()

   
if __name__ == "__main__":
    main()