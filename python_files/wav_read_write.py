import scipy.io.wavfile as wf
# import soundfile as wf


def read(filepath):
    a, b = wf.read(filepath)
    # return b,a
    return a, b


def write(filepath, sample_rate, audio_data):
    # wf.write(file=filepath, data=audio_data, samplerate=sample_rate)
    wf.write(filename=filepath, data=audio_data, rate=sample_rate)
