import librosa
import matplotlib.pyplot as plt
import numpy as np
import tempoEstimator
from audioFilter import audioFilter

import sounddevice as sd

song = "sink.mp3"
y, sr = librosa.load(song)

# add instead a time delay before spawning the notes instead of just spawning 0s every 0.1 seconds

y_filter = audioFilter(y, sr)
hop_length = 512
oenv = librosa.onset.onset_strength(y=y_filter, sr=sr, hop_length=hop_length)
onset_times = np.round(librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, units='time'), 2)

## Generate clicks at these change points
#clicks = librosa.clicks(times=onset_times, sr=sr, length=len(y))
#
## Combine the original audio with the clicks
#y_with_clicks = y + clicks
#
## Play the combined audio
#sd.play(y_with_clicks, sr)
#
#sd.wait()

def bpm_to_intervals(bpm_array):
    # the bpm-array is the bpm at each frame, so these are the intervals for that given moment to the frame
    intervals = 60.0 / bpm_array  # Convert BPM to intervals in seconds
    return intervals

def bpm_per_second(bpm_per_frame, sr, hop_length):

    # Calculate the number of frames per second
    frames_per_second = sr // hop_length

    # Number of seconds in the audio
    num_seconds = len(bpm_per_frame) // frames_per_second
    #print(num_seconds)
    
    bpm_per_second = []
    
    for i in range(num_seconds):
        start = i * frames_per_second
        end = (i + 1) * frames_per_second
        bpm_per_second.append(np.mean(bpm_per_frame[start:end]))
    
    return np.array(bpm_per_second)

def bpm_for_time(bpm_array, time):
    """
    Get the BPM value at a specific time.
    
    Parameters:
    bpm_array (list of tuples): List of tuples (bpm, time_when_change_occurs).
    time (float): The specific time at which to find the BPM.
    
    Returns:
    float: The BPM value at the specified time.
    """
    bpm = bpm_array[0][0]  # Start with the first BPM value
    
    for bpm_change, change_time in bpm_array:
        if time < change_time:
            break
        bpm = bpm_change
    
    return bpm


#greatest common divisor
#def find_interval(numbers):
#    if len(numbers) == 1:
#        numbers.append(0.10)
#    #print(numbers)
#    intervals = [int(number * 100) for number in numbers]
#    gcd = round(np.gcd.reduce(intervals) / 100, 2)
#    return gcd

def find_best_subdivision_level(measure_time, min_interval):
    # Consider common musical subdivisions: 1, 2, 4, 8, 16, 32, etc.
    common_subdivisions = [2**i for i in range(4)]  # Up to 1/32th subdivision
    for subdivision in common_subdivisions:
        interval = measure_time / subdivision
        if interval <= min_interval:
            return subdivision
    return max(common_subdivisions)

def quantize_onsets(onsets, measure_time, subdivision_level):

    onset_end = max(onsets)
    subdivision_interval = measure_time / subdivision_level
    
    # Calculate the grid points within the range of onset_start to onset_end
    grid_points = np.arange(premeasure_time, onset_end + subdivision_interval, subdivision_interval)
    
    # Quantize the onsets to the nearest grid point
    quantized_onsets = [min(grid_points, key=lambda x: abs(x - onset)) for onset in onsets]
    
    return quantized_onsets


