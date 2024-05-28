import librosa
import numpy as np
import matplotlib.pyplot as plt
from utils import tempo
import tempoEstimator

# Load the audio file
y, sr = librosa.load("Music+Beatmaps/sink.mp3")
hop_length = 512

# Compute the onset envelope
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

# Compute the tempogram
tempogram = librosa.feature.tempogram(onset_envelope=oenv, sr=sr, hop_length=hop_length)

# Estimate the tempo using the custom function
tempo_estimates = tempoEstimator.tempoEstimate((y,sr))

print(tempo_estimates)

# Round the tempos to the nearest integer for counting
rounded_tempos = np.round(tempo_estimates).astype(int)

# Count the occurrences of each tempo
unique_tempos, counts = np.unique(rounded_tempos, return_counts=True)

# Calculate the percentage of each tempo
total_counts = np.sum(counts)
percentages = (counts / total_counts) * 100

# Plot the tempogram
plt.figure(figsize=(14, 8))
librosa.display.specshow(tempogram, sr=sr, hop_length=hop_length,
                         x_axis='time', y_axis='tempo', cmap='magma')

# Plot the percentages as a bar chart
plt.figure(figsize=(14, 8))
plt.bar(unique_tempos, percentages, color='blue')
plt.xlabel('Tempo (BPM)')
plt.ylabel('Percentage (%)')
plt.title('Percentage of Tempo Occurrences')
plt.show()

# Print the tempo percentages for reference
for tempo, percentage in zip(unique_tempos, percentages):
    print(f'Tempo: {tempo} BPM, Percentage: {percentage:.2f}%')

# Identify groups of tempos related by common factors
def group_tempos_by_factors(tempos, factors=[0.5, 2, 2/3]):
    groups = []
    used = set()
    for i in range(len(tempos)):
        if tempos[i] in used:
            continue
        group = [tempos[i]]
        for factor in factors:
            related_tempo = tempos[i] * factor
            if related_tempo in tempos and related_tempo not in used:
                group.append(related_tempo)
                used.add(related_tempo)
            related_tempo = tempos[i] / factor
            if related_tempo in tempos and related_tempo not in used:
                group.append(related_tempo)
                used.add(related_tempo)
        groups.append(group)
    return groups

# Group detected peaks by common factors
peak_tempos = unique_tempos[peaks]
peak_percentages = percentages[peaks]
groups = group_tempos_by_factors(peak_tempos)

# Determine the true tempo based on grouped peaks
def determine_true_tempo(groups, unique_tempos, percentages):
    best_group = max(groups, key=lambda group: np.sum([percentages[np.where(unique_tempos == tempo)[0][0]] for tempo in group]))
    return np.mean(best_group)

true_tempo = determine_true_tempo(groups, unique_tempos, percentages)

# Print the tempo percentages for reference
print("Detected Tempos and Their Percentages:")
for tempo, percentage in zip(unique_tempos, percentages):
    print(f'Tempo: {tempo} BPM, Percentage: {percentage:.2f}%')

# Print the true tempo
print(f'\nTrue Tempo: {true_tempo:.2f} BPM')