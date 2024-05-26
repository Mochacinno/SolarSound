import librosa
import matplotlib.pyplot as plt
import numpy as np

# calculate room mean square energy
# separate file if needed

def calculate_rms(y, sr):
    # Calculate RMS
    rms = librosa.feature.rms(y=y)
    
    # Create a time array in seconds
    times = librosa.times_like(rms, sr=sr)

    return times, rms[0]

def plot_rms(times, rms):
    plt.figure(figsize=(14, 6))
    plt.plot(times, rms, label='RMS Energy', color='b')
    plt.xlabel('Time (s)')
    plt.ylabel('RMS Energy')
    plt.title('RMS Energy over Time')
    plt.legend(loc='upper right')
    plt.show()

def normalize_rms(rms):
    normalized_rms = (rms - np.min(rms)) / (np.max(rms) - np.min(rms))
    return normalized_rms

# Example usage:

# Load audio file
y, sr = librosa.load("Music+Beatmaps/sink.mp3")                                                                 

# Calculate RMS
times, rms = calculate_rms(y, sr)
normalized_rms = normalize_rms(rms)
# Plot RMS
plot_rms(times, normalized_rms)