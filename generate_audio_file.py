from read_instructions_file import *
from gtts import gTTS
import os
from scipy.io.wavfile import read, write
import numpy as np

bin_delta_time_sec = 1 / 16000


def generate_audio_signal_from_text(text):
    tts = gTTS(text, lang='en')
    tts.save('temp.mp3')
    os.system("ffmpeg -y -i temp.mp3 -ar 16000 -ac 1 temp.wav")
    a = read("temp.wav")
    v = np.array(a[1], dtype=np.int16)
    return v


def generate_audio_file():
    audio_arrays = []
    instructions_list = read_instructions_file()
    for line in instructions_list:
        if type(line) == TextLine:
            v = generate_audio_signal_from_text(line.text)
            audio_arrays.append(v)
        elif type(line) == WaitLine:
            num_bins = int(line.time_seconds / bin_delta_time_sec)
            audio_arrays.append(np.zeros(num_bins,dtype=np.int16))
        else:
            raise Exception("unexpected code path")
        
    write("out.wav",16000,np.concatenate(audio_arrays))
        
    


generate_audio_file()
