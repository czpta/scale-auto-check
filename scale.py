# import scaleapi # not in use
import requests
import urllib.request
# import click # not in use 
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
    else:
      added_row = pandas.Series({'task_id': task_json['task_id'],
                        'uuid': box_size['uuid'],
                        'violation': 'Success',
                        'description': 'The task has passed check 1'}, index=output.columns)
      output = output.append(added_row, ignore_index=True)    
  
  return(output)


# Calculates the percentage of how much two boxes overlap each other
def overlapping_percentage(box1, box2):
  # Find coords for both boxes
  x1 = max(box1['left'], box2['left'])
  y1 = max(box1['left'], box2['top'])
  x2 = min(box1['left']+box1['width'], box2['left']+box2['width'])
  y2 = min(box1['top']+box1['height'], box2['top']+box2['height'])

  # Calculate the area where the boxes cross each other
  cross_section = (x2 - x1 + 1) * (y2 - y1 + 1)

  # Calculate the area of both boxes
  box1_area = (box1['width'] + 1) * (box1['height'] + 1)
  box2_area = (box2['width'] + 1) * (box2['height'] + 1)

  # Calculate percentage by dividing cross_section by sum of
  # both areas minus the cross_section
  percentage = cross_section / float(box1_area + box2_area - cross_section)

  return(percentage)


# Determines if two boxes overlap
def overlapping_checker(box1, box2):
  return not (
        ((box1['top'] + box1['height']) < (box2['top'])) or
        (box1['top'] > (box2['top'] + box2['height'])) or
        ((box1['left'] + box1['width']) < box2['left']) or
        (box1['left'] > (box1['left'] + box2['width']))
    )

# Check 2: Signs don't overlap by 80% or more
def check_2(task_json, output):
  overlapping_box_list = []

  # Generate list of boxes that overlap each other
  for i, current_box in enumerate(task_json['response']['annotations']):
    previous_box = task_json['response']['annotations'][i-1] if i > 0 else None
    if previous_box is not None:
      if overlapping_checker(previous_box, current_box) == True:
        overlapping_box_list.append(current_box)
  
  # Get the percentage of how much the boxes overlap
  for i, current_box in enumerate(overlapping_box_list):
    previous_box = overlapping_box_list[i-1] if i > 0 else None
    if previous_box is not None:
      # if box overlapping percentage > .8, log it
      if overlapping_percentage(previous_box, current_box) > .8:
        percentage_string = "{:.0%}".format(overlapping_percentage(previous_box, current_box))
        description_string = 'Box is overlapping box ' + previous_box['uuid'] + ' by ' + percentage_string
        added_row = pandas.Series({'task_id': task_json['task_id'],
                        'uuid': current_box['uuid'],
                        'violation': 'Check 2',
                        'description': description_string}, index=output.columns)
        output = output.append(added_row, ignore_index=True)
  
  return(output)


# Goes through given list of tasks and goes about retrieving them
def submit_task_list(task_list):
  # Grab list from csv
  csv = pandas.read_csv(task_list, sep=",", index_col=None)

  output = pandas.DataFrame({'task_id': [],
                        'uuid': [],
                        'violation': [],
                        'description': []})

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
    check_2_rows = check_2(task, output)

  check_1_rows.to_csv('output/check1.csv')
  loguru.success("Output Check 1 to output/check1.csv")
  check_2_rows.to_csv('output/check2.csv')
  loguru.success("Output Check 2 to output/check2.csv")


# Main function
submit_task_list('task_list.csv')