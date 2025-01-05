from python_files.ffmpeg_name_file import ffmpeg_name
import itertools
import os
from typing import Iterator, Optional
import warnings
import python_files.wav_read_write as wf
import numpy as np
try:
    from tqdm import tqdm as pbar
except:
    def pbar(arr):
        print("tqdm not installed, can't print progress. please install tqdm library")
        return arr

WAV_SAMPLE_RATE = 44100
MASTER_VOLUME = 10000


def convert_file_to_wav(path):
    path_name, ext = os.path.splitext(path)
    os.system(f"{ffmpeg_name} -y -i \"{path}\" -ar {WAV_SAMPLE_RATE} \"{path_name}_{WAV_SAMPLE_RATE}.wav\" >nul 2>&1")
    return f"{path_name}_{WAV_SAMPLE_RATE}.wav"


def normalize_audio(data):
    try:
        import pyloudnorm as pyln
        # measure the loudness first
        meter = pyln.Meter(WAV_SAMPLE_RATE)  # create BS.1770 meter
        data = data.astype(float) / np.max(np.abs(data))
        data_temp = np.copy(data)
        if len(data_temp) < meter.block_size * WAV_SAMPLE_RATE:
            data_temp = np.concatenate([data_temp] * (int(meter.block_size * WAV_SAMPLE_RATE / len(data_temp)) + 1))
        loudness = meter.integrated_loudness(data_temp)
        # loudness normalize audio to -12 dB LUFS
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = pyln.normalize.loudness(data, loudness, -12.0)
    except ModuleNotFoundError as e:
        print(f"Warning, pyloudnorm not installed. using rms norm for audio normalization. {e}")
        rms = np.sqrt(np.mean(data.astype(float)**2))
        data = data.astype(float) / rms
    data *= MASTER_VOLUME
    data[np.abs(data) > 2**14] = 2**14 * np.sign(data[np.abs(data) > 2**14])
    data = data.astype(np.int16)
    return data


# load sfx files
try:
    delay_end_sfx = normalize_audio(wf.read(r"sfx\delay_end.wav")[1].astype(np.int16))
    delay_start_sfx = normalize_audio(wf.read(r"sfx\delay_indicator.wav")[1].astype(np.int16))
    rep_count_sfx = normalize_audio(wf.read(r"sfx\rep_count.wav")[1].astype(np.int16))
except Exception as ex:
    print("WARNING: couldn't load indicator sound effects, Will continue without them.")
    delay_end_sfx = np.zeros(10, np.int16)
    delay_start_sfx = np.zeros(10, np.int16)
    rep_count_sfx = np.zeros(10, np.int16)


def add_repcount_beeps_to_music(music_data, b_has_rep_beeps, number_of_beeps, b_has_initial_beep, initial_delaybeep_time):
    delaybeep_start_index = int(initial_delaybeep_time * WAV_SAMPLE_RATE)
    if b_has_initial_beep:
        try:
            music_data[delaybeep_start_index - len(delay_end_sfx):delaybeep_start_index] += delay_end_sfx[:, np.newaxis]
            music_data[:len(delay_start_sfx)] += delay_start_sfx[:, np.newaxis]
        except:
            # delay is too small. makes no sense to aks for such small delay, thus skipping delay-beep
            pass

    if b_has_rep_beeps:
        beep_indexes = np.linspace(delaybeep_start_index, len(music_data), number_of_beeps + 1, endpoint=True, dtype=int)[0:-1]
        for i in beep_indexes:
            music_data[i:i + len(rep_count_sfx)] += (rep_count_sfx[:, np.newaxis] * 1.7).astype(np.int16)
    return normalize_audio(music_data)


class MusicDispenser:
    music_file_iter: Iterator
    music_files_list: list

    current_signal_arr: Optional[np.ndarray] = None
    current_index_in_signal: int = 0

    def init_from_path_arr(self, paths: list[str]):
        self.music_files_list = []
        self.current_signal_arr: Optional[np.ndarray] = None
        self.current_index_in_signal: int = 0
        for p in paths:
            self.add_path_to_music_list(p)

    def init_from_path(self, path: str):
        self.music_files_list = []
        self.current_signal_arr: Optional[np.ndarray] = None
        self.current_index_in_signal: int = 0
        self.init_from_path_arr([path])

    def add_path_to_music_list(self, path):
        if not os.path.exists(path):
            raise Exception("path not found")
        if os.path.isdir(path):
            self.add_dir_to_music_list(path)
        else:
            self.add_file_to_music_list(path)

    def add_dir_to_music_list(self, dir_path: str):
        musics = os.listdir(dir_path)
        for p in pbar(musics):
            # check if file has already converted version
            p_name, _ = os.path.splitext(p)
            if p_name + f"_{WAV_SAMPLE_RATE}.wav" in musics:
                continue
            self.add_file_to_music_list(os.path.join(dir_path, p))

    def add_file_to_music_list(self, path: str):
        if f"_{WAV_SAMPLE_RATE}.wav" not in path:
            path = convert_file_to_wav(path)
        self.music_files_list.append(path)
        self.music_file_iter = itertools.cycle(self.music_files_list)

    def load_next_song_if_needed(self):
        while self.current_signal_arr is None or self.current_index_in_signal >= len(self.current_signal_arr):
            path = next(self.music_file_iter)
            a = wf.read(path)
            self.current_signal_arr = np.array(a[1], dtype=np.int16)
            self.current_signal_arr = normalize_audio(self.current_signal_arr)
            self.current_index_in_signal = 0

    def get_number_of_bins_left_to_end_of_song(self):
        self.load_next_song_if_needed()
        assert (self.current_signal_arr is not None)
        return len(self.current_signal_arr) - self.current_index_in_signal

    def get_music_signal(self, num_bins):
        self.load_next_song_if_needed()
        assert (self.current_signal_arr is not None)
        ret = self.current_signal_arr[self.current_index_in_signal:self.current_index_in_signal + num_bins]
        self.current_index_in_signal += num_bins
        if len(ret) < num_bins:
            # song ended midway
            ret2 = self.get_music_signal(num_bins - len(ret))
            ret = np.concatenate([ret, ret2])
        return ret

    def get_smooth_music_signal(self, num_bins, b_until_end_of_song):
        if b_until_end_of_song:
            num_bins = max(num_bins, self.get_number_of_bins_left_to_end_of_song())
        signal = self.get_music_signal(num_bins)
        # make paket
        paket = np.ones(signal.shape)
        num_bins_incline = int(WAV_SAMPLE_RATE * 0.1)
        num_bins_decline = int(WAV_SAMPLE_RATE * 0.4)
        paket[:num_bins_incline, :] = np.linspace(0, 1, num_bins_incline)[:, np.newaxis]
        paket[-num_bins_decline:, :] = np.linspace(1, 0, num_bins_decline)[:, np.newaxis]

        ret = (signal * paket).astype(np.int16)
        return ret
