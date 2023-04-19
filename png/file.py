
from PIL import Image
import numpy as np


def creating_image(img_array, imgpath):
	print("[*] Creating new image with edited pixels...")
	data = Image.fromarray(img_array.astype(np.uint8)).convert('RGB')
	data.save(imgpath)

def create_txtfile(contents, txtfilepath):
	with open(txtfilepath, 'w') as f:
		f.write(contents)