import requests
import pandas as pd
import os.path
import time
import threading
import pynput
from pynput.keyboard import	Key, Listener
import warnings
warnings.filterwarnings('ignore')


#image upload function
def get_new_url():
	response = requests.get("https://randomfox.ca/floof")
	print(response.status_code)
	fox_image_url = response.json()['image']
	print(fox_image_url)
	return fox_image_url
#image upload function
def get_new_image(fox_image_url):
	file_path = "images/" + fox_image_url[28:] #images/something.jpg
	with open(file_path,"wb") as f:
		img = requests.get(fox_image_url)
		f.write(img.content)
		print(fox_image_url[28:],"downloaded!")
	return file_path

def get_index(file_name,data_list):
	for i in range(len(data_list)):
		if(file_name==data_list[i]):
			return i
#general func
def data_update():
	if(os.path.exists("data.csv")):#if the file has already been created, then changes are made to it
		data = pd.read_csv('data.csv')
		new_url = get_new_url()
		if(os.path.exists(new_url[21:])):#checks for the existence of a file to avoid duplicate files
			data["duplicates"][get_index(new_url[21:], data["images path"].values.tolist())] += 1 #increments 1 to the duplicate column if such file already exists
		else:
			file_path = get_new_image(new_url)
			data = pd.concat([data, pd.DataFrame({"id":[int(file_path.replace("images/","").replace(".jpg",""))],"images path":[file_path],"duplicates":[0]})],ignore_index = True,axis = 0)
		data.to_csv("data.csv",index = False)
		print("file \"data.csv\" was updated!")
	else:#creates the file if it doesn't exist, this is possible if the program is launched for the first time
		file_path = get_new_image(get_new_url())
		data = pd.DataFrame({"id":[int(file_path.replace("images/","").replace(".jpg",""))],"images path":[file_path],"duplicates":[0]})
		data.to_csv("data.csv",index = False)
		print("file \"data.csv\" created!")

def Timer(t = 15):
	while t+1:
		minutes = t // 60
		seconds = t % 60
		timer = '{:02d}:{:02d}'.format(minutes,seconds)
		print(timer,end="\r")
		t-=1
		time.sleep(1)
		while start_stop_event.is_set():
			time.sleep(1)
		if(exit_event.is_set()):
			break

def thread1():
	while exit_event.is_set()==False:
		print("'s' - start/stop timer , esc - exit")
		Timer()
		print("     ",end="\r")
		if(exit_event.is_set()==False):
			data_update()
		print("-"*15,"\n")
	print("thread1 is stopped")

def on_press(key):
	if type(key) == pynput.keyboard._win32.KeyCode:
		if key.char == 's':
			if(start_stop_event.is_set()==False):
				start_stop_event.set()
			else:
				start_stop_event.clear()



def on_release(key):
	if key == Key.esc:
		exit_event.set()
		start_stop_event.clear()
		return False

start_stop_event = threading.Event()
exit_event = threading.Event()
thrd1 = threading.Thread(target=thread1)
thrd1.start()
with Listener(on_press = on_press,on_release = on_release) as listener:
	listener.join()


