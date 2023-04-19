'''
DEPENDENCY:
- pillow
- numpy

JADEN: WORK-IN-PROGRESS
- Pixel edits works with PNG

- Metadata (flags)
	- How many LSB used
	- Num of pixels that holds the secret size
	- Secret Size bits

- TAKE INTO ACCOUNT MAX & MIN, limits of array	[1][255] or [0][258]
'''

from Better_Video import header				# import header.py file
from Better_Video import file					# import file.py file
from Better_Video import body					# import body.py
from Better_Video import decode


# import header				# import header.py file
# import file					# import file.py file
# import body					# import body.py
# import decode

import sys
import math

from PIL import Image
import numpy as np


DELIMITER = '|#2004#|'

def program_termination(flag):
	if  flag == 0:
		print("[*] Encoding Successful! Image encoded.")
	elif flag == 1:
		print("[!] ENCODING ERROR!!! Secret is too big for the file!")
	elif flag == 2:
		print("[!] ENCODING ERROR!!! Mismatch of remainder bits!")
	elif flag == 100:
		print("[!] ENCODING ERROR!!! Not enough pixel columns to write data! ")
	return flag



def valid_secret(total_color_bits, filesize_bits, num_secret_bits, lsb_bit_selected):

	num_of_lsb = lsb_bit_selected + 1							# for e.g 2 LSB Selected is (0,1,2 == 3) hence +1

	updated_total_bits = total_color_bits - 24					# Full 24 bits taken for first pixel despite only using 3 bits (R0,G0,B0)
	
	reserved_filesize_bits = math.ceil(filesize_bits / num_of_lsb) * 8
	print("[*] Full bits reserved to represent filesize: ", reserved_filesize_bits)

	updated_total_bits -= reserved_filesize_bits
	print("[*] Remaining bits for secret: ", updated_total_bits)		# 1,572,784 bits

	max_bits_for_secret = int(updated_total_bits * (num_of_lsb / 8))	# 589,794 bits (Mutiplied by usable bits)
	print("[*] Max bits for secret allowed ({} LSBs used - 'LSB[{}] to LSB[0]'): {}".format(num_of_lsb, lsb_bit_selected, max_bits_for_secret))

	if (num_secret_bits > max_bits_for_secret):
		program_termination(1)
	else:
		print("[*] Secret is encodable within the file! (Secret Size < File Size)")


def get_total_bits(img_array):
	'''
	MATRIX => (H, W, D) == (256, 256, 3) | 256 rows | 256 cols | 3? 
	MIN => 0 
	MAX => 255

	TAKE INTO ACCOUNT HEADER FIELDS WHILE CALCULATING MAX
	'''
	height_pixels = img_array.shape[0]						# int values e.g 256 or 1280
	width_pixels = img_array.shape[1]						# int values e.g 256 or 1920

	total_pixels = height_pixels * width_pixels				# 65,536 pixels
	total_colors = total_pixels * 3 						# 196,608 colors (Multiply with R,G,B)
	
	total_color_bits = total_colors * 8						# 1,572,864 total bits (Each Color has 8 bits)
	print("[*] Total RGB bits in file: ", total_color_bits)

	'''
	Either, used to store the secret length during the encoding process
	Or, used to read the secret length during the decoding process
	'''
	filesize_bits = math.ceil(math.log2(total_color_bits))
	print("[*] Filesize Bits: ", filesize_bits)

	return total_color_bits, filesize_bits, height_pixels, width_pixels

	
	
def get_img(imgpath):
	img = Image.open(imgpath)
	img.load()
	original_img_array = np.asarray(img, dtype='uint8')
	img_array = original_img_array.copy()

	return img_array


def convert_to_binary(secret_string):
	secret_binary = ''.join(format(each_char, '08b') for each_char in bytearray(secret_string, 'utf-8'))
	return secret_binary


def get_string_from_txtfile(txtfilepath):
	with open(txtfilepath) as f:
		data = f.read()
	return data



