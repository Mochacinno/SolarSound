import librosa
import librosa.display
import matplotlib.pyplot as plt
import sounddevice as sd
import scipy.signal as signal 
from utils import audioFilter
import numpy as np

# Load the audio file
audio_file = "Music+Beatmaps/tabiji.mp3"
y, sr = librosa.load(audio_file)

## SLICE THE MUSIC
# Define start and end times in seconds
start_time = 76  # Start at 5 seconds
end_time = 120   # End at 10 seconds

# Convert start and end times to sample indices
start_sample = int(start_time * sr)
end_sample = int(end_time * sr)

# Slice the y array
y = y[start_sample:end_sample]

# # Decomposition
# D = librosa.stft(y)
# H, P = librosa.decompose.hpss(D, margin=2.0)
# R = D - (H+P)
# y_harm = librosa.istft(H)
# y_perc = librosa.istft(P)
# y_resi = librosa.istft(R)
y = audioFilter(y, sr)
#y = y_harm

def onsetDetect(y, sr, hop_len):
    # Compute the onset envelope
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length = hop_len)
    
    # Detect onsets
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

    # For example, to compute the tempo:
    #tempo, beats_static = librosa.beat.beat_track(y=y, sr=sr, units='time', trim=True)
    return onsets


# onsets = onsetDetect(y, sr, 512)
# onsets2 = onsetDetect(y, sr*8, 64)

# # Plot the audio signal
# plt.figure(figsize=(12, 6))
# librosa.display.waveshow(y, sr=sr, alpha=0.5)  # Plot the original audio signal

# # Generate the click track
# click_track = librosa.clicks(times=onsets, sr=sr, click_freq=660,
#                              click_duration=0.25, length=len(y))

# # Generate the click track
# click_track2 = librosa.clicks(times=onsets2, sr=sr, click_freq=660,
#                              click_duration=0.25, length=len(y))

# # Combine the audio signal with the click track
# combined_audio = y + click_track2


# # Play the combined audio using sounddevice
# sd.play(combined_audio, sr)

# # Plot onsets as vertical lines
# plt.vlines(onsets, ymin=-1, ymax=1, color='g', alpha=0.7, linestyle='-', label='Onsets 512')

# plt.vlines(onsets2, ymin=-1, ymax=1, color='r', alpha=0.7, linestyle='--', label='Onsets 64')

# Superflux
n_fft = 1024
hop_length = int(librosa.time_to_samples(1./200, sr=sr))
lag = 2
n_mels = 138
fmin = 27.5
fmax = 16000.
max_size = 3

S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=n_fft,
                                   hop_length=hop_length,
                                   fmin=fmin,
                                   fmax=fmax,
                                   n_mels=n_mels)

odf_sf = librosa.onset.onset_strength(S=librosa.power_to_db(S, ref=np.max),
                                      sr=sr,
                                      hop_length=hop_length,
                                      lag=lag, max_size=max_size)

onset_sf = librosa.onset.onset_detect(onset_envelope=odf_sf,
                                      sr=sr,
                                      hop_length=hop_length,
                                      units='time')


frame_time = librosa.frames_to_time(np.arange(len(odf_sf)),
                                    sr=sr,
                                    hop_length=hop_length)



o_env = librosa.onset.onset_strength(y=y, sr=sr*8, hop_length = 64)
times = librosa.times_like(o_env, sr=sr*8)
onset_times = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr*8, units='time')
click_track = librosa.clicks(times=onset_sf, sr=sr, click_freq=660, click_duration=0.1, length=len(y))

combined_audio = y + click_track

## Resample the audio to the new sample rate
#combined_slow = librosa.resample(combined_audio, sr, sr/2)


sd.play(combined_audio, sr/2)

plt.plot(frame_time, odf_sf, label='Onset strength')

plt.vlines(onset_sf, 0, odf_sf.max(), color='r', alpha=0.9,
           linestyle='--', label='Onsets superflux')

plt.vlines(onset_times, 0, o_env.max(), color='b', alpha=0.9,
           linestyle='--', label='Onsets')

# plt.xlabel('Time (s)')
# plt.ylabel('Amplitude')
# plt.title('Audio Signal with Onsets')
plt.legend()
plt.show()

# Wait for the audio to finish playing
status = sd.wait()