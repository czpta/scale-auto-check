import scaleapi
import requests
import urllib.request
import click
import pandas
import json
from loguru import logger

# Project setup
client = scaleapi.ScaleClient('API_TOKEN')
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



# Goes through given list of tasks and goes about retrieving them
def submit_task_list(task_list):
  # Grab list from csv
  csv = pandas.read_csv(task_list, sep=",", index_col=None)
  # Go through list in loop
  for task_id in csv.iterrows():
    # call task_getter on each task
    task_file_name = 'tasks/' + task_id[1][0] + '.json'
    with open(task_file_name, 'w') as outfile:
      json.dump(task_getter(task_id[1][0]), outfile)
    # get image per each task
    retrieve_images(task_getter(task_id[1][0]), task_id[1][0])


# Check 1: Task has a bounding box that takes up the
# entire image (bounding box size > x percent of the image size)
def check_1(task_json):
  # Get image and check out its size
  # See if box width equal to or greater than 80% of image width
  # See if box height equal to or greater than 80% of image height
  print("1")


# Check 2: Signs don't overlap by 80% or more
def check_2(task_json):
  # Get x2, x1 calculation to see where box is horizontally
  # Get y1, y2 calculation to see where box is vertically 
  # Do math to get list of overlapping boxes
  # For each overlapping box, calculate percentage of overlap
  print("2")


# Check 3: Greater than 4 signs in one small area
def check_3(task_json):
  # Get list of all supersmall boxes
  # Find the ones within 6 pixels distance from each other
  # If one of the boxes has more than 4 related boxes to it,
  # then there are too many boxes in one small area
  print("3")


# Main function
submit_task_list('task_list.csv')