def encodeMain(img, input_secret, isTextBox, isBase64, lsb_bit_selected):

	''' (1) COVER IMAGE '''
	imgpath = "./source/" + img	# duplicated copy in source to manipulate
	imgname = img.split(".")[0]
	print("[*] Filename without extension: ", imgname)	# for e.g taylor, italy_medium ....
	

	''' (2) SECRET STRING FROM TEXT BOX [OR] TEXT FILE '''
	# FROM TXTBOX
	# secret_string = r"Anne Frank's The Diary of a \==:;Young Girl is among the most enduring documents of the twentieth century. Since its publication in 1947, it has been read by tens of millions of people all over the world. It remains a beloved and deeply admired testament to the indestructable nature of the human spirit. Restore in this Definitive Edition are diary entries that had been omitted from the original edition. These passages, which constitute 30 percent more material, reinforce the fact that Anne was first and foremost a teenage girl, not a remote and flawless symbol. She fretted about, and tried to copie with, her own emerging sexuality. Like many young girls, she often found herself in disagreement with her mother. And like any teenager, she veered between the carefree nature of a child and the full-fledged sorrow of an adult. Anne emerges more human, more vulnerable, and more vital than ever. Anne Frank and her family, fleeing the horrors of Nazi occupation, hid in the back of an Amsterdam warehouse for two years. She was thirteen when the family went into the Secret Annex, and in these pages she grows to be a young woman and a wise observer of human nature as well. With unusual insight, she reveals the relations between eight people living under extraordinary conditions, facing hunger, the ever-present threat of discovery and death, complete estrangement from the outside world, and above all, the boredom, the petty misunderstandings, and the frustrations of living under such unbearable strain, in such confined quarters. A timely story rediscovered by each new generation, The Diary of a Young Girl stands without peer. For both young readers and adults it continues to bring to life this young woman, who for a time survived the worst horror of the modern world had seen — and who remained triumphantly and heartbreakingly human throughout her ordeal. For those who know and love Anne Frank, The Definitive Edition is a chance to discover her anew. For readers who have not yet encountered her, this is the edition to cherish. Anne Frank kept a diary from June 12, 1942, to August 1, 1944. Initially, she wrote it strictly for herself. Then, one day in 1944, Gerrit Bolkestein, a member of the Dutch government in exile, announced in a radio broadcast from Fondon that after the war he hoped to collect eyewitness accounts of the suffering of the Dutch people under the German occupation, which could be made available to the public. As an example, he specifically mentioned letters and diaries. Impressed by this speech, Anne Frank decided that when the war was over she would publish a book based on her diary. She began rewriting and editing her diary, improving on the text, omitting passages she didn't think were interesting enough and adding others from memory. At the same time, she kept up her original diary. In the scholarly work The Diary of Anne Frank: The Critical Edition (1989), Anne's first, unedited diary is referred to as version a, to distinguish it from her second, edited diary, which is known as version b. The last entry in Anne's diary is dated August 1, 1944. On August 4, 1944, the eight people hiding in the Secret Annex were arrested. Miep Gies and Bep Voskuijl, the two secretaries working in the building, found Anne's diaries strewn allover the floor. ,Miep Gies tucked them away in a desk drawer for safekeeping. After the war, when it became clear that Anne was dead, she gave the diaries, unread, to Anne's father, Otto Frank. After long deliberation, Otto Frank decided to fulfill his daughter's wish and publish her diary. He selected material from versions a and b, editing them into a shorter version later referred to as version c. Readers all over the world know this as The Diary of a fauna Girl. 'Paper has more patience than people.' I thought of this saying on one of those days when I was feeling a little depressed and was sitting at home with my chin in my hands, bored and listless, wondering whether to stay in or go out. I finally stayed where I was, brooding. Yes, paper does have more patience, and since I'm not planning to let anyone else read this stiff-backed notebook grandly referred to as a 'diary,' unless I should ever find a real friend, it probably won't make a bit of difference."
	# secret_string = "taylor swift album folklore is amazing"
	# secret_string = 'team 10 will get an A+'
	# secret_string = 'the secret krabby patty formula is...'
	# secret_string = r"IT will be seen that this mere painstaking burrower and grub -worm of a poor devil of a Sub -Sub appears to have gone through the long Vaticans and street-stalls of the earth, pick- ing up whatever random allusions to whales he could anyways find in any book whatsoever, sacred or profane. Therefore you must not, in every case at least, take the higgledy-piggledy whale statements, however authentic, in these extracts, for veritable gospel cetology. Far from it. As touching the ancient authors generally, as well as the poets here appearing, these extracts are solely valuable or entertaining, as affording a glancing bird's-eye view of what has been promiscuously said, thought, fancied, and sung of Leviathan, by many nations and generations, including our own. So fare thee well, poor devil of a Sub-Sub, whose commen- tator I am. Thou belongest to that hopeless, sallow tribe which no wine of this world will ever warm ; and for whom even Pale Sherry would be too rosy-strong ; but with whom one sometimes loves to sit, and feel poor-devilish, too ; and grow convivial upon tears ; and say to them bluntly with full eyes and empty glasses, and in not altogether unpleasant sadness Give it up, Sub-Subs ! For by how much the more pains ye take to please the world, by so much the more shall ye forever go thankless ! Would that I could clear out Hampton Court and the Tuileries for ye ! But gulp down your tears and hie aloft to the royal-mast with your hearts ; for your friends who have gone before are clearing out the seven-storied heavens, and making refugees of long-pampered Gabriel, Michael, and Raphael, against your coming. Here ye strike but splintered hearts together there, ye shall strike unsplinterable glasses!"
	# FROM FILE (BASE64)
	# secret_string = r"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkAAAAOECAYAAAD5Tf2iAAABb2lDQ1BpY2MAACiRdZFLS0JBGIYfrVDKKEgoosCFRYsCKYiWYZCbaqEGWW30eAu8HM5RQtoGbVoILaI23Rb9g9oGbQuCoAgiWvUDum1CTt+ooITNYc738M68HzPvgH0ho2XNdh9kcwUjGPB7ViKrHscbTobpxU1/VDP1xdB8mH/H9wM2Ve8nVK//97UcXfGEqYHNKTyt6UZBeFZ4YbOgK94VdmvpaFz4WHjckAMK3yg9VuNXxakafyo2wsE5sKuenlQTx5pYSxtZ4TFhbzZT1OrnUTdxJXLLIamDMocwCRLAj4cYRTbIUGBCak4ya+3zVX1L5MWjyV+nhCGOFGnxjotalK4JqUnRE/JlKKnc/+ZpJqcma91dfuh4sayPEXDsQaVsWT8nllU5hbZnuMo1/HnJaeZL9HJD8x5BzzZcXDe02D5c7sDAkx41olWpTaY9mYT3c+iOQN8ddK7Vsqqvc/YI4S15ols4OIRR2d+z/gv5UmgHw2vLowAAAAlwSFlzAAAuIwAALiMBeKU/dgAAIABJREFUeAHs3e9rlFf++P+Xb/Z2wZY1dY03atFgQWcr0goBKd5InVDaZdhCV9E7baRWvtLWWiIthEBF0dou/WAtib0Tad+FXcJuKRmbG1KEgO8idsdAJZbqDSNpXFqh/0C+r3PO9eNc11zzI8lMMpM8B+xcc/0417ke55rJ7nld57zWiMic/uOFAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCKwYgf9ZMVfChSCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACgcAfkEAAAQQQQAABBBBAAAEEEGh9gbm5Ofn+hx/lmaefav3KUkMEEEAAAQQQQAABBJZRYM2aNfbsjABZxkbg1AgggAACCCCAAAIIIIAAAq0lMDMz01oVojZNF6DNm07cciegzVuuSZpeIdq86cQtdwLavOWapOkVqtTmBECaTs8JEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBBBAYKkFCIAstTjnQwABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAgaYLEABpOjEnQAABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAgaUWIACy1OKcDwEEEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBJou8Iemn4ETIIAAAggggAACCCCAAAIIIIDAggVmx07I4YubZHC0T7ZlljIpw4UBKe4dlNFD2XtkHjbPlZNDBRmQ5p5jnlVaWbuXhqUwWKxyTV3S99kpya+rsktTNrn7SwZGpS/XlBOsrEJtO94pb6sHRTnx+rDIaxfkVG+Hd82L87W/D1d3y4XTefFL9U7Q5MXF1b/JlWuN4oO2n6pSm7x+v168r7/1y9qWQQVtfa/K7mX5vamCtGI3BX/DK1yfuTeyf3trf/f4u+1QCYBUuLlYjQACCCCAAAIIIIAAAggggEDLCGy5I1/2F+XNjE7OyaEv5=="
	# [OR]
	# txtfilepath = "stock/krabby_patty.txt"	# PAYLOAD


	''' (3) Boolean Flag of Textbox or file option '''
	# If input_secret is a .txt file name
	if ('.txt' in input_secret) and (isTextBox == False):
		txtfile = input_secret
		txtfilepath = "./source/" + txtfile
		txtfilename = txtfile.split('.')[-2]		# takes the krabby_patty from "./source/krabby_patty.txt"
		print("[*] Text Filepath: ", txtfilepath)
		print("[*] Text Filename: ", txtfilename)
		
		filename_binary = convert_to_binary(txtfilename)
		delimiter_binary = convert_to_binary(DELIMITER)
		secret_string = get_string_from_txtfile(txtfilepath)

		# Append the filename with the delimiter and the secret body
		secret_binary = filename_binary + delimiter_binary + convert_to_binary(secret_string)
	else:
		secret_string = input_secret
		secret_binary = convert_to_binary(secret_string)



	''' (4) USER SELECT LSB '''
	# |-----|-----|-----|-----|-----|-----|-----|
	# 7		6	  5		4	  3     2     1     0
	# lsb_bit_selected = 1

	
	num_secret_bits = len(secret_binary)
	img_array = get_img(imgpath)

	total_color_bits, filesize_bits, max_height, max_width = get_total_bits(img_array)
	print("[*] Max Height: {}\n[*] Max Width: {}".format(max_height, max_width))


	valid_secret(total_color_bits, filesize_bits, num_secret_bits, lsb_bit_selected)

	first_pixel = img_array[0][0]	

	print(first_pixel)
	header.encode_firstpixel(first_pixel, isTextBox, isBase64, lsb_bit_selected)
	print(first_pixel)

	img_array, pixels_for_length, header_remainder_bits = header.encode_secretlength(img_array, num_secret_bits, filesize_bits, lsb_bit_selected)

	# Number of Pixels used so far, First Pixel + Pixels used by length
	num_header_pixels = 1 + pixels_for_length 

	print("[*] Total '{}' Pixels & '{}' remainder bits used for the header".format(num_header_pixels, header_remainder_bits))
	img_array = body.encode_secret(img_array, secret_binary, num_header_pixels, header_remainder_bits, lsb_bit_selected, max_height, max_width)

	''' 5. PROGRAM OUTPUT '''
	encoded_imgname = imgname + '_encoded' + '.png'
	file.creating_image(img_array, './output/' + encoded_imgname)

	''' 6. RETURN TO DOUG - successful termination '''
	return program_termination(0)



