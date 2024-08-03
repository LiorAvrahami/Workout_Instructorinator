from genericpath import isdir
import itertools
import os
from typing import Iterator, Optional
import warnings
import scipy.io.wavfile as wf
import numpy as np

WAV_SAMPLE_RATE = 44100
MUSIC_VOLUME_MULTIPLIER = 0.7
MASTER_VOLUME = 10000


def convert_file_to_wav(path):
    path_name, ext = os.path.splitext(path)
    os.system(f"ffmpeg -y -i \"{path}\" -ar {WAV_SAMPLE_RATE} \"{path_name}.wav\"")
    return f"{path_name}.wav"


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
    data[np.abs(data) > 2**14] = 2**14
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
    if b_has_initial_beep or b_has_rep_beeps:
        # first repetition beep is the same as delay end beep
        music_data[delaybeep_start_index:delaybeep_start_index + len(delay_end_sfx)] += delay_end_sfx[:, np.newaxis]
    if b_has_initial_beep:
        music_data[:+len(delay_start_sfx)] += delay_start_sfx[:, np.newaxis]
    if b_has_rep_beeps:
        beep_indexes = np.linspace(delaybeep_start_index, len(music_data), number_of_beeps + 1, endpoint=True, dtype=int)[1:-1]
        for i in beep_indexes:
            music_data[i:i + len(rep_count_sfx)] += rep_count_sfx[:, np.newaxis]
    return normalize_audio(music_data)


class MusicDispenser:
    music_file_iter: Iterator

    current_signal_arr: Optional[np.ndarray] = None
    current_index_in_signal: int = 0

    def init_from_path(self, path: str):
        if not os.path.exists(path):
            raise Exception("path not found")
        if os.path.isdir(path):
            self.__init_from_dir(path)
        else:
            self.__init_from_file(path)

    def __init_from_dir(self, path: str):
        musics = os.listdir(path)
        for p in musics:
            convert_file_to_wav(os.path.join(path, p))
        musics = [os.path.join(path, p) for p in os.listdir(path) if ".wav" in p]
        self.music_file_iter = itertools.cycle(musics)

    def __init_from_file(self, path: str):
        path = convert_file_to_wav(path)
        self.music_file_iter = itertools.cycle([path])

    def get_music_signal(self, num_bins):
        while self.current_signal_arr is None or self.current_index_in_signal >= len(self.current_signal_arr):
            path = next(self.music_file_iter)
            a = wf.read(path)
            self.current_signal_arr = np.array(a[1] * MUSIC_VOLUME_MULTIPLIER, dtype=np.int16)
            self.current_signal_arr = normalize_audio(self.current_signal_arr)
            self.current_index_in_signal = 0
        ret = self.current_signal_arr[self.current_index_in_signal:self.current_index_in_signal + num_bins]
        self.current_index_in_signal += num_bins
        if len(ret) < num_bins:
            # song ended midway
            ret2 = self.get_music_signal(num_bins - len(ret))
            ret = np.concatenate([ret, ret2])
        return ret

    def get_smooth_music_signal(self, num_bins):
        signal = self.get_music_signal(num_bins)
        # make paket
        paket = np.ones(signal.shape)
        num_bins_incline = int(WAV_SAMPLE_RATE * 0.1)
        num_bins_decline = int(WAV_SAMPLE_RATE * 0.4)
        paket[:num_bins_incline, :] = np.linspace(0, 1, num_bins_incline)[:, np.newaxis]
        paket[-num_bins_decline:, :] = np.linspace(1, 0, num_bins_decline)[:, np.newaxis]

        ret = (signal * paket).astype(np.int16)
        return ret
