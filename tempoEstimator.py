import librosa
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from librosaModified import tempo

#audio_file = "Music+Beatmaps/nATALIECUT2.mp3"
#y, sr = librosa.load(audio_file)
#y = librosa.effects.percussive(y=y, margin=6)

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
    #_, beats_dynamic = librosa.beat.beat_track(y=y, sr=sr, units='time',
    #                                           bpm=tempo_dynamic, trim=False)
    return tempo_dynamic

#res = tempoEstimate((y,sr))

## Plotting dynamic tempo estimate
#fig, ax = plt.subplots()
#times = librosa.times_like(res, sr=sr)
#ax.plot(times, res, label='Dynamic tempo estimate')
#ax.legend()
#ax.set(xlabel='Time (s)', ylabel='Tempo (BPM)')
#plt.show()




def bpm_to_intervals(bpm_array, sr):
    # Convert BPM to intervals in seconds
    intervals = 60.0 / bpm_array
    frame_intervals = intervals * sr / 512
    return frame_intervals

def intervals_to_times(intervals, sr, hop_length):
    # Convert intervals to time stamps
    times = []
    current_time = 0.0
    
    for interval in intervals:
        times.append(current_time)
        current_time += interval * hop_length / sr
    
    return np.array(times)

## Convert BPM to intervals
#intervals = bpm_to_intervals(res, sr)
#
## Convert intervals to times
#times = intervals_to_times(intervals, sr, hop_length=512)
#
## Generate click track
#click_track = librosa.clicks(times=times, sr=sr, click_freq=660, click_duration=0.1, length=len(y))
#
## Merge click track with original audio
#mixed_audio = y + click_track
#sd.play(mixed_audio, sr)
#status = sd.wait()
#
# Clicks with audio
#click_dynamic = librosa.clicks(times=res, sr=sr, click_freq=660,
#                               click_duration=0.25, length=len(y))
#
## Combine the original audio with the clicks
#y_with_clicks = y + click_dynamic
## Play the combined audio
#sd.play(y_with_clicks, sr)
#status = sd.wait()