import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio
import sounddevice as sd
import librosa
import scipy.signal as signal

y, sr = librosa.load("sink.mp3", duration=120)


onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length = 512)


# Define a threshold for significant onsets
threshold = np.mean(onset_env) + np.std(onset_env)  # Example threshold

# Find peaks above the threshold
peaks, _ = signal.find_peaks(onset_env, height=threshold)

# Get the times of the significant onsets
onsets = librosa.frames_to_time(peaks, sr=sr)


# Detect onsets
#onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

# Generate the click track
click_track = librosa.clicks(times=onsets, sr=sr, click_freq=660,
                             click_duration=0.25, length=len(y))

# Combine the audio signal with the click track
combined_audio = y + click_track


sd.play(combined_audio, sr)
status = sd.wait()