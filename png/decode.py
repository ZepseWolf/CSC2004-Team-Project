
from png import body

# import body


def get_metadata(first_pixel):
	red_binary = format(first_pixel[0], '08b')
	blue_binary = format(first_pixel[1], '08b')
	green_binary = format(first_pixel[2], '08b')

	# Retrieve Stored flag in Color Red - Position 1
	txtbox_flag = red_binary[6]

	base64_flag = blue_binary[6]

	red_lsb = red_binary[-1:]
	blue_lsb = blue_binary[-1:]
	green_lsb = green_binary[-1:]

	return int(red_lsb + blue_lsb + green_lsb, 2), int(txtbox_flag), int(base64_flag)

def read_secret_size(img_array, filesize_bits, whole_pixels_used, lsb_bit_selected):
	secret_size = ''
	for pixel in range(1, 1 + whole_pixels_used, 1):
		cur_pixel = img_array[0][pixel]
		for color in range(0, 3, 1):
			for bit_pos in range(7-lsb_bit_selected, 8, 1):
				secret_size += format(cur_pixel[color], '08b')[bit_pos]
				filesize_bits -= 1
				if filesize_bits == 0:
					return secret_size


def get_secret_size(img_array, filesize_bits, lsb_bit_selected):
	num_of_lsb = lsb_bit_selected + 1 
	total_pixels_used = (filesize_bits / num_of_lsb) / 3
	whole_pixels_used = int(total_pixels_used)
	remainder_bits = filesize_bits % (num_of_lsb * 3)
	print("[*] Whole Pixels used for file size: ", whole_pixels_used)
	print("[*] Remainder bits: ", remainder_bits)

	if remainder_bits != 0:
		whole_pixels_used += 1
	
	secret_size_binary = read_secret_size(img_array, filesize_bits, whole_pixels_used, lsb_bit_selected)
	secret_size = int(secret_size_binary, 2) # Convert back to decimal

	return secret_size, whole_pixels_used, remainder_bits


def read_secret(img_array, secret_size, pixel_to_start, last_row_id, last_col_id, max_width, lsb_bit_selected):
	secret = ''
	print(last_row_id, last_col_id)

	
	for row in range(0, last_row_id + 1, 1):
		# print(">>>>>>>> Doing row: ", row)
		if row != 0:
			pixel_to_start = 0

		cur_last_col_id = max_width
		for pixel in range(pixel_to_start, cur_last_col_id, 1):
			
			# print(pixel)
			cur_pixel = img_array[row][pixel]
			for color in range(0, 3, 1):
				for bit_pos in range(7-lsb_bit_selected, 8, 1):
					secret += format(cur_pixel[color], '08b')[bit_pos]
					
					secret_size -= 1
					# print(secret_size)
					if secret_size == 0:
						return secret
	print("why are u here")


def get_secret(img_array, secret_size, num_header_pixels, header_remainder_bits, lsb_bit_selected, max_height, max_width):
	num_of_lsb = lsb_bit_selected + 1
	total_pixels_used = int((secret_size / num_of_lsb) / 3)
	print("[*] Total Pixels Used: ", total_pixels_used)
	
	
	if header_remainder_bits:
		start_pixel = num_header_pixels + 1
	else:
		start_pixel = num_header_pixels
	last_pixel_used = start_pixel + total_pixels_used
	print(last_pixel_used)
	print("[*] Pixel['{}'] to START decoding secret".format(start_pixel))
	last_row_id, last_col_id = body.detect_rows(max_height, max_width, last_pixel_used)
	print("[*] Final Pixel['{}'] to END decoding of secret".format(start_pixel))
	secret = read_secret(img_array, secret_size, start_pixel, last_row_id, last_col_id, max_width, lsb_bit_selected)
	return secret
	

def binary_to_string(secret_binary):
	secret_string = ''
	char_binary = ''
	char_counter = 0
	for each_bit in secret_binary:
		char_binary += each_bit
		char_counter += 1
		if char_counter == 8:
			secret_string += chr(int(char_binary, 2))
			char_binary = ''	# Reset Char binary
			char_counter = 0	# Reset char counter
	return secret_string


