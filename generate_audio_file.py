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
META_DATA_FILE_NAME = "temp_metadata.txt"


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


def generate_audio_file(instructions_file_name: str, music_dispenser: MusicDispenser):
    total_time = 0
    audio_arrays = []
    chapter_times = []
    chapter_names_base = []
    instructions_list = read_instructions_file(instructions_file_name)
    for line in pbar(instructions_list):
        if type(line) == TextLine:
            if line.b_new_chapter:
                chapter_times.append(total_time)
                chapter_names_base.append(line.set_name)
            v = generate_audio_signal_from_text(line.text)
            audio_arrays.append(v)
            total_time += len(v) / WAV_SAMPLE_RATE
        elif type(line) == WaitLine:
            audio_time = line.time_seconds + line.delaybeep_time
            num_bins = int(audio_time / bin_delta_time_sec)
            v = music_dispenser.get_smooth_music_signal(num_bins)
            if line.b_beepreps or line.b_delaybeep:
                v = add_repcount_beeps_to_music(v, line.b_beepreps, line.num_beep_reps, line.b_delaybeep, line.delaybeep_time)
            audio_arrays.append(v)
            total_time += len(v) / WAV_SAMPLE_RATE
        else:
            raise Exception("unexpected code path")

    chapter_times.append(total_time)
    chapter_names_base.append(None)
    wf.write("temp_out.wav", WAV_SAMPLE_RATE, np.concatenate(audio_arrays))
    make_metadata_file(chapter_times, chapter_names_base)
    os.system(f"ffmpeg -v quiet -stats -y -i temp_out.wav -i {META_DATA_FILE_NAME} -map 0 -map_metadata 1 out_put_instructions_file.m4b")


def make_metadata_file(chapter_times, chapter_names_base):
    with open(META_DATA_FILE_NAME, "w+") as metadata_file:
        metadata_file.write(";FFMETADATA1\ntitle=Your Workout\nartist=Lior's Workout Instructinator\n\n")
        for i, (chapter_time_start, chapter_time_end) in enumerate(zip(chapter_times[:-1], chapter_times[1:])):
            metadata_file.write(
                "[CHAPTER]\n"
                "TIMEBASE=1/1000\n"
                f"START={chapter_time_start*1000}\n"
                f"END={chapter_time_end*1000}\n"
                f"title={chapter_names_base[i]} {i}\n\n"
            )


def inquire_input_path(query, default):
    try:
        import efipy
        path = efipy.inquire_input_path(query, default=default)
    except:
        path = input(query)
    return path


import sys
if len(sys.argv) >= 2:
    # instruction file passed as parameter
    instructions_file_names_arr = sys.argv[1:]
elif len(sys.argv) == 1:
    # ask user for instruction file
    instructions_file_names_arr = [inquire_input_path("enter instruction file path:", default="instructions.txt")]

# Ask User For Music Files
music_dispenser = MusicDispenser()
music_path = inquire_input_path("enter background music path:", default="songs")
music_dispenser.init_from_path(music_path)

for instructions_file_name in instructions_file_names_arr:
    try:
        generate_audio_file(instructions_file_name, music_dispenser)
    except Exception:
        print(traceback.format_exc())
        input()
        break
