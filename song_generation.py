import librosa
import numpy as np
import utils

def find_section_label(start_measure_time, musical_sections):
    for section_label, start_time, end_time in musical_sections:
        if start_time <= start_measure_time < end_time:
            return section_label
    return None

# TO review
def find_best_subdivision_level(measure_time, min_interval):
    #print(f"measure_time: {measure_time} with min_interval {min_interval}")
    # Consider common musical subdivisions: 1, 2, 4, 8, 16, 32, etc.
    common_subdivisions = [2**i for i in range(6)]  # Up to 32th note
    for subdivision in common_subdivisions:
        interval = measure_time / subdivision
        #print(abs(interval - min_interval))
        if abs(interval - min_interval) < 50:
            return subdivision
    return max(common_subdivisions)

async def generate_chart(song_path):
    y, sr = librosa.load(song_path)
    onset_times, bpms, rms, musical_sections = init_generate_chart(y, sr)
    rms_threshold = utils.find_rms_threshold(rms, sr)
    song_duration = librosa.get_duration(y=y, sr=sr) * 1000
    beatmap = []
    
    start_bpm = bpms[0][0]

    measure_time = calculate_measure_time(start_bpm)
    
    #print(f"measure_time: {measure_time}")
    
    start_time = onset_times[0]
    bpms = bpms
    start_measure_time = start_time
    index_onset = 0

    while start_measure_time <= song_duration:
        #print(f"start_measure_time: {start_measure_time}")
        #print(f"measure_time: {measure_time}")
        onsets_in_measure, index_onset = collect_onsets_in_measure(onset_times, start_measure_time, measure_time, index_onset)
        #print(f"raw: {onsets_in_measure}")
        #if len(onsets_in_measure) == 0:
        #    beats_per_measure = generate_empty_measure()
        #else:
        #    beats_per_measure, index_onset = generate_beats(onsets_in_measure, measure_time, start_measure_time, index_onset, rms, rms_threshold)
        beats_per_measure, index_onset = generate_beats(onsets_in_measure, measure_time, start_measure_time, index_onset, rms, rms_threshold, musical_sections)
        
        beatmap.append(beats_per_measure)
        start_measure_time += measure_time
        
        # Update measure time based on BPM changes
        bpm = utils.bpm_for_time(bpms, start_measure_time)
        #print(f"for bpm: {bpm}")
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

# Main function to generate beats
def generate_beats(onsets_in_measure, measure_time, start_measure_time, index_onset, smooth_rms, rms_threshold, musical_sections, sr=22050):
    
    # Find the section label for the current measure time
    current_section_label = find_section_label(start_measure_time, musical_sections)
    #print(f"current_section_label: {current_section_label} for start_measure_time: {start_measure_time}")

    # Static variables to store section notes and track the active section
    if not hasattr(generate_beats, 'section_notes_dict'):
        generate_beats.section_notes_dict = {}
        generate_beats.active_section_label = None

    section_notes_dict = generate_beats.section_notes_dict

    # Ensure section dictionary structure
    if current_section_label is not None:
        if current_section_label not in section_notes_dict:
            section_notes_dict[current_section_label] = []
        section_measures = section_notes_dict[current_section_label]
        
        # Determine the measure index within the section
        current_measure_index = (start_measure_time - min(start for _, start, end in musical_sections if start <= start_measure_time < end)) // measure_time
        current_measure_index = int(current_measure_index)
        
        # Check if the current measure has already been generated
        if current_measure_index < len(section_measures):
            return section_measures[current_measure_index], index_onset
    else:
        generate_beats.active_section_label = None
        beats_per_measure = []

    #print(f"dict: {generate_beats.section_notes_dict}")

    # Convert start_measure_time to frames and check RMS
    frame_index = librosa.time_to_frames(start_measure_time / 1000, sr=sr)
    
    # TODO - Tweak values to find the best time to switch to onset detection or not
    onset_detection_mode = False
    if smooth_rms[frame_index] > rms_threshold:
        ideal_subdivision = 8
    elif smooth_rms[frame_index] > 2 * rms_threshold / 3:
        #ideal_subdivision = 4
        ideal_subdivision = 8 # switches to onset detection
        onset_detection_mode = True
    elif smooth_rms[frame_index] > rms_threshold / 8:
        ideal_subdivision = 8 # switches to onset detection
        onset_detection_mode = True
    else:
        #ideal_subdivions = None
        ideal_subdivision = 8 # switches to onset detection
        onset_detection_mode = True

    if onset_detection_mode and len(onsets_in_measure) != 0:
        # Quantize onsets
        onsets_in_measure, index_onset = quantize_onsets(onsets_in_measure, measure_time, ideal_subdivision, start_measure_time, index_onset)
        print(onsets_in_measure)

    #print(onsets_in_measure)
    # Generate beats for the measure
    # TODO - avoid generating same note on same key in quick succession
    beats_per_measure = []
    beat = start_measure_time
    if ideal_subdivision is None:
        for i in range(4):
            group = np.zeros(4, dtype=int)
            beats_per_measure.append(group)
    else:
        for i in range(ideal_subdivision):
            print(beat)
            group = np.zeros(4, dtype=int)
            if onset_detection_mode and beat in onsets_in_measure:
                idx = np.random.randint(0, 4)
                group[idx] = 1
            if not onset_detection_mode:
                group[np.random.randint(0, 4)] = 1
            beats_per_measure.append(group)
            beat += measure_time // ideal_subdivision

     # Store the generated beats in the dictionary if they belong to a section
    if current_section_label is not None:
        section_notes_dict[current_section_label].append(beats_per_measure)
    
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

def chart_file_creation(beatmap, bpms, start_time, song):
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

def init_generate_chart(y, sr):
    # Filter the audio
    y = utils.audioFilter(y, sr)

    # Grab the parameters for our generate_chart algorithm
    onset_times = utils.onset_detection(y, sr)
    bpms = [(utils.find_best_tempo(y, sr), 0)] # for the current version, we assume song is CONSTANT tempo
    rms_values = librosa.feature.rms(y=y)[0]
    smoothed_rms = utils.smooth_rms(rms_values) # smoothen out the rms curve
    musical_sections = utils.segmentAnalysis(y, sr)
    return onset_times, bpms, smoothed_rms, musical_sections


if __name__ == "__main__":

    # main code
    song_name = "sink"
    y, sr = librosa.load("Music+Beatmaps/"+song_name+".mp3")

    #y = utils.slice_music(y, sr, 40, 100)

    y = utils.audioFilter(y, sr)
    #y = librosa.effects.harmonic(y=y)
    # onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    # pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)
    # beats_plp = np.flatnonzero(librosa.util.localmax(pulse))

    # times = librosa.times_like(onset_env)
    onset_times = utils.onset_detection(y, sr)

    # utils.createClickTrack(y, sr, librosa.frames_to_time(beats_plp), song_name+"click")

    bpms = [(utils.find_best_tempo(y, sr), 0)] # for the current version, we assume CONSTANT tempo
    print(bpms)

    beatmap, start_time = generate_chart(y, sr)

    chart_file_creation(beatmap, bpms, start_time, song_name)