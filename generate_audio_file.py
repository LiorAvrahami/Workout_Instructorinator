from read_instructions_file import *
from gtts import gTTS
import os
import scipy.io.wavfile as wf
import numpy as np
from music_dispenser import MusicDispenser, WAV_SAMPLE_RATE, normalize_audio, add_repcount_beeps_to_music
import traceback
try:
    from tqdm import tqdm as pbar
except:
    def pbar(arr):
        print("tqdm not installed, can't print progress. please install tqdm library")
        return arr
    
bin_delta_time_sec = 1 / WAV_SAMPLE_RATE


def __generate_audio_signal_from_text_priv(text):
    tts = gTTS(text, lang='en')
    tts.save('temp.mp3')
    os.system(f"ffmpeg -y -i temp.mp3 -ar {WAV_SAMPLE_RATE} temp.wav >nul 2>&1")
    a = wf.read("temp.wav")
    v = np.array(a[1], dtype=np.int16)
    v = normalize_audio(v)
    return np.vstack([v, v]).T


memoized_generate_audio_signal_from_text = {}


def generate_audio_signal_from_text(text):
    if text in memoized_generate_audio_signal_from_text:
        return memoized_generate_audio_signal_from_text[text]
    else:
        ret = __generate_audio_signal_from_text_priv(text)
        memoized_generate_audio_signal_from_text[text] = ret
        return ret


def generate_audio_file(music_dispenser: MusicDispenser):
    audio_arrays = []
    instructions_list = read_instructions_file()
    for line in pbar(instructions_list):
        if type(line) == TextLine:
            v = generate_audio_signal_from_text(line.text)
            audio_arrays.append(v)
        elif type(line) == WaitLine:
            audio_time = line.time_seconds + line.delaybeep_time
            num_bins = int(audio_time / bin_delta_time_sec)
            v = music_dispenser.get_smooth_music_signal(num_bins)
            if line.b_beepreps or line.b_delaybeep:
                v = add_repcount_beeps_to_music(v, line.b_beepreps, line.num_beep_reps, line.b_delaybeep, line.delaybeep_time)
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
try:
    generate_audio_file(music_dispenser)
except Exception:
    print(traceback.format_exc())
    input()
