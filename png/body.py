

from png import header
from png import main_png as main

# import header
# import main_png as main


def detect_color_to_start(length_remainder_bits, lsb_bit_selected):
	counter = -1
	'''
	(0:R, 1:G. 2:B)
	'''
	for color in range(0, 3, 1):
		for bit in range(lsb_bit_selected, -1, -1):
			counter += 1 
			if counter == length_remainder_bits:
				# Returns starting position to write
				return color, bit
			

def process_initial_excess(remainder_pixel, secret_binary, start_color, start_bit, lsb_bit_selected):
	secret_pos = 0
	write_flag = False
	# Loop within each color of one Pixel (R,G,B)
	for color in range(start_color, 3, 1): 
		# Loop within the user selected bits of one Color
		for bit_pos in range(lsb_bit_selected, -1, -1):
			if (write_flag == False) and (bit_pos == start_bit):
				write_flag = True
				
			if (write_flag == True):
				remainder_pixel[color] = header.set_bit(remainder_pixel[color], bit_pos, int(secret_binary[secret_pos]))
				secret_pos += 1
	return remainder_pixel, secret_pos


def process_body(img_array, pixel_to_start, last_row_id, max_width, secret_binary, secret_pos, lsb_bit_selected):
	print("[*] Writing body to Pixel '{}'".format(pixel_to_start))
	length_of_secret = len(secret_binary)
	# Looping each row of img_array
	for row in range(0, last_row_id+1, 1):
		# Set first pixel of each subsequent row
		if row != 0:
			pixel_to_start = 0

		cur_last_col_id = max_width
		# Loop for X number of Pixels, increments 1 to account for first pixel for LSB selection
		for pixel in range(pixel_to_start, cur_last_col_id, 1):
			# Loop within each color of one Pixel (R,G,B)
			# print("[***] PIXEL: ", pixel)
			for color in range(0, 3, 1): 
				# Loop within the user selected bits of one Color
				for bit_pos in range(lsb_bit_selected, -1, -1):
					(img_array[row][pixel])[color] = header.set_bit((img_array[row][pixel])[color], bit_pos, int(secret_binary[secret_pos]))
					secret_pos += 1
					if secret_pos == length_of_secret:
						return img_array, secret_pos



def process_tail(tail_pixel, secret_binary, secret_pos, final_remainder_bits, lsb_bit_selected):
	break_counter = 0
	# Loop within each color of Tail Pixel (R,G,B)
	for color in range(0, 3, 1): 
		# Loop within the user selected bits of one Color
		for bit_pos in range(lsb_bit_selected, -1, -1):
			tail_pixel[color] = header.set_bit(tail_pixel[color], bit_pos, int(secret_binary[secret_pos]))
			secret_pos += 1 
			break_counter += 1
			if break_counter == final_remainder_bits:
				print("[*] Tail Pixel: ", tail_pixel)
				print("[*] Final secret pos (after remainder): ", secret_pos)
				return tail_pixel


def detect_rows(max_height, max_width, last_pixel):
	last_row_id = 0 	# Default number of rows
	last_col_id = last_pixel
	if last_pixel > max_width:
		last_col_id = last_pixel % max_width
		last_row_id = int(last_pixel / max_width)
		if last_row_id > max_height:
			main.program_termination(100)
	print("[*] {} Rows and {} Cols needed to write data!".format(last_row_id, last_col_id))
	return last_row_id, last_col_id
	


def encode_secret(img_array, secret_binary, num_header_pixels, header_remainder_bits, lsb_bit_selected, max_height, max_width):
	num_secret_bits = len(secret_binary)
	pixels_for_secret, body_remainder_bits = header.calculate_pixels(num_secret_bits, lsb_bit_selected)
	print("[*]'{}' Pixels and '{}' Remainder Bits Needed to Store FULL Secret".format(pixels_for_secret, body_remainder_bits))
	
	start_pixel = num_header_pixels - 1
	if header_remainder_bits:
		start_pixel += 1

	print("[*] WRITE BODY TO THIS pixel[{}]".format(start_pixel))
	
	
	last_body_pixel = start_pixel + pixels_for_secret
	print("[*] Last Body Pixel: ", last_body_pixel)
	last_row_id, last_col_id = detect_rows(max_height, max_width, last_body_pixel)
	rows_needed = last_row_id + 1
	print("[*] Last Row ID: ", last_row_id)
	print("[*] Last Col ID: ", last_col_id)
	print("[*] Rows Needed to write data: ", rows_needed)
	
	secret_pos = 0
	img_array, secret_pos = process_body(img_array, start_pixel, last_row_id, max_width, secret_binary, secret_pos, lsb_bit_selected)

	print("[*] Final secret pos: ", secret_pos)
	
	return img_array
