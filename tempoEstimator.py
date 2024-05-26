import librosa
import numpy as np
from utils import tempo

def tempoEstimate(song):
    """
    dynamic tempo estimate of music 
    ### Parameters:
    tuple (y, sr)
    ### Returns:
    An array of tempo estimates along the time
    """
    y, sr = song
    oenv = librosa.onset.onset_strength(y=y, sr=sr)

    tempo_dynamic = tempo(onset_envelope=oenv, sr=sr, std_bpm=2)
    #print(tempo_dynamic)
    #_, beats_dynamic = librosa.beat.beat_track(y=y, sr=sr, units='time',
    #                                           bpm=tempo_dynamic, trim=False)

    # round values
    #tempo_dynamic = np.round(tempo_dynamic)
    return tempo_dynamic

def bpm_to_intervals(bpm_array, sr):
    # Convert BPM to intervals in seconds
    intervals = 60.0 / bpm_array
    frame_intervals = intervals * sr / 512
    return frame_intervals

def intervals_to_times(intervals, sr, hop_length):
    # Convert intervals to time stamps
    times = []
    current_time = 0.0
    
    for interval in intervals:
        times.append(current_time)
        current_time += interval * hop_length / sr
    
    return np.array(times)


def bpm_changes(bpm_array, start_time):
    sr=22050
    hop_length=512
    """
    Convert an array of BPM values per frame into an array of tuples representing changes in BPM.
    
    Parameters:
    bpm_array (np.ndarray): Array of BPM values per frame.
    sr (int): Sample rate of the audio.
    hop_length (int): Hop length used in the analysis.

    Returns:
    list: List of tuples (bpm, time_in_seconds) representing BPM changes.
    """
    changes = []
    previous_bpm = None
    
    for i, bpm in enumerate(bpm_array):
        if bpm != previous_bpm:
            time = int((i * hop_length / sr) * 1000) + start_time # turn into miliseconds and get rid of floating point issue in calculations later on
            changes.append((int(bpm), time))
            previous_bpm = bpm
    
    return changes