def decodeMain(encoded_imgname):

	''' 1. STEGO FILENAME '''
	imgpath = './output/' + encoded_imgname
	img_array = get_img(imgpath)
	first_pixel = img_array[0][0]
	selected_lsb, isTextBox, isBase64 = decode.get_metadata(first_pixel)
	print("[*] LSB Selected: ", selected_lsb)
	print("[*] Txtbox Selected: ", isTextBox)
	print("[*] base64 Selected: ", isBase64)
	total_color_bits, filesize_bits, max_height, max_width = get_total_bits(img_array)
	secret_size, size_pixel_used, size_remainder_bits = decode.get_secret_size(img_array, filesize_bits, selected_lsb)
	pixels_for_secret, body_remainder_bits = header.calculate_pixels(secret_size, selected_lsb)
	
	print("[*] Detected Secret Size: ", secret_size)
	print("[*] Header used '{}' pixels with '{}' size remainder bits".format(size_pixel_used, size_remainder_bits))
	print("[*] '{}' Pixels and '{}' Remainder Bits Needed to Store FULL Secret".format(pixels_for_secret, body_remainder_bits))

	secret_binary = decode.get_secret(img_array, secret_size, size_pixel_used, size_remainder_bits, selected_lsb, max_height, max_width)
	secret_string = decode.binary_to_string(secret_binary)

	# If NOT textbox and NOT base64
	if isTextBox == 0 and isBase64 == 0:
		'''
		TODO
		- NEED STORE TXTFILE NAME AS PART OF SECRET HAHAHHAHAHAHAHAHAH
		- SOURCE FOLDER 
		- RAISE ERROR
		'''
		temp_secret = secret_string.split(DELIMITER)
		txtfilename = temp_secret[0] + '.txt'
		secret_string = temp_secret[1]

		print("[*] Extracting Hidden txt file...")
		file.create_txtfile(secret_string, './output/' + txtfilename)
		print("[*] Extracted Hidden txt file!")
		secret_type = 2
	else:
		secret_type = isBase64	# 0: based64 or 1: normal
		txtfilename = ''

	''' 2. & 3. RETURN TO DOUG '''
	'''
	secret_type
	0: normal str
	1: base64 str
	2: txtfile str
	'''
	return txtfilename, secret_type, secret_string
	# IF 2: TXTFILE, UI DISPLAY TXTFILE DOWNLOADED and this is the contents of the txtfile


