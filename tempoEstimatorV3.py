import librosa
import beat as beat
import sounddevice as sd
from audioFilter import audioFilter
import matplotlib.pyplot as plt

audio_file = "Music+Beatmaps/Tourbillon.mp3"
y, sr = librosa.load(audio_file)
y = audioFilter(y=y, sr=sr)
# Detect the beats
beats = beat.detect_combi_beats(y, sr)




# Generate clicks at these change points
#clicks = librosa.clicks(times=beats, sr=sr, length=len(y))
#
## Combine the original audio with the clicks
#y_with_clicks = y + clicks
#
## Play the combined audio
#sd.play(y_with_clicks, sr)
#
#sd.wait()

