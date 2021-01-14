# Scale AI Automated Checks
### The purpose of this project is to run automated checks every once in a while against a list of tasks that have been submitted to the platform.

## Setup
As of this current version replace the key word 'BASIC_TOKEN' on line 11
of scale.py. A future version will use a token file that will be hidden
with .gitignore.

The input for this project is a task list, you can find the list on [task_list.csv](https://github.com/czpta/scale-auto-check/blob/master/task_list.csv). You can list the ID of tasks you'd like to check against there, and the program will fetch the tasks from Scale AI to perform its checks.

## Output
The end result are CSV files for each of the existing checks. Examples have been commited to the repo and are found in the output folder.

## Checks
These are the checks that currently exist today:
1. Check 1 will calculate each of the bounding boxes in each of the tasks as well as the size of the image the task is assinged to and check if each of the boxes are greater than 80 percent of the size of the image size. The point here is to ensure a tasker is not mistakingly submitting a task with one big box overlapping the entire image. It's better to safely target this as the likelihood of the relevance of the box is low if it overtakes the entire image.

2. Check 2 will ensure signs do not overlap each other by 80 percent or more. The idea here is that if two boxes are on top of each other than it is likely that one of them doesn't have enough information to be relevant to the viewer at the time the image was taken. Another idea would be to avoid accidental duplicates of what is supposed to be one singular box.