def main():
	''' FORMAT
	=== ENCODE FORMATS ===
		- .png (textbox) -> .png 
		- .jpg (textbox) -> .png 
		- .png (txtfile) -> .png         
        - .jpg (txtfile) -> .png
	=== DECODE FORMATS ===
		- png -> secret string
		- png -> txt file
		- png -> base64 string
	'''

	''' ENCODING
	--- PNG ENCODING ---
	[INPUT PARAMETERS]
	1.  ORIGINAL FILENAME (COVER OBJ) 
		- meow.jpg [string]
	2. 	SECRET STRING from txtbox [OR] SECRET TXTFILE filename (.txt) '/PNG/STOCK/krabby_patty.txt'
		- filename [string]
		- [OR]
		- secret text OR BASE 64 text [string]
	3. 	RADIO BUTTON FLAG
		- isTextBox [boolean]
	4. 	USER SELECTED LSB
		- etc 3 [int]

	[PROGRAM OUTPUT]
	5. ENCODED IMAGE with Secret (STEGO OBJ)
		- In /output folder

	[RETURN TO DOUG]
	[NEW] Return 0 for success
	[OLD] 6. Return output image name for UI to take & display
		- meow_encoded.jpg
	'''

	
	'''
	!!! DURING ENCODING if .TXT FILE detected as secret,
	1. Copy .txt file to /source/
		- So that jaden can take from source
	2. Return .txt filename to JADEN


	!!! DURING DECODING if .TXT FILE detected as secret,
	1. Display .txt file contents
	2. Tell user that secret .txt file extracted
	'''
	
	# secret_string = r"Anne Frank's The Diary of a \==:;Young Girl is among the most enduring documents of the twentieth century. Since its publication in 1947, it has been read by tens of millions of people all over the world. It remains a beloved and deeply admired testament to the indestructable nature of the human spirit. Restore in this Definitive Edition are diary entries that had been omitted from the original edition. These passages, which constitute 30 percent more material, reinforce the fact that Anne was first and foremost a teenage girl, not a remote and flawless symbol. She fretted about, and tried to copie with, her own emerging sexuality. Like many young girls, she often found herself in disagreement with her mother. And like any teenager, she veered between the carefree nature of a child and the full-fledged sorrow of an adult. Anne emerges more human, more vulnerable, and more vital than ever. Anne Frank and her family, fleeing the horrors of Nazi occupation, hid in the back of an Amsterdam warehouse for two years. She was thirteen when the family went into the Secret Annex, and in these pages she grows to be a young woman and a wise observer of human nature as well. With unusual insight, she reveals the relations between eight people living under extraordinary conditions, facing hunger, the ever-present threat of discovery and death, complete estrangement from the outside world, and above all, the boredom, the petty misunderstandings, and the frustrations of living under such unbearable strain, in such confined quarters. A timely story rediscovered by each new generation, The Diary of a Young Girl stands without peer. For both young readers and adults it continues to bring to life this young woman, who for a time survived the worst horror of the modern world had seen and who remained triumphantly and heartbreakingly human throughout her ordeal. For those who know and love Anne Frank, The Definitive Edition is a chance to discover her anew. For readers who have not yet encountered her, this is the edition to cherish. Anne Frank kept a diary from June 12, 1942, to August 1, 1944. Initially, she wrote it strictly for herself. Then, one day in 1944, Gerrit Bolkestein, a member of the Dutch government in exile, announced in a radio broadcast from Fondon that after the war he hoped to collect eyewitness accounts of the suffering of the Dutch people under the German occupation, which could be made available to the public. As an example, he specifically mentioned letters and diaries. Impressed by this speech, Anne Frank decided that when the war was over she would publish a book based on her diary. She began rewriting and editing her diary, improving on the text, omitting passages she didn't think were interesting enough and adding others from memory. At the same time, she kept up her original diary. In the scholarly work The Diary of Anne Frank: The Critical Edition (1989), Anne's first, unedited diary is referred to as version a, to distinguish it from her second, edited diary, which is known as version b. The last entry in Anne's diary is dated August 1, 1944. On August 4, 1944, the eight people hiding in the Secret Annex were arrested. Miep Gies and Bep Voskuijl, the two secretaries working in the building, found Anne's diaries strewn allover the floor. ,Miep Gies tucked them away in a desk drawer for safekeeping. After the war, when it became clear that Anne was dead, she gave the diaries, unread, to Anne's father, Otto Frank. After long deliberation, Otto Frank decided to fulfill his daughter's wish and publish her diary. He selected material from versions a and b, editing them into a shorter version later referred to as version c. Readers all over the world know this as The Diary of a fauna Girl. 'Paper has more patience than people.' I thought of this saying on one of those days when I was feeling a little depressed and was sitting at home with my chin in my hands, bored and listless, wondering whether to stay in or go out. I finally stayed where I was, brooding. Yes, paper does have more patience, and since I'm not planning to let anyone else read this stiff-backed notebook grandly referred to as a 'diary,' unless I should ever find a real friend, it probably won't make a bit of difference."
	secret_string = r"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkAAAAOECAYAAAD5Tf2iAAABb2lDQ1BpY2MAACiRdZFLS0JBGIYfrVDKKEgoosCFRYsCKYiWYZCbaqEGWW30eAu8HM5RQtoGbVoILaI23Rb9g9oGbQuCoAgiWvUDum1CTt+ooITNYc738M68HzPvgH0ho2XNdh9kcwUjGPB7ViKrHscbTobpxU1/VDP1xdB8mH/H9wM2Ve8nVK//97UcXfGEqYHNKTyt6UZBeFZ4YbOgK94VdmvpaFz4WHjckAMK3yg9VuNXxakafyo2wsE5sKuenlQTx5pYSxtZ4TFhbzZT1OrnUTdxJXLLIamDMocwCRLAj4cYRTbIUGBCak4ya+3zVX1L5MWjyV+nhCGOFGnxjotalK4JqUnRE/JlKKnc/+ZpJqcma91dfuh4sayPEXDsQaVsWT8nllU5hbZnuMo1/HnJaeZL9HJD8x5BzzZcXDe02D5c7sDAkx41olWpTaY9mYT3c+iOQN8ddK7Vsqqvc/YI4S15ols4OIRR2d+z/gv5UmgHw2vLowAAAAlwSFlzAAAuIwAALiMBeKU/dgAAIABJREFUeAHs3e9rlFf++P+Xb/Z2wZY1dY03atFgQWcr0goBKd5InVDaZdhCV9E7baRWvtLWWiIthEBF0dou/WAtib0Tad+FXcJuKRmbG1KEgO8idsdAJZbqDSNpXFqh/0C+r3PO9eNc11zzI8lMMpM8B+xcc/0417ke55rJ7nld57zWiMic/uOFAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCKwYgf9ZMVfChSCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACgcAfkEAAAQQQQAABBBBAAAEEEGh9gbm5Ofn+hx/lmaefav3KUkMEEEAAAQQQQAABBJZRYM2aNfbsjABZxkbg1AgggAACCCCAAAIIIIAAAq0lMDMz01oVojZNF6DNm07cciegzVuuSZpeIdq86cQtdwLavOWapOkVqtTmBECaTs8JEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBBBAYKkFCIAstTjnQwABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAgaYLEABpOjEnQAABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAgaUWIACy1OKcDwEEEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBJou8Iemn4ETIIAAAggggAACCCCAAAIIIIDAggVmx07I4YubZHC0T7ZlljIpw4UBKe4dlNFD2XtkHjbPlZNDBRmQ5p5jnlVaWbuXhqUwWKxyTV3S99kpya+rsktTNrn7SwZGpS/XlBOsrEJtO94pb6sHRTnx+rDIaxfkVG+Hd82L87W/D1d3y4XTefFL9U7Q5MXF1b/JlWuN4oO2n6pSm7x+v168r7/1y9qWQQVtfa/K7mX5vamCtGI3BX/DK1yfuTeyf3trf/f4u+1QCYBUuLlYjQACCCCAAAIIIIAAAggggEDLCGy5I1/2F+XNjE7OyaEv5=="
	txtfilepath = "krabby_patty.txt"
	# encoded_imgname = encodeMain('italy_medium.jpg', secret_string, True, 2)
	# exit_flag = encodeMain('rgb.png', secret_string, True, 2)		# isTextBox -> True
	# encoded_imgname = encodeMain('taylor.jpg', txtfilepath, False, 2)		# isTextBox -> False
	# print("[*] Exit Flag: ", exit_flag)


	'''
	--- PNG DECODING ---
	[INPUT PARAMETERS]
	1. Stego obj filename
		- IN SOURCE FOLDER
		- Process in this code if file extension is ONLY .png

	[RETURN TO DOUG]
	2. FLAG: I can tell u if its base64, .txtfile, text
		- if base64 then show download button
		- if .txtfile
			- DISPLAY TEXT
		- if text
			- DISPLAY TEXT
	3. SECRET:
		- can be base64 str
		- can be just text

	secret_type
	0: base64 syr
	1: normal str
	2: txtfile str

	'''
	txtfilename, secret_type, secret_str = decodeMain('frame0.png')
	if txtfilename:
		print("[*] Decoded txtfilename is: ", txtfilename)
	print("[*] Decoded Secret Type is: ", secret_type)
	print("[*] Decoded Secret String is: ", secret_str)
	

	sys.exit(0)



if __name__ == "__main__":
	main()