from read_instructions_file import *
from gtts import gTTS
import os
import scipy.io.wavfile as wf
import numpy as np
from music_dispenser import MusicDispenser, WAV_SAMPLE_RATE, normalize_audio

bin_delta_time_sec = 1 / WAV_SAMPLE_RATE


def generate_audio_signal_from_text(text):
    tts = gTTS(text, lang='en')
    tts.save('temp.mp3')
    os.system(f"ffmpeg -y -i temp.mp3 -ar {WAV_SAMPLE_RATE} temp.wav")
    a = wf.read("temp.wav")
    v = np.array(a[1], dtype=np.int16)
    v = normalize_audio(v)
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
            v = music_dispenser.get_smooth_music_signal(num_bins)
            audio_arrays.append(v)
        else:
            raise Exception("unexpected code path")

    wf.write("temp_out.wav", WAV_SAMPLE_RATE, np.concatenate(audio_arrays))
    os.system("ffmpeg -y -i temp_out.wav out_put_instructions_file.mp3")


music_dispenser = MusicDispenser()
try:
    import efipy
    music_path = efipy.inquire_input_path("enter background music path:", default="songs")
    music_dispenser.init_from_path(music_path)
except:
    music_path = input("enter background music path:")
generate_audio_file(music_dispenser)
