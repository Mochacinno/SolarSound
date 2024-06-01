import librosa
import numpy as np
import matplotlib.pyplot as plt

def smooth_rms(rms, window_size=5):
    """Smooth the RMS values using a simple moving average."""
    return np.convolve(rms, np.ones(window_size)/window_size, mode='same')

song_name = "tourbillon.ogg"
y, sr = librosa.load("Music+Beatmaps/"+song_name)
## SLICE THE MUSIC
# Define start and end times in seconds
start_time = 0  # Start at 5 seconds
end_time = 120   # End at 10 seconds

# Convert start and end times to sample indices
start_sample = int(start_time * sr)
end_sample = int(end_time * sr)

# Slice the y array
y = y[start_sample:end_sample]

# Compute RMS values
rms = librosa.feature.rms(y=y)[0]

# Smooth the RMS values
smoothed_rms = smooth_rms(rms, window_size=20)  # Adjust the window size as needed

# Compute the time for each RMS value
frames = range(len(rms))
t = librosa.frames_to_time(frames, sr=sr)

# Determine a threshold for high RMS values
mean_rms = np.mean(smoothed_rms)
std_rms = np.std(smoothed_rms)
threshold = mean_rms - 0.5 * std_rms  # You can adjust the multiplier based on your requirements
print(threshold)

# Identify high RMS sections
high_rms_indices = np.where(smoothed_rms > threshold)[0]

# Group consecutive indices into sections
sections = np.split(high_rms_indices, np.where(np.diff(high_rms_indices) != 1)[0] + 1)

# Convert frame indices to time
high_rms_sections = [(librosa.frames_to_time(section[0], sr=sr), 
                      librosa.frames_to_time(section[-1], sr=sr)) for section in sections if len(section) > 0]

print(high_rms_sections)

# Merge close sections to form larger segments if they are within a short duration
merged_sections = []
min_gap_duration = 0.5  # Minimum gap duration in seconds to consider sections separate
for start, end in high_rms_sections:
    if not merged_sections or start - merged_sections[-1][1] > min_gap_duration:
        merged_sections.append((start, end))
    else:
        merged_sections[-1] = (merged_sections[-1][0], end)



# Print high RMS sections
print("High RMS sections (in seconds):")
for start, end in merged_sections:
    print(f"Start: {start:.2f}, End: {end:.2f}")

# Plot the RMS values and highlight high RMS sections
plt.figure(figsize=(14, 6))
plt.plot(t, rms, label='RMS')
plt.plot(t, smoothed_rms, label='Smoothed RMS', alpha=0.75)
for start, end in merged_sections:
    plt.axvspan(start, end, color='red', alpha=0.3)
plt.xlabel('Time (s)')
plt.ylabel('RMS')
plt.title('RMS Values with High RMS Sections Highlighted')
plt.legend()
plt.show()