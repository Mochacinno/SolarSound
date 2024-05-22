import librosa
import matplotlib.pyplot as plt
import numpy as np
import tempoEstimator

song = "Music+Beatmaps/nATALIECUT2.mp3"
y, sr = librosa.load(song)

# add instead a time delay before spawning the notes instead of just spawning 0s every 0.1 seconds

#y_filter = audioFilter(y, sr)
hop_length = 512
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
onset_times = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, units='time')

def bpm_to_intervals(bpm_array):
    # the bpm-array is the bpm at each frame, so these are the intervals for that given moment to the frame
    intervals = 60.0 / bpm_array  # Convert BPM to intervals in seconds
    return intervals

def bpm_per_second(bpm_per_frame, sr, hop_length):

    # Calculate the number of frames per second
    frames_per_second = sr // hop_length

    # Number of seconds in the audio
    num_seconds = len(bpm_per_frame) // frames_per_second
    print(num_seconds)
    
    bpm_per_second = []
    
    for i in range(num_seconds):
        start = i * frames_per_second
        end = (i + 1) * frames_per_second
        bpm_per_second.append(np.mean(bpm_per_frame[start:end]))
    
    return np.array(bpm_per_second)


def time_to_frame(time, sr=22050, hop_length=512):
    """Convert time in seconds to the corresponding frame index."""
    return int(np.floor(time * sr / hop_length))

def bpm_for_time(bpm_array, time, sr=22050, hop_length=512):
    """Get the BPM value at a specific time."""
    frame_index = time_to_frame(time, sr, hop_length)
    return bpm_array[frame_index]


#greatest common divisor
def find_interval(numbers):
    if len(numbers) == 1:
        numbers.append(0.10)
    #print(numbers)
    intervals = [int(number * 100) for number in numbers]
    gcd = np.gcd.reduce(intervals) / 100
    return gcd

def generate_groups(onset_times, intervals):
    beatmap = []
    groups = []
    beats = []
    
    current_time = 0
    window = intervals[0]

    onset_times = np.round(onset_times, 2)

    index_onset = 0
    while index_onset < len(onset_times):

        if current_time <= onset_times[index_onset] <  current_time + window:
            beats.append(round(onset_times[index_onset] % window, 2))  # Round onset time to 2 decimal places
            beats_filled = False
        else:
            beats_filled = True
            index_onset -= 1
        
        if beats_filled or index_onset == len(onset_times) - 1:
            if len(beats) != 0:
                interval = find_interval(beats)
                interval = round(interval, 2)  # Round interval to 2 decimal places
            else:
                interval = window / 4
            slot = 0
            while slot <= window:
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
            current_time += window
            if index_onset < len(intervals):
                bpm = bpm_for_time(bpm_array, current_time)
                window = bpm / 60  # Update window based on the next BPM interval

        index_onset += 1

    return beatmap

# main code
bpm_array = tempoEstimator.tempoEstimate((y, sr))

intervals_from_bpm = bpm_per_second(bpm_array, sr, 512)
#print(intervals_from_bpm)
beatmap = generate_groups(onset_times, intervals_from_bpm)


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