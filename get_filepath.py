'''
SY: WORK-IN-PROGRESS
TESTING OUT WITH COLOR GRADIENT PNG
'''

import chunk
from hashlib import new
import sys
import os
from this import d
from PIL import Image, ImageMath
import numpy as np


import tkinter as tk
from tkinter import filedialog

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def encode(imgpath, secret_binary):
	# jpg trailer (END) => FF D9
	img = Image.open(imgpath)
	img.load()
	newimg = img.copy() 	#(SY: Using a copy of the original image to manupilate)
	img_array = np.asarray(newimg, dtype='int32')
	#print(img_array.shape)	 # MATRIX => (256, 256, 3) | 256 rows | 256 cols | 3 ?(RGB)
	#print(img_array.min())  # => 0
	#print(img_array.max())  # => 255
	#print(img_array[0][1])  # => [255,0,0] FIRST Pixel
	# get first pixel rgb try to find & tally in hxd

	datalist = [int(x) for x in secret_binary] #append all secret binary into a list
	datalist = list(chunks(datalist, 8))
	datalen = len(datalist)
	pix = newimg.getdata()
	imgdata = iter(pix)
	newdata_pixels = []
	
	#Since one letter = 8 bit, we would need at least 3 pixels to encode one letter, the last pixcel will determine if it is EOF 
	#Lets make value odd if 1 and even if 0
	for i in range(datalen):
		pix = [value for value in imgdata.__next__()[:3] +
									imgdata.__next__()[:3] +
									imgdata.__next__()[:3]]
		
		for j in range(0, 8):
			if(datalist[i][j] == 0 and pix[j] % 2 != 0):
				pix[j] -= 1
			
			elif(datalist[i][j] == 1 and pix[j] % 2 == 0):
				if(pix[j] != 0):
					pix[j] -= 1
				else:
					pix[j] += 1
	
		if(i == datalen - 1):
			if(pix[-1] % 2 == 0):
				if(pix[-1] != 0):
					pix[-1] -= 1
				else:
					pix[-1] += 1

		else:
			if(pix[-1] % 2 != 0):
				pix[-1] -= 1

		pix = tuple(pix)
		newdata_pixels.append(pix[0:3])
		newdata_pixels.append(pix[3:6])
		newdata_pixels.append(pix[6:9])
	
	# print(len(newdata_pixels) == datalen * 3)
	newimg = cons_newimg(newimg, newdata_pixels)
	newimg.save("Stego_colour_img.png", "PNG")

def cons_newimg(new_img, newdata_pixels):
	w = new_img.size[0]
	(x,y) = (0,0)

	for pixel in newdata_pixels:
		new_img.putpixel((x,y), pixel) #Insert new pixcel starting from top left
		if(x == w-1): # When reached the end of first row of pixel
			x = 0
			y += 1

		else:
			x += 1

	return new_img

def manipulate_secret(secret_string):
	secret_binary = ''.join(format(each_char, '08b') for each_char in bytearray(secret_string, 'ascii'))
	print(secret_binary)
	return secret_binary

def get_file_path():
	root = tk.Tk()
	root.withdraw()
	
	# Prompt user to select file -> Returns a Tuple
	filepath_Tuple = filedialog.askopenfilenames()

	if len(filepath_Tuple) == 0:
		print("[*] No file selected.")
	else:
		filepath = filepath_Tuple[0]
		print("[*] User selected path: " + filepath)
		file_ext = filepath.split(".")[-1]
		print("[*] Input File Extension is: " + file_ext)

	list_of_accepted_ext = [
		'jpg',
		'png',
		'txt',
		'mp3',
		'mp4'
	]

	if file_ext in list_of_accepted_ext:
		print("[*] This is an accepted file extension: " + file_ext)
		return filepath
	else:
		print("[*] This file extension '{}' is not allowed!".format(file_ext))
		sys.exit(0)


def decode(imgpath):
	img = Image.open(imgpath)
	img.load()
	payload = ''
	imgdata = iter(img.getdata())
	# print(list(img.getdata())[0])
	while(1):
		pix = [value for value in imgdata.__next__()[:3] +
							imgdata.__next__()[:3] +
							imgdata.__next__()[:3]]

		binary_str = ''

		for i in pix[:8]:
			if(i % 2 == 0):
				binary_str += '0'
			else:
				binary_str += '1'
		
		payload += chr(int(binary_str, 2))

		if(pix[-1] % 2 != 0):
			return payload


def main():
	# UI PRESS -> 'Choose a File' -> activates get_file_path
	# imgpath = get_file_path()
	
	# hardcoded imgpath for now
	imgpath = ".\stock\italy_medium_edited.jpg"
	decode_imgpath = ".\Stego_colour_img.png"
	secret_string = 'team 10 will get an A+'

	secret_binary = manipulate_secret(secret_string)
	encode(imgpath, secret_binary)
	# payload = decode(decode_imgpath)
	# print(payload)

	sys.exit(0)


if __name__ == "__main__":
	main()