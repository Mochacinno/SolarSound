import librosa
import matplotlib.pyplot as plt
import numpy as np

import utils

def smooth_rms(rms, window_size=5):
    """Smooth the RMS values using a simple moving average."""
    return np.convolve(rms, np.ones(window_size)/window_size, mode='same')

def find_rms_threshold(smoothed_rms) :

    # Compute the time for each RMS value
    frames = range(len(smoothed_rms))
    t = librosa.frames_to_time(frames, sr=sr)

    # Determine a threshold for high RMS values
    mean_rms = np.mean(smoothed_rms)
    std_rms = np.std(smoothed_rms)
    threshold = mean_rms - 0.5 * std_rms  # You can adjust the multiplier based on your requirements
    #print(threshold)

    return threshold


# TO review
def find_best_subdivision_level(measure_time, min_interval):
    print(f"measure_time: {measure_time} with min_interval {min_interval}")
    # Consider common musical subdivisions: 1, 2, 4, 8, 16, 32, etc.
    common_subdivisions = [2**i for i in range(6)]  # Up to 32th note
    for subdivision in common_subdivisions:
        interval = measure_time / subdivision
        print(abs(interval - min_interval))
        if abs(interval - min_interval) < 50:
            return subdivision
    return max(common_subdivisions)

def generate_chart(onset_times, bpms, song_duration, smooth_rms, rms_threshold):

    beatmap = []
    
    start_bpm = bpms[0][0]
    measure_time = calculate_measure_time(start_bpm)
    #print(f"measure_time: {measure_time}")
    
    index_onset = 0
    start_time = onset_times[0]
    bpms = bpms
    start_measure_time = start_time
    while start_measure_time <= song_duration:
        print(f"start_measure_time: {start_measure_time}")
        #print(f"measure_time: {measure_time}")
        onsets_in_measure, index_onset = collect_onsets_in_measure(onset_times, start_measure_time, measure_time, index_onset)
        #print(f"raw: {onsets_in_measure}")
        #if len(onsets_in_measure) == 0:
        #    beats_per_measure = generate_empty_measure()
        #else:
        #    beats_per_measure, index_onset = generate_beats(onsets_in_measure, measure_time, start_measure_time, index_onset, smooth_rms, rms_threshold)
        beats_per_measure, index_onset = generate_beats(onsets_in_measure, measure_time, start_measure_time, index_onset, smooth_rms, rms_threshold)
        
        beatmap.append(beats_per_measure)
        start_measure_time += measure_time
        
        # Update measure time based on BPM changes
        bpm = bpm_for_time(bpms, start_measure_time)
        print(f"for bpm: {bpm}")
        measure_time = calculate_measure_time(bpm)
    return beatmap, start_time

def calculate_measure_time(bpm):
    # calculates ( 60 / bpm ) * 4
    return int(240000 / bpm)

def collect_onsets_in_measure(onset_times, start_measure_time, measure_time, index_onset):
    end_measure_time = start_measure_time + measure_time
    #print(f"end_measure_time: {end_measure_time}")
    onsets_in_measure = []

    #print("ONSET WINDOW")
    while index_onset < len(onset_times) and start_measure_time <= onset_times[index_onset] < end_measure_time:
        #print(onset_times[index_onset])
        onsets_in_measure.append(onset_times[index_onset])
        index_onset += 1
    
    return onsets_in_measure, index_onset

def generate_empty_measure():
    return [np.zeros(4, dtype=int) for _ in range(4)]

def generate_beats(onsets_in_measure, measure_time, start_measure_time, index_onset, smooth_rms, rms_threshold):
    #print(f"onsets in measure: {onsets_in_measure}")
    frame_index = librosa.time_to_frames(start_measure_time/1000, sr=sr)
    if smooth_rms[frame_index] > rms_threshold:
        #generate alot of notes
        ideal_subdivision = 8
    else:
        ideal_subdivision = 4
    print(ideal_subdivision)
    #onsets_in_measure, index_onset = quantize_onsets(onsets_in_measure, measure_time, ideal_subdivision, start_measure_time, index_onset)
    #print(f"quantised: {onsets_in_measure}")
    beats_per_measure = []

    beat = start_measure_time
    for i in range(ideal_subdivision):
        group = np.zeros(4, dtype=int)
        # If the measure has a lot of onsets detected, generate notes in every subdivision
        group[np.random.randint(0, 4)] = 1
        beats_per_measure.append(group)
        beat += measure_time // ideal_subdivision
        #print(beat) 
    
    return beats_per_measure, index_onset

def quantize_onsets(onsets, measure_time, subdivisions, start_measure_time, index_onset):
    
    interval = measure_time // subdivisions
    end_measure_time = start_measure_time + measure_time
    grid_points = np.arange(start_measure_time, end_measure_time + interval, interval)
    
    quantized_onsets = [min(grid_points, key=lambda x: abs(x - onset)) for onset in onsets]
    
    if end_measure_time == max(quantized_onsets):
        #print(f"{onset_times[index_onset - 1]} was replaced")
        onset_times[index_onset - 1] = max(quantized_onsets)
        index_onset -= 1
    return quantized_onsets, index_onset

def chartFileCreation(beatmap, bpms, start_time, song):
    # Format note start time
    text_content = "START_TIME:\n"
    text_content += str(start_time)+"\n"
    # Format BPMS into text content
    text_content += "BPMS:\n"
    for bpm, start_time in bpms:
        text_content += f"{start_time}:{bpm},\n"
    # Format beatmap notes into text content
    text_content += "NOTES:\n"
    for groups in beatmap:
        for group in groups:
            text_content += ''.join(map(str, group))  # Convert group to string and append to text content
            text_content += "\n"
        text_content += ",\n"  # Add comma and newline after every measure
    
    # Write text content to a file
    output_file = "Music+Beatmaps/"+song+".txt"
    with open(output_file, 'w') as file:
        file.write(text_content)
    
    print(f"Text file '{output_file}' generated successfully.")

# main code
song_name = "universe"
y, sr = librosa.load("Music+Beatmaps/"+song_name+".ogg")
## SLICE THE MUSIC
# Define start and end times in seconds
start_time = 0  # Start at 5 seconds
end_time = 120   # End at 10 seconds

# Convert start and end times to sample indices
start_sample = int(start_time * sr)
end_sample = int(end_time * sr)

# Slice the y array
#y = y[start_sample:end_sample]
y_old = y
y = audioFilter(y, sr)

#onset_times = onset_detection(y, sr)
#onset_times = onset_times * 1000
#onset_times = onset_times.astype(np.int64)
#createClickTrack(y, sr, onset_times / 1000, song_name+"click")
onset_times = [1289]

start_time = onset_times[0]
#bpms = tempoEstimator.bpm_changes(tempoEstimator.tempoEstimate((y, sr)), start_time)
#print(bpms)
bpms = [(175,0)]
song_duration = librosa.get_duration(y=y, sr=sr) * 1000

rms_values = librosa.feature.rms(y=y)[0]
smoothed_rms = smooth_rms(rms_values)
rms_threshold = find_rms_threshold(smoothed_rms)

## For testing purposes
#onset_times = [1000, 2100, 3994, 5120, 6000, 8790, 17100, 17520, 18003, 18420, 18800]
#bpms = [(60,0),(120,12500)]
#beatmap = generate_chart(onset_times, bpms, 20000)

beatmap, start_time = generate_chart(onset_times, bpms, song_duration, smoothed_rms, rms_threshold)
chartFileCreation(beatmap, bpms, start_time, song_name)