def generate_groups(onset_times, bpms):
    print(bpms)
    # onset times and bpm should just be rounded to 2 decimal places from the start. its not like we can perceive that difference
    beatmap = []
    beats_per_measure = [] # we just suppose its 4 measures per bar so 4/4 all the time. (which will fuck up if the music is in 3/4 or becomes that midway)
    onsets_in_measure = []
    
    measure_time = 240 / bpms[0][0] # because we start at t = 0. and so 60/bpm  * 4
    print(f"measure time: {measure_time}")
    print(f"onsets: {onset_times}")
    
    # dunno if i need to round 
    #onset_times = np.round(onset_times, 2)
    #print(bpms)
    song_duration = librosa.get_duration(y=y, sr=sr)

    index_onset = 0
    
    # for quantisation
    end_prev_measure_time = 0
    prev_measure_time = 0
    prev_ideal_subdivision = 0
    prev_last_quantized_onset = 0

    start_measure_time = onset_times[0] # assume its the first onset detection
    while start_measure_time <= song_duration:
        # basing off bpm at time t, we get the bpm, and thus in 4 beats, we know how much time has passed (this is the variable window)
        # TO FIX: need to add the previous quantised final element onset time to the next to clauclate the quantisation for all of them i think?
        # checking whether to add any notes detected by onset detection
        end_measure_time = start_measure_time + measure_time
        if index_onset < len(onset_times):
            if start_measure_time <= onset_times[index_onset] <  end_measure_time:
                onsets_in_measure.append(onset_times[index_onset])
                beats_filled = False
            else:
                # once theres no more onset times that are within start of measure and end of measure
                beats_filled = True
                index_onset -= 1 # to go back to the previous onset because it we want to start with the one that couldnt be put into the measure the next time

            if beats_filled or index_onset == len(onset_times) - 1: # if index onset is already at the last element of onset time, it should still process it.]
                if prev_last_quantized_onset != 0: # for the startin case
                    onsets_in_measure.insert(0, prev_last_quantized_onset)
                print(f"start measure time: {start_measure_time}")
                print(f"onsets not quantised: {onsets_in_measure}")

                if len(onsets_in_measure) == 0:
                    # if there are no beats within this measure window, generate zeros for each beat of the measure
                    ideal_subdivision = 4 # assuming 4 subdivisions as default for empty measures
                    for i in range(ideal_subdivision):
                            group = np.zeros(4, dtype=int)
                            beats_per_measure.append(group)

                elif len(onsets_in_measure) == 1:
                    # if there are no beats within this measure window, generate zeros for each beat of the measure
                    ideal_subdivision = 4 # assuming 4 subdivisions as default for empty measures
                    for i in range(ideal_subdivision):
                        if i == 0:
                            # generate a 1 somewhere within the 4 zeros
                            group = np.zeros(4, dtype=int)
                            idx = np.random.randint(0, 4)
                            group[idx] = 1
                            beats_per_measure.append(group)
                        else:
                            group = np.zeros(4, dtype=int)
                            beats_per_measure.append(group)

                else:
                    # quantize onset_times first
                    ideal_subdivision = find_best_subdivision_level(measure_time, min(np.diff(onsets_in_measure)))
                    ideal_subdivision = 16
                    print(f"ideal_subdivision: {ideal_subdivision}")
                    onsets_in_measure = quantize_onsets(onsets_in_measure, measure_time, ideal_subdivision)
                    print(f"onsets quantised: {onsets_in_measure}")

                    # generate beats based on quantized onsets
                    beat = onsets_in_measure[0]
                    for i in range(ideal_subdivision):
                        #print(f"for beat: {beat}")
                        #print(f"is beat in onset? {beat in onsets_in_measure}")
                        if beat in onsets_in_measure:
                            # generate a 1 somewhere within the 4 zeros
                            group = np.zeros(4, dtype=int)
                            idx = np.random.randint(0, 4)
                            group[idx] = 1
                            beats_per_measure.append(group)
                        else:
                            # generate 0000
                            group = np.zeros(4, dtype=int)
                            beats_per_measure.append(group)
                        beat += (measure_time / ideal_subdivision) 
                if len(onsets_in_measure) != 0:
                    if max(onsets_in_measure) == end_measure_time:
                        # case where the last quantised note was the last beat of its measure so it needs to generated at the start of the new measure
                        prev_last_quantized_onset = max(onsets_in_measure)
                    # else we just need to have an empty array
                    else:
                        prev_last_quantized_onset = 0
                else:
                    prev_last_quantized_onset = 0
                onsets_in_measure = [] # reset onsets in measure for next measure
                beatmap.append(beats_per_measure)
                beats_per_measure = [] # reset the beats per mesure
                #print(f"start measure time {start_measure_time}")
                
                start_measure_time += measure_time # update the start_measure_time for next measure

                # grab the new bpm if it changed
                bpm = bpm_for_time(bpms, start_measure_time)
                measure_time = 240 / bpm  # Update window based on the next BPM interval
                print(f"measure_time: {measure_time}")
                # end_prev_measure_time = end_measure_time
                # prev_measure_time = measure_time
                # prev_ideal_subdivision = ideal_subdivision
            
            # continue for next index_onset
            index_onset += 1
        else:
            start_measure_time += measure_time # update the start_measure_time for next measure
    return beatmap

# main code
bpm_array = tempoEstimator.tempoEstimate((y, sr))

bpms = tempoEstimator.bpm_changes(bpm_array)
#print(bpms)

beatmap = generate_groups(onset_times, bpms)
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