import librosa
import librosa.display
import matplotlib.pyplot as plt
import sounddevice as sd

# Load the audio file
audio_file = "nATALIE.mp3"
y, sr = librosa.load(audio_file)

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

""" # Kill everything above the max tempo
    if max_tempo is not None:
        max_idx = int(np.argmax(bpms < max_tempo))
        logprior[:max_idx] = -np.inf

    # explicit axis expansion
    logprior = util.expand_to(logprior, ndim=tg.ndim, axes=-2)
    
    # Get the maximum, weighted by the prior
    # Using log1p here for numerical stability
    tempo_est = []
    print("TOP 3 TEMPOS:")
    for i in range(3):
        best_period = np.argmax(np.log1p(1e6 * tg) + logprior, axis=-2)
        tempo_est.append(np.take(bpms, best_period))
        print(f"tempo: {np.take(bpms, best_period)}, with a weight of: {logprior[best_period]}")
        logprior[best_period] = -np.inf
    
    return tempo_est[0] """