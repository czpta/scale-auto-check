import scaleapi
import requests
import urllib.request
import click
import pandas
import json
from PIL import Image
from loguru import logger

# Project setup
headers = {"Authorization": "Basic BASIC_TOKEN"}


# task_getter retrives one task when given an id.
def task_getter(task_id):
  # task_id is of type string, example = '5f127f6c3a6b1000172320ad'
  base_url = "https://api.scale.com/v1/task/"
  url = base_url + task_id
  response = requests.request("GET", url, headers=headers)
  return (response.json())


# When given a task JSON, return the corresponding image
def retrieve_images(f, task_id):
  # Retrieve the URL 
  image_url = f['params']['attachment']
  file_name = 'tasks/' + task_id + '.jpg'
  # Store image
  urllib.request.urlretrieve(image_url, file_name)
  return(file_name)


# Check 1: Task has a bounding box that takes up the
# entire image (bounding box size > x percent of the image size)
def check_1(task_json, image_file, output):
  # Get image and check out its size
  image_size = image_file.size
  image_width = image_size[0]
  image_height = image_size[1]
  # Create output format
  rows_list = []
  # Get box width + height
  for box_size in task_json['response']['annotations']:
    width_percentage = 1
    height_percentage = 1
    # See if box width equal to or greater than 80% of image width
    box_width = box_size['width']
    width_percentage = 100 * float(box_width) / float(image_width)
    # See if box height equal to or greater than 80% of image height
    box_height = box_size['height']
    height_percentage = 100 * float(box_height) / float(image_height)

    if width_percentage > 80 or height_percentage > 80:
      added_row = pandas.Series({'task_id': task_json['task_id'],
                        'uuid': box_size['uuid'],
                        'violation': 'Check 1',
                        'description': 'Task has a bounding box that takes up the entire image'}, index=output.columns)
      output = output.append(added_row, ignore_index=True)
    
    if task_json['task_id'] not in output['task_id']:
      added_row = pandas.Series({'task_id': task_json['task_id'],
                        'uuid': box_size['uuid'],
                        'violation': 'Success',
                        'description': 'The task has passed check 1'}, index=output.columns)
      output = output.append(added_row, ignore_index=True)    
  
  # output.append(output_append, ignore_index=True)
  return(output)


# Check 2: Signs don't overlap by 80% or more
def check_2(task_json, image_file):
  # Get x2, x1 calculation to see where box is horizontally
  # Get y1, y2 calculation to see where box is vertically 
  # Do math to get list of overlapping boxes
  # For each overlapping box, calculate percentage of overlap
  print("2")


# Check 3: Greater than 4 signs in one small area
def check_3(task_json, image_file):
  # Get list of all supersmall boxes
  # Find the ones within 6 pixels distance from each other
  # If one of the boxes has more than 4 related boxes to it,
  # then there are too many boxes in one small area
  print("3")


# Goes through given list of tasks and goes about retrieving them
def submit_task_list(task_list):
  # Grab list from csv
  csv = pandas.read_csv(task_list, sep=",", index_col=None)

  output = pandas.DataFrame({'task_id': [],
                        'uuid': [],
                        'violation': [],
                        'description': []})
  final_rows = []
  # rows_list = ['task_id', 'uuid', 'violation', 'description']

  # Go through list in loop
  for task_id in csv.iterrows():
    # call task_getter on each task
    task_file_name = 'tasks/' + task_id[1][0] + '.json'
    task = task_getter(task_id[1][0])
    with open(task_file_name, 'w') as outfile:
      json.dump(task, outfile)
    # get image per each task
    retrieved_image = retrieve_images(task, task_id[1][0])
    opened_image = Image.open(retrieved_image)
    # Perform checks on the image + task object for a given task
    check_1_rows = check_1(task, opened_image, output)
    final_rows.append(check_1_rows)
    check_2(task, opened_image)
    check_3(task, opened_image)

    output = check_1_rows
  # output.columns = ['task_id', 'uuid', 'violation', 'description']
  output.to_csv('output/check1.csv')


# Main function
submit_task_list('task_list.csv')