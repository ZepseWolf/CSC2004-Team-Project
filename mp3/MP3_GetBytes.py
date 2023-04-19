# Modules required (pip install): Wave, Numpy, pydub, ffmpeg-python, got to download ffmpeg and put bin in PATH
# https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
# https://stackoverflow.com/questions/3049572/how-to-convert-mp3-to-wav-in-python
from os import path
from pydub import AudioSegment
import numpy as np
import wave

# convert mp3 files to wav format

def audio_convert(src, dst):                                                                         
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")

def encode(dst):
    audio_file = wave.open(dst, "r")
    audio_file_soundwave = audio_file.readframes(-1)
    print(audio_file_soundwave[:10])
    signal_audio = np.frombuffer(audio_file_soundwave, dtype = "int16")
    # print(type(signal_audio[0]))
    framerate_audio = audio_file.getframerate()
    # print(framerate_audio)
    duration_audio = len(signal_audio) / framerate_audio
    # print(duration_audio)
    # byte_array = bytearray.fromhex(str(signal_audio[5]))
    # print(byte_array)
    audio_file_soundwave = list(audio_file_soundwave)
    audio_file_soundwave = bytearray(audio_file_soundwave)
    print(audio_file_soundwave[:10])



def main():
    #Should covert to user input
    src = "..\\stock\\Good_Morning.mp3"
    dst = '..\\stock\\test.wav'            
    #audio_convert(src, dst)
    encode(dst)


if __name__ == "__main__":
	main()