from genericpath import isdir
import itertools
import os
from typing import Iterator, Optional
import scipy.io.wavfile as wf
import numpy as np

WAV_SAMPLE_RATE = 44100

def convert_file_to_wav(path):
    path_name, ext = os.path.splitext(path)
    os.system(f"ffmpeg -y -i \"{path}\" -ar {WAV_SAMPLE_RATE} \"{path_name}.wav\"")
    return f"{path_name}.wav"


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
            convert_file_to_wav(os.path.join(path,p))
        musics = [os.path.join(path,p) for p in os.listdir(path) if ".wav" in p]
        self.music_file_iter = itertools.cycle(musics)

    def __init_from_file(self, path: str):
        path = convert_file_to_wav(path)
        self.music_file_iter = itertools.cycle([path])

    def get_music_signal(self, num_bins):
        while self.current_signal_arr is None or self.current_index_in_signal >= len(self.current_signal_arr):
            path = next(self.music_file_iter)
            a = wf.read(path)
            self.current_signal_arr = np.array(a[1], dtype=np.int16)
            self.current_index_in_signal = 0
        ret = self.current_signal_arr[self.current_index_in_signal:self.current_index_in_signal + num_bins]
        self.current_index_in_signal += num_bins
        # make paket
        paket = np.ones(ret.shape)
        num_bins_incline = int(WAV_SAMPLE_RATE * 0.1)
        num_bins_decline = int(WAV_SAMPLE_RATE * 0.4)
        paket[:num_bins_incline,:] = np.linspace(0, 1, num_bins_incline)[:,np.newaxis]
        paket[-num_bins_decline:,:] = np.linspace(1, 0, num_bins_decline)[:,np.newaxis]

        ret = (ret * paket).astype(np.int16)
        return ret
