from read_instructions_file import *
from gtts import gTTS
import os
import scipy.io.wavfile as wf
import numpy as np
from music_dispenser import MusicDispenser, WAV_SAMPLE_RATE

bin_delta_time_sec = 1 / WAV_SAMPLE_RATE


def generate_audio_signal_from_text(text):
    tts = gTTS(text, lang='en')
    tts.save('temp.mp3')
    os.system(f"ffmpeg -y -i temp.mp3 -ar {WAV_SAMPLE_RATE} temp.wav")
    a = wf.read("temp.wav")
    v = np.array(a[1], dtype=np.int16)
    return np.vstack([v, v]).T


def generate_audio_file(music_dispenser: MusicDispenser):
    audio_arrays = []
    instructions_list = read_instructions_file()
    for line in instructions_list:
        if type(line) == TextLine:
            v = generate_audio_signal_from_text(line.text)
            audio_arrays.append(v)
        elif type(line) == WaitLine:
            num_bins = int(line.time_seconds / bin_delta_time_sec)
            v = music_dispenser.get_music_signal(num_bins)
            audio_arrays.append(v)
        else:
            raise Exception("unexpected code path")

    wf.write("out.wav", WAV_SAMPLE_RATE, np.concatenate(audio_arrays))


music_dispenser = MusicDispenser()
music_dispenser.init_from_path("11 - Burnin' For You.mp3")
generate_audio_file(music_dispenser)
