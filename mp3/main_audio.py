import os.path
import sys

import numpy as np
import wave
from pydub import AudioSegment
import filestream



def to_bin(data):
    # Convert 'data' to binary format as String
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [format(i, "08b") for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type is not supported.")

def convert_audio(source, dest):
    print('[*] Converting', source[-3:], 'to', dest[-3:], '...')
    
    print(source,"  ", dest)
    if source[-4:] == '.mp3':       # check if its a mp3 file, if it is, then convert to wav
        AudioSegment.from_mp3(source).export(dest, format=dest[-3:])
        return
    if source[-4:] == '.wav':
        AudioSegment.from_mp3(source).export(dest, format=dest[-3:])
    return

def limit_check(payload, cover_frames, bitrange):
    payload_length = len(payload)
    cover_length = len(cover_frames)
    print('Payload length:', payload_length)
    print('Cover length:', cover_length)
    if(payload_length > (cover_length * bitrange)):
        return 1
    return 0

def generate_wav(data, dest):
    print('[*] Writing new data to file...')
    file = open(dest, "wb")
    file.write(data)
    file.close

def encode_audio(source, dest, payload, bitrange):
    # error checking, and checking if file exists
    print('[*] Cover image URI is:', source, 'using', bitrange, 'bits.')
    if source[-4:] != '.wav':
        # convert mp3 to wav
        if source[-4:] == '.mp3':
            # convert current mp3 source into wav, as this method expects source to be of .wav type
            source_mp3 = source
            source = source[:-4]
            source += '.wav'
            # convert mp3 to wav
            convert_audio(source_mp3, source)
        else:
            print('[!] Only .wav and .mp3 files are supported.')
            return
    if dest[-4:] != '.wav':
        dest += '.wav'
    if not os.path.exists(source):
        print('[!] Source file does not exist, only .wav files are accepted for encoding')
        return 1
    # check if payload is a file or plaintext
    if os.path.exists(payload):
        # convert file's bytestream to binary stream, at the same time appending file type identifier
        bin_payload = filestream.get_stream(payload)
        # Append delimiter A5= to payload
        bin_payload += to_bin('A5=')
    else:
        print('[*] Payload is not a file, encoding as plaintext')
        # Append delimiter A5= to payload
        payload += "A5="
        # Convert payload to binary
        bin_payload = to_bin(payload)

    song = wave.open(source, 'rb')      # open audio file
    # Get all frames in wav
    # read all frames and store them
    frames = song.readframes(song.getnframes())
    # Do limit checking
    if limit_check(bin_payload, frames, bitrange):
        print(
            '[!] Payload size too large for cover .wav file, please use something smaller')
        # raise Exception("! Payload is larger than file !")
        return -1
    print('[*] Encoding...')
    frames = list(frames)
    # convert frames into bytearrays to work with
    frames = bytearray(frames)

    # apply payload padding
    # Split the payload into specified bitrange slices
    bin_payload = [bin_payload[index: index + bitrange]
                    for index in range(0, len(bin_payload), bitrange)]

    # set bitmask clear to specified bitranges
    bitmask = 0
    for i in range(0, bitrange):
        bitmask += 1 << i
    # convert bitmask integer into bytearray
    bitmask = bitmask.to_bytes(1, byteorder=sys.byteorder)
    # get first index of bytearray, as there is no use for lists
    bitmask = bitmask[0]

    # embed payload into frames, payload slices determined by bitrange specified
    for i, bits in enumerate(bin_payload):
        # if binary slice is not the specified bitrange length (usually happens to the last bit), add trailing 0s
        if len(bits) < bitrange:
            bits = bits.ljust(bitrange, '0')
        # clear specified number of bits, and set bits according to payload
        frames[i] = (frames[i] & ~bitmask) | int(bits, 2)
    # convert bytearray into bytes, the format to write to a wav file
    modded_frames = bytes(frames)
    # write to a wav file on specified destination
    with wave.open(dest, 'wb') as newfile:
        # ensure that song properties are maintained
        newfile.setparams(song.getparams())
        # write the embedded audio file
        newfile.writeframes(modded_frames)
        newfile.close()
    song.close()
    print('[*] Successfully encoded and exported to:', dest)
    return 0

def decode_audio(source, dest, bitrange, decodeformat='file'):
    print('[*] Attempting to decode:', source, 'using', bitrange, 'bits.')
    # Store decoded characters to see the delimiter
    prevprev_char = ''
    prev_char = ''
    current_char = ''
    if source[-4:] != '.wav':
        # convert mp3 to wav
        if source[-4:] == '.mp3':
            # convert current mp3 source into wav, as this method expects source to be of .wav type
            source_mp3 = source
            source = source[:-4]
            source += '.wav'
            # convert mp3 to wav
            convert_audio(source_mp3, source)

    if not os.path.exists(source):
        print('[!] Source file', source,
                'does not exist, only .wav and .mp3 files are accepted for decoding')
        return
    # Read frames from specified file
    print('[*] Decoding...')
    song = wave.open(source, 'rb')              # open audio file
    # read frames from audio file
    frames = song.readframes(song.getnframes())
    # convert frames into byte arrays for manipulation
    frames = bytearray(frames)
    decoded_bin = ''
    decoded_string = ''
    for byte in frames:
        # extract out bytearray into binary strings
        decoded_bin += to_bin(byte)[-bitrange:]

    if decodeformat == 'file':
        # slice out the front 4 bits first to identify format
        decoded_string = decoded_bin[:4]
        # extract data starting from 4th bit, as 1-4 is for identifier
        decoded_bin = decoded_bin[4:]
        # format as byte representation
        decoded_bin = [decoded_bin[index: index + 8]
                        for index in range(0, len(decoded_bin), 8)]
        for byte in decoded_bin:
            val = int(byte, 2)                  # convert byte to int
            # convert int to ascii characters
            current_char = format(val, 'c')
            if prevprev_char == 'A' and prev_char == '5' and current_char == '=':   # identify stop code A5=
                # trim off stop code
                decoded_string = decoded_string[:-16]
                break
            prevprev_char = prev_char       # update previous char for stop code identification
            prev_char = current_char        # update previous char for stop code identification
            decoded_string += byte
        extension = filestream.generate_from_stream(
            decoded_string, dest)   # generate file from
        return extension
    else:
        # Decoding plaintext string in audio file, no need for first 4 bit file identifier
        decoded_bin = [decoded_bin[index: index + 8]
                        for index in range(0, len(decoded_bin), 8)]
        for byte in decoded_bin:
            val = int(byte, 2)
            if 31 < val < 128:
                current_char = format(val, 'c')
                if prevprev_char == 'A' and prev_char == '5' and current_char == '=':
                    decoded_string = decoded_string[:-2]
                    break
                prevprev_char = prev_char
                prev_char = current_char
                decoded_string += current_char

        with open(dest, 'w') as newfile:
            newfile.write(decoded_string)
            newfile.close()
        print('[*] Successfully decoded and exported to', dest)
        return decoded_string


def mainEncode(audioName, payload, LSB_bit_Selected): #isTextBox?
    ''' (1) COVER AUDIO '''
   
    audiopath = "./source/" + audioName
    destinationPath = "./output/" + audioName.split(".")[0] + "_encoded"
    exit_flag = encode_audio(audiopath, destinationPath, payload, LSB_bit_Selected)
    return exit_flag

def mainDecode(encoded_audioName, LSB_bit_Selected):
    audiopath = './source/' + encoded_audioName
    destinationPath = "./output/decoded_from_Audio"
    payload = decode_audio(audiopath, destinationPath, LSB_bit_Selected, "")
    return payload



if __name__ == '__main__':
    # src = "..\\stock\\sample-15s.mp3"
    # src = "..\\source\\Original.wav"
    # dst = "..\\output\\encoded_from_Audio.wav"
    # dst2 = "..\\output\\decoded_from_Audio"
    # payload = "Jaden Armpit is green"
    payload = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkAAAAOECAYAAAD5Tf2iAAABb2lDQ1BpY2MAACiRdZFLS0JBGIYfrVDKKEgoosCFRYsCKYiWYZCbaqEGWW30eAu8HM5RQtoGbVoILaI23Rb9g9oGbQuCoAgiWvUDum1CTt+ooITNYc738M68HzPvgH0ho2XNdh9kcwUjGPB7ViKrHscbTobpxU1/VDP1xdB8mH/H9wM2Ve8nVK//97UcXfGEqYHNKTyt6UZBeFZ4YbOgK94VdmvpaFz4WHjckAMK3yg9VuNXxakafyo2wsE5sKuenlQTx5pYSxtZ4TFhbzZT1OrnUTdxJXLLIamDMocwCRLAj4cYRTbIUGBCak4ya+3zVX1L5MWjyV+nhCGOFGnxjotalK4JqUnRE/JlKKnc/+ZpJqcma91dfuh4sayPEXDsQaVsWT8nllU5hbZnuMo1/HnJaeZL9HJD8x5BzzZcXDe02D5c7sDAkx41olWpTaY9mYT3c+iOQN8ddK7Vsqqvc/YI4S15ols4OIRR2d+z/gv5UmgHw2vLowAAAAlwSFlzAAAuIwAALiMBeKU/dgAAIABJREFUeAHs3e9rlFf++P+Xb/Z2wZY1dY03atFgQWcr0goBKd5InVDaZdhCV9E7baRWvtLWWiIthEBF0dou/WAtib0Tad+FXcJuKRmbG1KEgO8idsdAJZbqDSNpXFqh/0C+r3PO9eNc11zzI8lMMpM8B+xcc/0417ke55rJ7nld57zWiMic/uOFAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCKwYgf9ZMVfChSCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACgcAfkEAAAQQQQAABBBBAAAEEEGh9gbm5Ofn+hx/lmaefav3KUkMEEEAAAQQQQAABBJZRYM2aNfbsjABZxkbg1AgggAACCCCAAAIIIIAAAq0lMDMz01oVojZNF6DNm07cciegzVuuSZpeIdq86cQtdwLavOWapOkVqtTmBECaTs8JEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBBBAYKkFCIAstTjnQwABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAgaYLEABpOjEnQAABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAgaUWIACy1OKcDwEEEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBJou8Iemn4ETIIAAAggggAACCCCAAAIIIIDAggVmx07I4YubZHC0T7ZlljIpw4UBKe4dlNFD2XtkHjbPlZNDBRmQ5p5jnlVaWbuXhqUwWKxyTV3S99kpya+rsktTNrn7SwZGpS/XlBOsrEJtO94pb6sHRTnx+rDIaxfkVG+Hd82L87W/D1d3y4XTefFL9U7Q5MXF1b/JlWuN4oO2n6pSm7x+v168r7/1y9qWQQVtfa/K7mX5vamCtGI3BX/DK1yfuTeyf3trf/f4u+1QCYBUuLlYjQACCCCAAAIIIIAAAggggEDLCGy5I1/2F+XNjE7OyaEv5=="

    mainEncode("Sample-15s.mp3", payload, 8)
    # decodeded_payload = mainDecode("Original_encoded.wav", 8)
    # print(decodeded_payload)