import librosa
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

y, sr = librosa.load("sink.mp3", duration=100)

# Define start and end times in seconds
start_time = 76  # Start at 5 seconds
end_time = 96   # End at 10 seconds

# Convert start and end times to sample indices
start_sample = int(start_time * sr)
end_sample = int(end_time * sr)

# Slice the y array
y = y[start_sample:end_sample]

# BINS_PER_OCTAVE = 12 * 3
# N_OCTAVES = 7
# C = librosa.amplitude_to_db(np.abs(librosa.cqt(y=y, sr=sr,
#                                         bins_per_octave=BINS_PER_OCTAVE,
#                                         n_bins=N_OCTAVES * BINS_PER_OCTAVE)),
#                             ref=np.max)

# tempo, beats = librosa.beat.beat_track(y=y, sr=sr, trim=False)
# Csync = librosa.util.sync(C, beats, aggregate=np.median)


# # For plotting purposes, we'll need the timing of the beats
# # we fix_frames to include non-beat frames 0 and C.shape[1] (final frame)
# beat_times = librosa.frames_to_time(librosa.util.fix_frames(beats,
#                                                             x_min=0),
#                                     sr=sr)

# fig, ax = plt.subplots()
# librosa.display.specshow(Csync, bins_per_octave=12*3,
#                          y_axis='cqt_hz', x_axis='time',
#                          x_coords=beat_times, ax=ax)
# plt.show()

f0, voiced_flag, voiced_probs = librosa.pyin(y,
                                             sr=sr,
                                             fmin=librosa.note_to_hz('C2'),
                                             fmax=librosa.note_to_hz('C7'))
times = librosa.times_like(f0, sr=sr)

D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
fig, ax = plt.subplots()
img = librosa.display.specshow(D, x_axis='time', y_axis='log', ax=ax)
ax.set(title='pYIN fundamental frequency estimation')
fig.colorbar(img, ax=ax, format="%+2.f dB")

times = librosa.times_like(f0, sr=sr)

# Convert f0 to MIDI note numbers, NaN values are replaced with -1
midi_notes = librosa.hz_to_midi(f0)
midi_notes = np.nan_to_num(midi_notes, nan=-1)

# Detect changes in MIDI note values
change_points = np.where(np.diff(midi_notes, prepend=midi_notes[0]) != 0)[0]
change_times = times[change_points]

# Generate clicks at these change points
clicks = librosa.clicks(times=change_times, sr=sr, length=len(y))

# Combine the original audio with the clicks
y_with_clicks = y + clicks

# Play the combined audio
sd.play(y_with_clicks, sr)

ax.plot(times, f0, label='f0', color='cyan', linewidth=3)
ax.legend(loc='upper right')
plt.show()

status = sd.wait()

