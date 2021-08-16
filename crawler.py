import numpy as np
import re
import sys
import datetime
import requests
from bs4 import BeautifulSoup

from nonogram_solver import GameBoard, Clue
import nonogram_solver as solver

# needs to be speedy fast
solver.do_animation = False

if (len(sys.argv) != 3):
    print("usage: ", sys.argv[0], "<size_number> <email>")
    sys.exit()

page_size = 0
subpage = "/?size=" + str(page_size)
url = "https://www.puzzle-nonograms.com" + subpage

# first, we need to pull in the whole page.
session = requests.Session()
index_html = session.get(url)

#print(index_html.text)

# get the clue data out of the html
index_soup = BeautifulSoup(index_html.text, 'html.parser')

width = int(index_soup.find('input', { 'name' : 'w' })["value"])
height = int(index_soup.find('input', { 'name' : 'h' })["value"])

magic_param = index_soup.find('input', { 'name' : 'param' })["value"]

pattern = re.compile(r"var task = '(.*?)';", re.MULTILINE | re.DOTALL)
script = index_soup.find("script", text = pattern)

task_string = pattern.search(script.text).group(1);
task_string = task_string.split('/')
print(task_string)
clue_list = task_string[width :] + task_string[: width]
print(clue_list)
clue_list = [Clue(list(i.split('.')), width if index > width else height)
    for index, i in enumerate(clue_list)]


board = GameBoard((width, height), clue_list, False)
start_time = datetime.datetime.now()
if (board.attemptSolve()):
    end_time = datetime.datetime.now()
    time_delta = round((end_time - start_time).total_seconds() * 1000)
    time_string = str(round(time_delta / 60000)) + ":" + str(round(time_delta / 1000) % 60)
    form_data = { 
        'jstimer' : '0',
        'jsPersonalTimer' : '',
        'jstimerPersonal' : str(time_delta),
        'stopClock' : '0',
        'fromSolved' : '0',
        'robot' : '1',
        'zoomslider' : '1',
        'jstimerShow' : time_string,
        'jstimerShowPersonal' : time_string,
        'b' : '1',
        'size' : str(page_size),
        'param' : magic_param,
        'w' : str(width),
        'h' : str(height),
        'ansH' : ''.join(['y' if i == 2 else 'n' for i in board.boardState.flatten('C')]),
        'ready' : "+++Done+++",
    }
    response = session.post("https://www.puzzle-nonograms.com/", data = form_data)
    response_soup = BeautifulSoup(response.text, "html.parser")

    magic_param = response_soup.find('input', { 'name' : 'solparams' })
    if (magic_param is None):
        print("failed")
        sys.exit()

    magic_param = magic_param['value']
    
    print(session.post("https://www.puzzle-nonograms.com/hallsubmit.php", { 'submitscore' : '1',
        'solparams' : magic_param, 'robot' : '1', 'email' : 'connormc757@gmail.com' }).text)
