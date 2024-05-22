import librosa
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from librosaModified import tempo

audio_file = "Music+Beatmaps/nATALIE.mp3"
y, sr = librosa.load(audio_file)
y = librosa.effects.percussive(y=y, margin=6)

## Clicks with audio
#click_dynamic = librosa.clicks(times=beats_dynamic, sr=sr, click_freq=660,
#                               click_duration=0.25, length=len(y))
#
## Combine the original audio with the clicks
#y_with_clicks = y + click_dynamic

## Play the combined audio
#sd.play(y_with_clicks, sr)
#
## For accurate beat identification, show areas which bpm can change, then have the user choose from the lines on the tempogram which are most suited
## to do in the future
## TEMPOGRAM
#tempogram = librosa.feature.tempogram(
#    onset_envelope=oenv,
#    sr=sr, 
#    hop_length=512, 
#    win_length=384
#)
#
#plt.figure(figsize=(10, 5))
#librosa.display.specshow(tempogram, x_axis='time', y_axis='tempo')
#plt.xlabel('Time (sec)')
#plt.show()
#
#sd.wait()

def tempoEstimate(song):
    """
    dynamic tempo estimate of music 
    ### Parameters:
    tuple (y, sr)
    ### Returns:
    An array of tempo estimates along the time
    """
    y, sr = song
    oenv = librosa.onset.onset_strength(y=y, sr=sr)

    tempo_dynamic = tempo(onset_envelope=oenv, sr=sr, std_bpm=2)
    #print(tempo_dynamic)
    _, beats_dynamic = librosa.beat.beat_track(y=y, sr=sr, units='time',
                                               bpm=tempo_dynamic, trim=False)
    return beats_dynamic

res = tempoEstimate((y,sr))

#fig, ax = plt.subplots()
#times = librosa.times_like(res, sr=sr)
#ax.plot(times, res, label='Dynamic tempo estimate')
#ax.legend()
#ax.set(xlabel='Time (s)', ylabel='Tempo (BPM)')

# Clicks with audio
click_dynamic = librosa.clicks(times=res, sr=sr, click_freq=660,
                               click_duration=0.25, length=len(y))

# Combine the original audio with the clicks
y_with_clicks = y + click_dynamic
# Play the combined audio
sd.play(y_with_clicks, sr)
plt.show()
status = sd.wait()