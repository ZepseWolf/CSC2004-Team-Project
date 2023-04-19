
def calculate_pixels(num_bits, lsb_bit_selected):
	num_of_lsb  = lsb_bit_selected + 1
	num_of_bits_to_pixels = num_of_lsb * 3	# Multiply by 3 colors
	num_of_pixels = int(num_bits / num_of_bits_to_pixels)	
	remainder_bits = num_bits % num_of_bits_to_pixels
	return num_of_pixels, remainder_bits


def set_bit(color_value, pos, secret_bit):
	# print("Start Color => ", color_value)
	# print("Secret Bit => ", secret_bit)
	# Set mask based on the position (e.g 0000 0001 for bit 0)
	mask = 1 << pos	# push 1, [pos] number of times

	# Clears the masking bit
	color_value &= ~mask 	

	if secret_bit == 1:
		# Set the masking bit to 1
		color_value |= mask
	# print("End Color => ", color_value)
	# print("====================")
	return color_value


def write_length(img_array, secret_length_bin, pixels_for_length, filesize_bits, length_bits_used, lsb_bit_selected):
	bit_counter = 0
	length_bit_pos = 0
	# Loop for X number of Pixels, increments 1 to account for first pixel for LSB selection
	for pixel in range(1, pixels_for_length+1, 1):
		# Loop within each color of one Pixel (R,G,B)
		print("[***] Header PIXEL: ", pixel)
		for color in range(0, 3, 1): 
			# Loop within the user selected bits of one Color
			for bit_pos in range(lsb_bit_selected, -1, -1):
				# Once secret length written in full, return img_array
				if bit_counter == filesize_bits:
					return img_array
				elif bit_counter >= (filesize_bits - length_bits_used):
					(img_array[0][pixel])[color] = set_bit((img_array[0][pixel])[color], bit_pos, int(secret_length_bin[length_bit_pos]))
					length_bit_pos += 1
				else:
					(img_array[0][pixel])[color] = set_bit((img_array[0][pixel])[color], bit_pos, 0)
				# print(bit_counter)
				bit_counter += 1


def encode_secretlength(img_array, secret_length_dec, filesize_bits, lsb_bit_selected):
	
	secret_length_bin = bin(secret_length_dec)[2:] # str of binary
	length_bits_used = len(secret_length_bin)

	print("[*] Secret Bit Length => Decimal: {} | Binary: {}".format(secret_length_dec, secret_length_bin))
	print("[*] {} length_bits_used out of the total {} filesize_bits".format(length_bits_used, filesize_bits))
	
	pixels_for_length, remainder_bits = calculate_pixels(filesize_bits, lsb_bit_selected)
	print("[*] '{}' Pixels Needed to Store Length, '{}' Remainder Bits".format(pixels_for_length, remainder_bits))

	if remainder_bits != 0:
		pixels_for_length += 1	# Round UP the number of pixels if there is a remainder

	write_length(img_array, secret_length_bin, pixels_for_length, filesize_bits, length_bits_used, lsb_bit_selected)
	return img_array, pixels_for_length, remainder_bits



def encode_firstpixel(first_pixel, isTextBox, isBase64, lsb_bit_selected):
	'''
	[ R0 G0 B0 ] ==> 111 to 000
	[  0  1  0 ] e.g 010 == 2nd LSB set == 3 LSB bits
	(0010 000X, 0000 000X, 0000 000X) BIT 7 to BIT 0 - USER OPTION
	'''
	lsb_binary = format(lsb_bit_selected , '03b')	# for e.g 2 LSB Selected is (0,1,2 == 3) hence +1
	print("[*] User Selected LSB (in binary): ", lsb_binary)

	# Store flag in Color RED - Position 1
	if isTextBox == True:
		first_pixel[0] = set_bit(first_pixel[0], 1, 1)
	else:
		first_pixel[0] = set_bit(first_pixel[0], 1, 0)

	# Store flag in Color BLUE - Position 1
	if isBase64 == True:
		first_pixel[1] = set_bit(first_pixel[1], 1, 1)
	else:
		first_pixel[1] = set_bit(first_pixel[1], 1, 0)

	# Sets Each 0th Bit of Each Color with the lsb_binary
	for pos in range(0, 3, 1):
		first_pixel[pos] = set_bit(first_pixel[pos], 0, int(lsb_binary[pos]))
