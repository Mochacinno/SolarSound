
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

map = "onset_times"

bpms = [(123.0, 0.0), (129.0, 0.58), (92.0, 0.74), (199.0, 0.98), (96.0, 2.46), (199.0, 3.6), (96.0, 6.2), (199.0, 10.29), (96.0, 10.66), (185.0, 12.63)]

start_time = 0.07

beatmap = []
beats = []
beats_in_measure = []
res = []
with open(map + ".txt", 'r') as file:
        for line in file:
            if line.strip():
                if "," in line.strip():
                    beatmap.append(beats_in_measure)
                    beats_in_measure = []
                else:
                    beat = []
                    blocks = line.strip()
                    for block in blocks:
                        beat.append(int(block))
                    beats_in_measure.append(beat)
#print(len(beatmap))

current_time = start_time * 1000

for beats_per_mesure in beatmap:
    bpm = bpm_for_time(bpms, current_time / 1000)
    measure_time = (60 / bpm) * 4000
    print(measure_time)
    for i in range(len(beats_per_mesure)):
        # Calculate the time for the current beat by adding the time for the previous beat
        beats_per_mesure[i] = (beats_per_mesure[i], (current_time + (measure_time / (len(beats_per_mesure))-1) * i))
        # Update the previous time for the next iteration
    current_time += measure_time
    res.append(beats_per_mesure)
print(res)