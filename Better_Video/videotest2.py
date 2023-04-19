from gettext import bind_textdomain_codeset
import math
from pickle import FALSE
import sys
import cv2, numpy as np
import os
import shutil
from subprocess import call, STDOUT
from Better_Video import header
from Better_Video import body
from Better_Video import decode
from Better_Video import main_png
from PIL import Image

def convert_to_bin(data):
    """Convert `data` to binary format as string"""
    if isinstance(data, str):
        return ''.join([ format(ord(i), "08b") for i in data ])
    elif isinstance(data, bytes):
        return ''.join([ format(i, "08b") for i in data ])
    elif isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data ]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")

def extract_frames(videoName):
    if not os.path.exists("./temp"):
        os.makedirs("temp")
    print("[INFO] temp directory created")

    #Loads video and capture it's frames
    vidframecap = cv2.VideoCapture(videoName)
    print("Vid Name: ", videoName)
    #Create a loop to capture all frames then save each to unique filename for sorting later on
    framesgenerated = 0
    
    while True:
        success, image = vidframecap.read()
        
        if not success:
            break
        cv2.imwrite(os.path.join("./temp", "frame{:d}.png".format(framesgenerated)), image)
        framesgenerated += 1

    return framesgenerated

def clean(path):
    if os.path.exists("./" + path):
        shutil.rmtree("./" + path)
        print("[INFO] " + path + " files cleaned up")
        return 0 



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


