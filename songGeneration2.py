import librosa
import matplotlib.pyplot as plt
import numpy as np
import math
import scipy.signal as signal 
from audioFilter import audioFilter
from pitchDetection import pitchDetection

song = "nATALIECUT2.mp3"
y, sr = librosa.load(song)
# #y = librosa.effects.percussive(y=y)

# # Band pass filter
# lowcut = 200.0  # Low cutoff frequency, Hz
# highcut = 500.0  # High cutoff frequency, Hz
# order = 4  # Filter order

# # Normalize the frequencies by the Nyquist frequency (sr / 2)
# nyquist = 0.5 * sr
# low = lowcut / nyquist
# high = highcut / nyquist

# # Create the filter coefficients
# b, a = signal.butter(order, [low, high], btype='band')

# # Apply the filter to the signal
# y = signal.filtfilt(b, a, y)

# stream_coeff = 1
# chord_coeff = 0

"""
# Plot the audio signal
plt.figure(figsize=(12, 6))

librosa.display.waveshow(y, sr=sr, alpha=0.5)  # Plot the original audio signal

# Plot onsets as vertical lines
plt.vlines(librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, units='time'), ymin=-1, ymax=1, color='g', alpha=0.8, linestyle='-', label='Onsets env')

plt.show()
"""
y_filter = audioFilter(y, sr)
hop_length = 512
oenv = librosa.onset.onset_strength(y=y_filter, sr=sr, hop_length=hop_length)
onset_times = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, units='time')

#print(onset_times)

#greatest common divisor
def find_interval(numbers):
    if len(numbers) == 1:
        numbers.append(0.10)
    print(numbers)
    intervals = [int(number * 100) for number in numbers]
    gcd = np.gcd.reduce(intervals) / 100
    #print(gcd)
    return gcd

def generate_groups(onset_times):
    beatmap = []
    groups = []
    window = 0
    beats = []
    onset_times = np.round(onset_times, 2)
    index_onset = 0
    while index_onset < len(onset_times):
        if window <= onset_times[index_onset] <  window+1:
            beats.append(round(onset_times[index_onset] % 1, 2))  # Round onset time to one decimal place
            beats_filled = False
        else:
            #window += 1
            beats_filled = True
            index_onset -= 1
        
        if beats_filled or index_onset == len(onset_times) - 1:
            if len(beats) != 0:
                interval = find_interval(beats)
                interval = round(interval, 2)  # Round interval to one decimal place
            else:
                interval = 0.25
            slot = 0
            while slot <= 1:
                if slot in beats:
                    group = np.zeros(4, dtype=int)
                    idx = np.random.randint(0, 4)
                    group[idx] = 1
                    groups.append(group)
                else:
                    group = np.zeros(4, dtype=int)
                    groups.append(group)
                slot = round(slot + interval, 2)
            beats = []
            beatmap.append(groups)
            groups = []
            window += 1

        index_onset += 1

    return beatmap


# Generate groups based on onset times
#beatmap = generate_groups(onset_times)

# Generate groups based on pitch changes
#y_filter = audioFilter(y, sr)
#beat_timing = pitchDetection(y_filter, sr)


beatmap = generate_groups(onset_times)
#print(len(beatmap))

# Format groups into text content
text_content = ""
for groups in beatmap:
    #text_content += ",\n"  # Add comma and newline after every 4 groups
    for group in groups:
        text_content += ''.join(map(str, group))  # Convert group to string and append to text content
        text_content += "\n"
    text_content += ",\n"


# Write text content to a file
output_file = "onset_times.txt"
with open(output_file, 'w') as file:
    file.write(text_content)

print(f"Text file '{output_file}' generated successfully.")