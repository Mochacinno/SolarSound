import librosa
import numpy as np

def pitchDetection(y, sr):

    f0, voiced_flag, voiced_probs = librosa.pyin(y,
                                                 sr=sr,
                                                 fmin=librosa.note_to_hz('C2'),
                                                 fmax=librosa.note_to_hz('C7'))
    times = librosa.times_like(f0, sr=sr)

    # Convert f0 to MIDI note numbers, NaN values are replaced with -1
    midi_notes = librosa.hz_to_midi(f0)
    midi_notes = np.nan_to_num(midi_notes, nan=-1)

    # Detect changes in MIDI note values
    change_points = np.where(np.diff(midi_notes, prepend=midi_notes[0]) != 0)[0]
    change_times = times[change_points]

    return change_times

