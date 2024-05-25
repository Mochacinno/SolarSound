import librosa
import matplotlib.pyplot as plt
import numpy as np
import tempoEstimator
from utils import bpm_for_time
from utils import audioFilter

def generate_chart(onset_times, bpms, song_duration):

    beatmap = []
    
    start_bpm = bpms[0][0]
    measure_time = calculate_measure_time(start_bpm)
    #print(f"measure_time: {measure_time}")
    
    index_onset = 0
    start_time = onset_times[0]
    start_measure_time = start_time
    while start_measure_time <= song_duration:
        print(f"start_measure_time: {start_measure_time}")
        print(f"measure_time: {measure_time}")
        onsets_in_measure, index_onset = collect_onsets_in_measure(onset_times, start_measure_time, measure_time, index_onset)
        print(f"raw: {onsets_in_measure}")
        if len(onsets_in_measure) == 0:
            beats_per_measure = generate_empty_measure()
        else:
            beats_per_measure, index_onset = generate_beats(onsets_in_measure, measure_time, start_measure_time, index_onset)
        
        beatmap.append(beats_per_measure)
        start_measure_time += measure_time
        
        # Update measure time based on BPM changes
        bpm = bpm_for_time(bpms, start_measure_time)
        measure_time = calculate_measure_time(bpm)

    return beatmap, start_time

def calculate_measure_time(bpm):
    # calculates ( 60 / bpm ) * 4
    return int(240000 / bpm)

def collect_onsets_in_measure(onset_times, start_measure_time, measure_time, index_onset):
    end_measure_time = start_measure_time + measure_time
    print(f"end_measure_time: {end_measure_time}")
    onsets_in_measure = []

    #print("ONSET WINDOW")
    while index_onset < len(onset_times) and start_measure_time <= onset_times[index_onset] < end_measure_time:
        #print(onset_times[index_onset])
        onsets_in_measure.append(onset_times[index_onset])
        index_onset += 1
    
    return onsets_in_measure, index_onset

def generate_empty_measure():
    return [np.zeros(4, dtype=int) for _ in range(4)]

def generate_beats(onsets_in_measure, measure_time, start_measure_time, index_onset):
    ideal_subdivision = 16 # to change
    onsets_in_measure, index_onset = quantize_onsets(onsets_in_measure, measure_time, ideal_subdivision, start_measure_time, index_onset)
    print(f"quantised: {onsets_in_measure}")
    beats_per_measure = []

    beat = start_measure_time
    for i in range(ideal_subdivision):
        group = np.zeros(4, dtype=int)
        if beat in onsets_in_measure:
            idx = np.random.randint(0, 4)
            group[idx] = 1
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
        print(f"{onset_times[index_onset - 1]} was replaced")
        onset_times[index_onset - 1] = max(quantized_onsets)
        index_onset -= 1
    return quantized_onsets, index_onset

def chartFileCreation(beatmap, bpms, start_time):
    # Format BPMS into text content
    text_content = "BPMS:\n"
    for bpm, start_time in bpms:
        text_content += f"{start_time}:{bpm},\n"
    # Format note start time
    text_content += "START_TIME:\n"
    text_content += str(start_time)+"\n"
    # Format beatmap notes into text content
    text_content += "NOTES:\n"
    for groups in beatmap:
        for group in groups:
            text_content += ''.join(map(str, group))  # Convert group to string and append to text content
            text_content += "\n"
        text_content += ",\n"  # Add comma and newline after every measure
    
    # Write text content to a file
    output_file = "onset_times.txt"
    with open(output_file, 'w') as file:
        file.write(text_content)
    
    print(f"Text file '{output_file}' generated successfully.")

# main code
song = "Music+Beatmaps/nATALIECUT2.mp3"
y, sr = librosa.load(song)
y_filter = audioFilter(y, sr)
#y_filter = librosa.effects.percussive(y=y, margin=5)
hop_length = 512
oenv = librosa.onset.onset_strength(y=y_filter, sr=sr, hop_length=hop_length)
onset_times = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, units='time')

onset_times = onset_times * 1000
onset_times = onset_times.astype(np.int64)
bpms = tempoEstimator.bpm_changes(tempoEstimator.tempoEstimate((y, sr)))
print(bpms)
song_duration = librosa.get_duration(y=y, sr=sr) * 1000

## For testing purposes
#onset_times = [1000, 2100, 3994, 5120, 6000, 8790, 17100, 17520, 18003, 18420, 18800]
#bpms = [(60,0),(120,12500)]
#beatmap = generate_chart(onset_times, bpms, 20000)

beatmap, start_time = generate_chart(onset_times, bpms, song_duration)
chartFileCreation(beatmap, bpms, start_time)