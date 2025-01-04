from python_files.read_instructions_file import *
from gtts import gTTS
import os
import python_files.wav_read_write as wf
import numpy as np
from python_files.music_dispenser import MusicDispenser, WAV_SAMPLE_RATE, normalize_audio, add_repcount_beeps_to_music
import traceback
try:
    from tqdm import tqdm as pbar
except:
    def pbar(arr):
        print("tqdm not installed, can't print progress. please install tqdm library")
        return arr

bin_delta_time_sec = 1 / WAV_SAMPLE_RATE
META_DATA_FILE_NAME = "temp_metadata.txt"


def __generate_audio_signal_from_text_priv(text, speaker: Speaker):
    tts = gTTS(text, lang='en', tld=speaker.accent)
    tts.save('temp.mp3')

    if speaker.speed != 1:
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3("temp.mp3")
        final = audio.speedup(playback_speed=speaker.speed)
        # export to mp3
        final.export("temp.mp3", format="mp3")

    os.system(f"ffmpeg -y -i temp.mp3 -ar {WAV_SAMPLE_RATE} temp.wav >nul 2>&1")
    a = wf.read("temp.wav")
    v = np.array(a[1], dtype=np.int16)
    v = normalize_audio(v)
    return np.vstack([v, v]).T


memoized_generate_audio_signal_from_text = {}


def generate_audio_signal_from_text(text, speaker: Speaker):
    if (text, speaker) in memoized_generate_audio_signal_from_text:
        return memoized_generate_audio_signal_from_text[(text, speaker)]
    else:
        ret = __generate_audio_signal_from_text_priv(text, speaker)
        memoized_generate_audio_signal_from_text[(text, speaker)] = ret
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
            v = generate_audio_signal_from_text(line.text, line.speaker)
            audio_arrays.append(v)
            total_time += len(v) / WAV_SAMPLE_RATE
        elif type(line) == WaitLine:
            audio_time = line.time_seconds + line.delaybeep_time
            num_bins = int(audio_time / bin_delta_time_sec)
            v = music_dispenser.get_smooth_music_signal(num_bins, b_until_end_of_song=line.b_until_end_of_song)
            if line.b_beepreps or line.b_delaybeep:
                v = add_repcount_beeps_to_music(v, line.b_beepreps, line.num_beep_reps, line.b_delaybeep, line.delaybeep_time)
            audio_arrays.append(v)
            total_time += len(v) / WAV_SAMPLE_RATE
        else:
            raise Exception("unexpected code path")

    chapter_times.append(total_time)
    chapter_names_base.append(None)
    wf.write("temp_out.wav", WAV_SAMPLE_RATE, np.concatenate(audio_arrays))

    chapter_times, chapter_names_base = truncate_tiny_chapters(chapter_times, chapter_names_base)
    make_metadata_file(chapter_times, chapter_names_base)
    os.system(
        f"ffmpeg -loglevel error -stats -y -i temp_out.wav -i {META_DATA_FILE_NAME} -map 0 -map_metadata 1 {os.path.splitext(instructions_file_name)[0]}.m4b")


def truncate_tiny_chapters(chapter_times, chapter_names_base):
    # truncate tiny chapters. if one chapter is large and is fallowed by a tiny chapter, then the tiny chapter should be swallowed into the large chapter.
    tiny_chapter_size_seconds = 15
    large_chapter_size_seconds = 40
    chapter_lengths = np.diff(chapter_times)
    chapter_times_to_remove = []
    i = 1
    while i < len(chapter_lengths):
        if chapter_lengths[i] < tiny_chapter_size_seconds and chapter_lengths[i - 1] > large_chapter_size_seconds:
            chapter_times_to_remove.append(i)
            i += 1
        i += 1
    del i

    chapter_times = [chapter_times[i] for i in range(len(chapter_times)) if i not in chapter_times_to_remove]
    chapter_names_base = [chapter_names_base[i] for i in range(len(chapter_names_base)) if i not in chapter_times_to_remove]
    return chapter_times, chapter_names_base


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
    instructions_file_names_arr = [inquire_input_path("enter instruction file path:", default="")]

# Ask User For Music Files
music_path = inquire_input_path("enter background music path:", default="songs")

for instructions_file_name in instructions_file_names_arr:
    if os.path.splitext(instructions_file_name)[-1] != ".txt":
        continue
    try:
        music_dispenser = MusicDispenser()
        music_dispenser.init_from_path(music_path)
        generate_audio_file(instructions_file_name, music_dispenser)
    except Exception:
        print(traceback.format_exc())
        input()
        break
