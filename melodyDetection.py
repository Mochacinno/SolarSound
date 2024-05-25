import librosa
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from utils import audioFilter
import scipy.signal as signal
from scipy import interpolate

# Load the audio file
y, sr = librosa.load("music.mp3", duration=100)

#Band pass filter
lowcut = 20.0  # Low cutoff frequency, Hz
highcut = 8000.0  # High cutoff frequency, Hz
order = 4  # Filter order

# Normalize the frequencies by the Nyquist frequency (sr / 2)
nyquist = 0.5 * sr
low = lowcut / nyquist
high = highcut / nyquist

# Create the filter coefficients
b, a = signal.butter(order, [low, high], btype='band')

# Apply the filter to the signal
y_harmonic = signal.filtfilt(b, a, y)

y_harmonic = audioFilter(y_harmonic, sr)
#y_harmonic = librosa.effects.harmonic(y=y_harmonic)

# Extract the fundamental frequency (f0) using the harmonic component
f0 = librosa.yin(y_harmonic, sr=sr, fmin=librosa.note_to_hz('C4'), fmax=librosa.note_to_hz('C7'))
times = librosa.times_like(f0, sr=sr)

# Convert f0 to MIDI note numbers, NaN values are replaced with -1
midi_notes = librosa.hz_to_midi(f0)
midi_notes = np.nan_to_num(midi_notes, nan=-1)

# Find indices of NaN values in midi_notes
nan_indices = np.where(midi_notes == -1)[0]
print(midi_notes)

# Create a function for nearest neighbor interpolation
interp_func_nearest = interpolate.interp1d(np.arange(len(midi_notes))[midi_notes != -1], 
                                           midi_notes[midi_notes != -1], 
                                           kind='nearest', 
                                           fill_value='extrapolate')

# Interpolate NaN values with nearest neighbor
midi_notes_nearest = midi_notes.copy()
midi_notes_nearest[nan_indices] = interp_func_nearest(nan_indices)
print(midi_notes_nearest)
# Detect changes in MIDI note values within the specified range
change_points = np.where(np.abs(np.diff(midi_notes_nearest)) >= 5)[0]
change_times = times[change_points]

# Plot the results
D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
fig, ax = plt.subplots()
img = librosa.display.specshow(D, x_axis='time', y_axis='log', ax=ax)
ax.set(title='Pitch Detection and Change Points')
fig.colorbar(img, ax=ax, format="%+2.f dB")
plt.plot(times, f0, label='f0', color='cyan')
plt.vlines(change_times, ymin=f0.min(), ymax=f0.max(), color='red', alpha=0.5, linestyle='--', label='Pitch Change Points')
#plt.legend()

# Generate clicks at these change points
clicks = librosa.clicks(times=change_times, sr=sr, length=len(y_harmonic))

# Combine the original audio with the clicks
y_with_clicks = y_harmonic + clicks

# Play the combined audio
sd.play(y_with_clicks, sr)
plt.show()
# Print the times when the pitch changes
#print("Pitch changes at times (in seconds):", change_times)

# Play the isolated harmonic component (melody)
sd.wait()