import librosa
import librosa.display
import matplotlib.pyplot as plt
import sounddevice as sd
import scipy.signal as signal 

# Load the audio file
audio_file = "sink.mp3"
y, sr = librosa.load(audio_file)

D = librosa.stft(y)
H, P = librosa.decompose.hpss(D, margin=1.0)
R = D - (H+P)
y_harm = librosa.istft(H)
y_perc = librosa.istft(P)
y_resi = librosa.istft(R)
y = y_harm

# Compute the onset envelope
onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length = 512)

# Detect onsets
onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

# For example, to compute the tempo:
tempo, beats_static = librosa.beat.beat_track(y=y, sr=sr, units='time', trim=True)

# Plot the audio signal
plt.figure(figsize=(12, 6))
librosa.display.waveshow(y, sr=sr, alpha=0.5)  # Plot the original audio signal

# Generate the click track
click_track = librosa.clicks(times=onsets, sr=sr, click_freq=660,
                             click_duration=0.25, length=len(y))

# Combine the audio signal with the click track
combined_audio = y + click_track


# Play the combined audio using sounddevice
sd.play(combined_audio, sr)

# Plot onsets as vertical lines
plt.vlines(onsets, ymin=-1, ymax=1, color='g', alpha=0.7, linestyle='-', label='Onsets')

plt.vlines(beats_static, ymin=-1, ymax=1, color='r', alpha=0.7, linestyle='--', label='Beats')  # Plot beats as vertical lines


plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Audio Signal with Onsets')
plt.legend()
plt.show()

# Wait for the audio to finish playing
status = sd.wait()