import librosa
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
from pydub import AudioSegment
import sounddevice as sd

# Load the audio file 1 which is not
audio_file = "nATALIECUT2.mp3"

# Load the audio signal
y, sr = librosa.load(audio_file)
y_perc = librosa.effects.harmonic(y=y, margin=1)

# For example, to compute the tempo:
tempo, beats_static = librosa.beat.beat_track(y=y_perc, sr=sr, units='time', trim=True)

# Generate the click track
click_track = librosa.clicks(times=beats_static, sr=sr, click_freq=660,
                             click_duration=0.25, length=len(y))

# Combine the audio signal with the click track
combined_audio = y_perc + click_track

# Play the combined audio using sounddevice
sd.play(combined_audio, sr)

# Wait for the audio to finish playing
status = sd.wait()

# Load the audio file 1 which is not
#audio_file = "nATALIECUT2.mp3"
#y, sr = librosa.load(audio_file)

#y_percussive = librosa.effects.harmonic(y)
#tempo, beats = librosa.beat.beat_track(y=y, sr=sr, start_bpm=100)
#oenv = librosa.onset.onset_detect(y=y, sr=sr, units='time')

#print(tempo)

# Load the audio file 2 which is correct
#audio_file = "test.mp3"
#y, sr = librosa.load(audio_file)
#
#tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
#
#print(tempo)


#hop_length = 512
#oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
#tempogram = librosa.feature.tempogram(onset_envelope=oenv, sr=sr, hop_length=hop_length)

#librosa.display.specshow(tempogram, sr=sr, hop_length=hop_length, x_axis='time', y_axis='tempo', cmap='magma')

#fig, ax = plt.subplots()
#times = librosa.times_like(oenv, sr=sr, hop_length=hop_length)
#ax.plot(times, oenv, label='Onset strength')
#
#ax.set(title='Tempogram')

#D = np.abs(librosa.stft(y))
#fig, ax = plt.subplots(nrows=2, sharex=True)
#librosa.display.specshow(librosa.amplitude_to_db(D, ref=np.max),
#                         x_axis='time', y_axis='log', ax=ax[0])
#ax[0].set(title='Power spectrogram')
#ax[0].label_outer()
#ax[1].vlines(oenv, 0, oenv.max(), color='r', alpha=0.9,
#           linestyle='--', label='Onsets')
#ax[1].legend()
#
#
#plt.show()