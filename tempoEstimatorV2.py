import librosa
import numpy as np
import matplotlib.pyplot as plt
from utils import tempo
import utils

# Load the audio file
y, sr = librosa.load("Music+Beatmaps/nhelv.mp3")
hop_length = 512


# Compute the onset envelope
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

# Compute the tempogram
tempogram = librosa.feature.tempogram(onset_envelope=oenv, sr=sr, hop_length=hop_length)


# Estimate the tempo using the custom function
tempo_estimates = utils.song_tempo_estimate((y,sr))
#print(tempo_estimates)

# Round the tempos to the nearest integer for counting
rounded_tempos = np.round(tempo_estimates).astype(int)

# Count the occurrences of each tempo
tempos = np.unique(rounded_tempos, return_counts=True) # array of [unique tempos], [number of occurences for each unique tempo])

# # Calculate the percentage of each tempo
# total_counts = np.sum(counts)
# percentages = (counts / total_counts) * 100

# # Plot the tempogram
# plt.figure(figsize=(14, 8))
# librosa.display.specshow(tempogram, sr=sr, hop_length=hop_length,
#                          x_axis='time', y_axis='tempo', cmap='magma')

# Plot the percentages as a bar chart
plt.figure(figsize=(14, 8))
plt.bar(tempos[0], tempos[1], color='blue')
plt.xlabel('Tempo (BPM)')
plt.ylabel('Percentage (%)')
plt.title('Percentage of Tempo Occurrences')
plt.show()

# # Print the tempo percentages for reference
# for tempo, percentage in zip(unique_tempos, percentages):
#     print(f'Tempo: {tempo} BPM, Percentage: {percentage:.2f}%')

def is_close(a, b, tol):
        return abs(a - b) <= tol

def find_best_tempo(group, tolerance):
    def combined_occurrences(tempo, group, tolerance):
        half = [t for t in group if is_close(tempo / 2, t[0], tolerance)]
        two_thirds = [t for t in group if is_close(tempo * 2 / 3, t[0], tolerance) or is_close(tempo / 3, t[0], tolerance)]
        return sum(t[1] for t in half + two_thirds)

    best_tempo = None
    highest_combined_occurrences = 0

    for tempo, occurrences in group:
        combined = occurrences + combined_occurrences(tempo, group, tolerance)
        if combined > highest_combined_occurrences:
            highest_combined_occurrences = combined
            best_tempo = tempo

    return best_tempo if best_tempo is not None else max(group, key=lambda t: t[1])[0]  # Fallback to highest occurrence if no suitable tempo found

def group_tempos_by_factors(tempos, factors=[2, 2/3], tolerance=5):

    def in_used(tempo, used, tol):
        return any(is_close(tempo, u, tol) for u in used)

    def find_related(tempo, all_tempos, used, factors, tolerance):
        related_group = [tempo]
        to_check = [tempo]

        while to_check:
            current = to_check.pop()
            for factor in factors:
                for related in (current[0] * factor, current[0] / factor):
                    for t in all_tempos:
                        if not in_used(t[0], used, tolerance) and is_close(t[0], related, tolerance):
                            related_group.append(t)
                            used.add(t[0])
                            to_check.append(t)
        return related_group

    # Combine tempos and occurrences into a single list of tuples
    all_tempos = list(zip(tempos[0], tempos[1]))

    grouped_tempos = []
    used = set()

    for tempo in all_tempos:
        if in_used(tempo[0], used, tolerance):
            continue
        group = find_related(tempo, all_tempos, used, factors, tolerance)
        grouped_tempos.append(group)

    # Find the group with the highest total occurrences
    max_group = max(grouped_tempos, key=lambda g: sum(t[1] for t in g))

    # Find the best tempo within the group
    best_tempo = find_best_tempo(max_group, tolerance)

    return best_tempo

# Group detected peaks by common factors
best_tempo = group_tempos_by_factors(tempos)
print(best_tempo)

#print(groups)
# # Determine the true tempo based on grouped peaks
# def determine_true_tempo(groups, unique_tempos, percentages):
#     best_group = max(groups, key=lambda group: np.sum([percentages[np.where(unique_tempos == tempo)[0][0]] for tempo in group]))
#     return np.mean(best_group)

# true_tempo = determine_true_tempo(groups, unique_tempos, percentages)

# # Print the tempo percentages for reference
# print("Detected Tempos and Their Percentages:")
# for tempo, percentage in zip(unique_tempos, percentages):
#     print(f'Tempo: {tempo} BPM, Percentage: {percentage:.2f}%')

# # Print the true tempo
# print(f'\nTrue Tempo: {true_tempo:.2f} BPM')