def encodeVideo(videoName, secretData, LSB_bit):
    if os.path.exists("temp"):
        clean("temp")


    
    '''(1) COVER VIDEO'''
    videoPath = "./source/" + videoName
    videoNamewithoutExt = videoName.split(".")[0]
    fileExt = videoName.split(".")[1]

    '''(2) Payload Path'''
    print("[*] Counting Frames...")
    framecount = extract_frames(videoPath)
    #Check total number of frames generated
    print("Total Number of Frames Generated from Video:", framecount)

    #Checking if there is sufficient bytes in video to encode data

    binarysecretdata = convert_to_bin(secretData) #Convert data to binary

    totalbits = 0
    for frame in range(0, framecount, 1):
        framepath = (os.path.join("./temp", "frame{:d}.png".format(frame)))
        image = cv2.imread(framepath)  #Read the image
        totalbits += image.shape[0]	 * image.shape[1] * 3 * (LSB_bit+1)  #Maximum bytes to encode
    print("[*] Bits available for encoding:", totalbits)
    if len(binarysecretdata) > totalbits:
        print(len(binarysecretdata), "   ", totalbits)
        raise ValueError("[!] Insufficient bits to encode data of %d bits, need bigger image or less data." % len(binarysecretdata))
    else:
        print("[*] Sufficient bits to encode data of %d bits." % len(binarysecretdata))

    #Extract audio from video
    call(["ffmpeg", "-i", videoPath, "-q:a", "0", "-map", "a", "temp/audio.mp3", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)

    #Start encoding process
    dataindex = 0
    full_data_len = len(binarysecretdata)
    print("Data to hide: {:d} bits",format(full_data_len))

    for frame in range(0, framecount, 1):

        framepath = (os.path.join("./temp", "frame{:d}.png".format(frame)))
        image = main_png.get_img(framepath)  #Read the image
        datalen = len(binarysecretdata) 
        height_pixels = image.shape[0]		
        width_pixels = image.shape[1]
        total_color_bits, filesize_bits, height_pixels, width_pixels = get_total_bits(image)


        pixels_per_frame = height_pixels * width_pixels
        colors_per_frame = pixels_per_frame * 3
        bits_avail_per_frame = colors_per_frame * (LSB_bit+1) 

       
        print("Frame {:d} Bits_Capacity : {:d}".format(frame, bits_avail_per_frame))

        bitsLeft = datalen - bits_avail_per_frame
        if(bitsLeft <= 0 ):
            bitsLeft = 0
            bits_to_encode = datalen
        else:
            bits_to_encode = bits_avail_per_frame
        
        Bin_Data_For_Frame = binarysecretdata[:bits_to_encode]
        # print("!!! BIN DATA FOR FRAME: ", Bin_Data_For_Frame)
        binarysecretdata = binarysecretdata[bits_to_encode:] #Remove whatever that was used to encode already. 
        # print("!!! binarysecretdata: ", binarysecretdata)
        # print("Bits to encode to frame ",str(frame)) #Can adjust accordingly
        # print("Remaining Bits left to encode: ", bitsLeft)

        #--------------------  Jaden Encode codes (Modified) ---------------------------
        if frame == 0:
            print("ENCODING FIRST FRAME FIRST PIXEL")
            first_pixel = image[0][0]
            # filesize_bit = math.ceil(math.log2(frameCapacity))

            isTextBox = True
            isBase64 = False
            header.encode_firstpixel(first_pixel, isTextBox, isBase64, LSB_bit)
            image, pixels_for_length, header_remainder_bits = header.encode_secretlength(image, full_data_len, filesize_bits, LSB_bit)
        
            # Number of Pixels used so far, First Pixel + Pixels used by length
            Frame0_num_header_pixels = 1 + pixels_for_length
            print("[*] Total '{}' Pixels & '{}' remainder bits used for the header".format(Frame0_num_header_pixels, header_remainder_bits))
            image = body.encode_secret(image, Bin_Data_For_Frame, Frame0_num_header_pixels, header_remainder_bits, LSB_bit, height_pixels, width_pixels)
        else:
            Start_pixels = 0
            Zero_remainder_bits = 0
            image = body.encode_secret(image, Bin_Data_For_Frame, Start_pixels, Zero_remainder_bits, LSB_bit, height_pixels, width_pixels)

        print("[*] Creating new image with edited pixels...")
        data = Image.fromarray(image.astype(np.uint8)).convert('RGB')
        data.save('temp/frame{}.png'.format(frame))
   
        # cv2.imwrite(os.path.join("./temp", "frame{}.png".format('abc')), image) #Replace old frame with new frame
        
        if(bitsLeft == 0): #If data is encoded, just break out of the Loop
            print("[*] All Bits Encoded")
            break
        #If not all data encoded, program will continue looping
        
        #-------------------------------------------------------------------------------
    print("[*] Creating MP4 File......")
    call(["ffmpeg", "-i", "temp/frame%d.png", "-vcodec", "png", "temp/noAudioStegoVid.avi", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)
    call(["ffmpeg", "-i", "temp/noAudioStegoVid.avi", "-i", "temp/audio.mp3", "-codec", "copy", "temp/audioStegoVid.avi", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)
    call(["ffmpeg", "-i", "temp/audioStegoVid.avi", "-f", "avi", "-c:v", "rawvideo", "-pix_fmt", "rgb32", "./output/" + videoNamewithoutExt + "_encoded" + "." + fileExt], stdout=open(os.devnull, "w"), stderr=STDOUT)
    print("[*] Cleaning Temp Folder.... ")
    clean("temp")

    return 0


def decodeVideo(videoName):

    if os.path.exists("temp"):
        clean("temp")


    '''Stego file location'''
    videoPath = './output/' + videoName + ".mp4"
    # videoNamewithoutExt = videoName.split(".")[0]
    # fileExt = videoName.split(".")[1]

    framecount = extract_frames(videoPath)

    # Check total number of frames generated
    print("Total Number of Frames Generated from Video:", framecount)

    secret_string = ""

    for frame in range(0, framecount, 1):
        framepath = (os.path.join("./temp", "frame{:d}.png".format(frame)))
        image = main_png.get_img(framepath)  # Read the image
        height_pixels = image.shape[0]		
        width_pixels = image.shape[1]

        print("[+] Decoding...")
        if(frame == 0):
            first_pixel = image[0][0]
            selected_lsb, isTextBox, isBase64 = decode.get_metadata(first_pixel)
            print("[*] LSB Selected: ", selected_lsb)
            total_color_bits, filesize_bits, max_height, max_width = main_png.get_total_bits(image)
            secret_size, size_pixel_used, size_remainder_bits = decode.get_secret_size(image, filesize_bits, selected_lsb)
            frame_capacity = max_height * max_width * 3 * selected_lsb
            num_Of_Frame_Used = math.ceil(secret_size/frame_capacity)

        print("[*] Detected Secret Size: ", secret_size)
        print("[*] Number of Frames used to encode: ", num_Of_Frame_Used)
        print("Frame Number: ", frame)

        pixels_per_frame = height_pixels * width_pixels
        colors_per_frame = pixels_per_frame * 3
        bits_avail_per_frame = colors_per_frame * (selected_lsb+1) 


        if(frame == 0):
            bitsLeft = secret_size - bits_avail_per_frame
        else:
            bitsLeft = bitsLeft - bits_avail_per_frame

        if(bitsLeft <= 0 ):
            bitsLeft = 0
            bits_to_decode = secret_size
        else:
            bits_to_decode = bits_avail_per_frame



        if(frame == 0):
            secret_binary = decode.get_secret(image, bits_to_decode, size_pixel_used, size_remainder_bits, selected_lsb, max_height, max_width)
            secret_string = secret_string + decode.binary_to_string(secret_binary)

        else: 
            Start_pixels = 0
            Zero_remainder_bits = 0
            secret_binary = decode.get_secret(image, secret_size, Start_pixels, Zero_remainder_bits, selected_lsb, max_height, max_width)
            secret_string = secret_string + decode.binary_to_string(secret_binary)
        
        
        if((frame + 1) == num_Of_Frame_Used):
            break

    print("Secret string: ", secret_string)
    clean("temp")
    return secret_string



if __name__ == "__main__":


    # while True:
    print("1.Insert payload 2.Reveal secret from video")
    print("any other value to exit")
    # choice = input()
    choice = '2'
    if choice == '1':
        # secret_data = input("Enter payload file: ")
        # videoFile = input("Enter video file: ")
        # LSB_bit = input("Enter LSB: ")
        secret_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkAAAAOECAYAAAD5Tf2iAAABb2lDQ1BpY2MAACiRdZFLS0JBGIYfrVDKKEgoosCFRYsCKYiWYZCbaqEGWW30eAu8HM5RQtoGbVoILaI23Rb9g9oGbQuCoAgiWvUDum1CTt+ooITNYc738M68HzPvgH0ho2XNdh9kcwUjGPB7ViKrHscbTobpxU1/VDP1xdB8mH/H9wM2Ve8nVK//97UcXfGEqYHNKTyt6UZBeFZ4YbOgK94VdmvpaFz4WHjckAMK3yg9VuNXxakafyo2wsE5sKuenlQTx5pYSxtZ4TFhbzZT1OrnUTdxJXLLIamDMocwCRLAj4cYRTbIUGBCak4ya+3zVX1L5MWjyV+nhCGOFGnxjotalK4JqUnRE/JlKKnc/+ZpJqcma91dfuh4sayPEXDsQaVsWT8nllU5hbZnuMo1/HnJaeZL9HJD8x5BzzZcXDe02D5c7sDAkx41olWpTaY9mYT3c+iOQN8ddK7Vsqqvc/YI4S15ols4OIRR2d+z/gv5UmgHw2vLowAAAAlwSFlzAAAuIwAALiMBeKU/dgAAIABJREFUeAHs3e9rlFf++P+Xb/Z2wZY1dY03atFgQWcr0goBKd5InVDaZdhCV9E7baRWvtLWWiIthEBF0dou/WAtib0Tad+FXcJuKRmbG1KEgO8idsdAJZbqDSNpXFqh/0C+r3PO9eNc11zzI8lMMpM8B+xcc/0417ke55rJ7nld57zWiMic/uOFAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCKwYgf9ZMVfChSCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACgcAfkEAAAQQQQAABBBBAAAEEEGh9gbm5Ofn+hx/lmaefav3KUkMEEEAAAQQQQAABBJZRYM2aNfbsjABZxkbg1AgggAACCCCAAAIIIIAAAq0lMDMz01oVojZNF6DNm07cciegzVuuSZpeIdq86cQtdwLavOWapOkVqtTmBECaTs8JEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBBBAYKkFCIAstTjnQwABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAgaYLEABpOjEnQAABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAgaUWIACy1OKcDwEEEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBJou8Iemn4ETIIAAAggggAACCCCAAAIIIIDAggVmx07I4YubZHC0T7ZlljIpw4UBKe4dlNFD2XtkHjbPlZNDBRmQ5p5jnlVaWbuXhqUwWKxyTV3S99kpya+rsktTNrn7SwZGpS/XlBOsrEJtO94pb6sHRTnx+rDIaxfkVG+Hd82L87W/D1d3y4XTefFL9U7Q5MXF1b/JlWuN4oO2n6pSm7x+v168r7/1y9qWQQVtfa/K7mX5vamCtGI3BX/DK1yfuTeyf3trf/f4u+1QCYBUuLlYjQACCCCAAAIIIIAAAggggEDLCGy5I1/2F+XNjE7OyaEv5=="
        # secret_data = "asdf"
        videoFile = "asd.mp4"
        LSB_bit = 4
        # LSB_bit = int(LSB_bit)

        # with open(payloadfile, "rb") as f:
        #     secret_data = f.read()

        encodeVideo(videoFile, secret_data, LSB_bit)
    elif choice == '2':
        videoFile = input("Enter video file to decode: ")
        decoded_data = decodeVideo(videoFile)
    # else:
    #     break