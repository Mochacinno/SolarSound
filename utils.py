import sounddevice as sd
import soundfile as sf
import scipy
import librosa
import numpy as np
import sklearn.cluster

import librosa
import numpy as np

def song_tempo_estimate(y, sr):
    """
    dynamic tempo estimate of music 
    ### Parameters:
    tuple (y, sr)
    ### Returns:
    An array of tempo estimates along the time
    """
    oenv = librosa.onset.onset_strength(y=y, sr=sr)

    tempo_dynamic = tempo(onset_envelope=oenv, sr=sr, std_bpm=2)

    return tempo_dynamic

def find_best_tempo(y, sr, factors=[2, 2/3], tolerance=5):
    def is_close(a, b, tol):
        return abs(a - b) <= tol

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

    # Estimate the tempo
    tempo_estimates = song_tempo_estimate(y, sr)

    # Round the tempos to the nearest integer for counting
    rounded_tempos = np.round(tempo_estimates).astype(int)

    # Count the occurrences of each tempo
    tempos = np.unique(rounded_tempos, return_counts=True)

    # Group detected tempos by common factors
    def group_tempos_by_factors(tempos, factors=[2, 2/3], tolerance=5):
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
        def find_best_tempo_in_group(group, tolerance):
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

        best_tempo_in_group = find_best_tempo_in_group(max_group, tolerance)

        return best_tempo_in_group

    # Get the best tempo estimate within the grouped tempos
    best_tempo = group_tempos_by_factors(tempos)

    return best_tempo

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

def slice_music(y, sr, start_time, end_time):
    # Convert start and end times to sample indices
    start_sample = int(start_time * sr)
    end_sample = int(end_time * sr)
    y = y[start_sample:end_sample]
    return y

def smooth_rms(rms, window_size=5):
    """Smooth the RMS values using a simple moving average."""
    return np.convolve(rms, np.ones(window_size)/window_size, mode='same')

def find_rms_threshold(smoothed_rms, sr) :

    # Compute the time for each RMS value
    frames = range(len(smoothed_rms))
    t = librosa.frames_to_time(frames, sr=sr)

    # Determine a threshold for high RMS values
    mean_rms = np.mean(smoothed_rms)
    std_rms = np.std(smoothed_rms)
    threshold = mean_rms - 0.5 * std_rms  # You can adjust the multiplier based on your requirements
    #print(threshold)

    return threshold

def segmentPicking(labels, times): 
    # needs to both be form of a numpy array
    # Define error window and minimum duration
    error_window = 1000
    min_duration = 1000

    # Calculate segment durations
    durations = np.diff(times)

    # Store segments with their labels and time windows, filtering out short segments
    segments = [(labels[i], times[i], times[i+1], durations[i]) for i in range(len(labels)) if durations[i] >= min_duration]

    # Find matching durations within each label group
    unique_labels = np.unique(labels)
    matching_segments = []

    for label in unique_labels:
        label_segments = [seg for seg in segments if seg[0] == label]
        for i in range(len(label_segments)):
            for j in range(i + 1, len(label_segments)):
                _, start_time_i, end_time_i, duration_i = label_segments[i]
                _, start_time_j, end_time_j, duration_j = label_segments[j]
                if abs(duration_i - duration_j) <= error_window:
                    matching_segments.append((label, start_time_i, end_time_i))
                    matching_segments.append((label, start_time_j, end_time_j))

    # Remove duplicates
    matching_segments = list(set(matching_segments))

    # # Print results
    # for seg in matching_segments:
    #     print(seg)
    return matching_segments

def segmentAnalysis(y, sr):
    BINS_PER_OCTAVE = 12 * 3
    N_OCTAVES = 7
    C = librosa.amplitude_to_db(np.abs(librosa.cqt(y=y, sr=sr, bins_per_octave=BINS_PER_OCTAVE, n_bins=N_OCTAVES * BINS_PER_OCTAVE)), ref=np.max)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, trim=False)

    Csync = librosa.util.sync(C, beats, aggregate=np.median)

    # For plotting purposes, we'll need the timing of the beats
    # we fix_frames to include non-beat frames 0 and C.shape[1] (final frame)
    beat_times = librosa.frames_to_time(librosa.util.fix_frames(beats, x_min=0), sr=sr)

    R = librosa.segment.recurrence_matrix(Csync, width=3, mode='affinity', sym=True)

    # Enhance diagonals with a median filter (Equation 2)
    df = librosa.segment.timelag_filter(scipy.ndimage.median_filter)
    Rf = df(R, size=(1, 7))

    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    Msync = librosa.util.sync(mfcc, beats)

    path_distance = np.sum(np.diff(Msync, axis=1)**2, axis=0)
    sigma = np.median(path_distance)
    path_sim = np.exp(-path_distance / sigma)

    R_path = np.diag(path_sim, k=1) + np.diag(path_sim, k=-1)

    deg_path = np.sum(R_path, axis=1)
    deg_rec = np.sum(Rf, axis=1)

    mu = deg_path.dot(deg_path + deg_rec) / np.sum((deg_path + deg_rec)**2)

    A = mu * Rf + (1 - mu) * R_path

    L = scipy.sparse.csgraph.laplacian(A, normed=True)

    # and its spectral decomposition
    evals, evecs = scipy.linalg.eigh(L)

    # We can clean this up further with a median filter.
    # This can help smooth over small discontinuities
    evecs = scipy.ndimage.median_filter(evecs, size=(9, 1))

    # cumulative normalization is needed for symmetric normalize laplacian eigenvectors
    Cnorm = np.cumsum(evecs**2, axis=1)**0.5

    # If we want k clusters, use the first k normalized eigenvectors.
    # Fun exercise: see how the segmentation changes as you vary k

    k = 10 # usually 5

    X = evecs[:, :k] / Cnorm[:, k-1:k]

    # applying k means

    KM = sklearn.cluster.KMeans(n_clusters=k, n_init="auto")

    seg_ids = KM.fit_predict(X)

    bound_beats = 1 + np.flatnonzero(seg_ids[:-1] != seg_ids[1:])

    # Count beat 0 as a boundary
    bound_beats = librosa.util.fix_frames(bound_beats, x_min=0)

    # Compute the segment label for each boundary
    bound_segs = list(seg_ids[bound_beats])

    # Convert beat indices to frames
    bound_frames = beats[bound_beats]

    # Make sure we cover to the end of the track
    bound_frames = librosa.util.fix_frames(bound_frames,
                                           x_min=None,
                                           x_max=C.shape[1]-1)

    bound_times = librosa.frames_to_time(bound_frames) * 1000
    freqs = librosa.cqt_frequencies(n_bins=C.shape[0],
                                    fmin=librosa.note_to_hz('C1'),
                                    bins_per_octave=BINS_PER_OCTAVE)
    
    return segmentPicking(bound_segs, bound_times)

def tempo_frequencies(
    n_bins: int, *, hop_length: int = 512, sr: float = 22050
) -> np.ndarray:
    
    bin_frequencies = np.zeros(int(n_bins), dtype=np.float64)

    bin_frequencies[0] = np.inf
    bin_frequencies[1:] = 60.0 * sr / (hop_length * np.arange(1.0, n_bins))
    return bin_frequencies


def tempo(
    *, 
    y = None, 
    sr = 22050,
    onset_envelope = None,
    tg = None,
    hop_length = 512,
    start_bpm = 120,
    std_bpm = 1.0,
    ac_size = 8.0,
    max_tempo = 320.0,
    prior = None,
    weight_diff_threshold = 1.15e-2
    ):
    
    if tg is None:
        win_length = librosa.time_to_frames(ac_size, sr=sr, hop_length=hop_length).item()

        tg = librosa.feature.tempogram(
            y=y,
            sr=sr,
            onset_envelope=onset_envelope,
            hop_length=hop_length,
            win_length=win_length,
        )
    else:
        # Override window length by what's actually given
        win_length = tg.shape[-2]


    assert tg is not None

    # Get the BPM values for each bin, skipping the 0-lag bin
    bpms = tempo_frequencies(win_length, hop_length=hop_length, sr=sr)

    # Weight the autocorrelation by a log-normal distribution
    if prior is None:
        logprior = -0.5 * ((np.log2(bpms) - np.log2(start_bpm)) / std_bpm) ** 2
    else:
        logprior = prior.logpdf(bpms)

    # Kill everything above the max tempo
    if max_tempo is not None:
        max_idx = int(np.argmax(bpms < max_tempo))
        logprior[:max_idx] = -np.inf

    # explicit axis expansion
    logprior = librosa.util.expand_to(logprior, ndim=tg.ndim, axes=-2)
    
    # Find the top 3 periods, weighted by the prior
    # Using log1p here for numerical stability
    top_3_periods = np.argsort(np.log1p(1e6 * tg) + logprior, axis=-2)[-3:]
    top_3_bpms = np.take(bpms, top_3_periods)
    top_3_weights = np.take(logprior, top_3_periods)
    
    # Choose the best period based on weight differences
    best_period = np.zeros(top_3_bpms.shape[1:], dtype=int)

    for i in range(top_3_weights.shape[1]):
        if np.abs(top_3_weights[0, i] - top_3_weights[1, i]) < weight_diff_threshold:
            best_period[i] = top_3_periods[1, i]
            #print("2nd tempo chosen")
        else:
            best_period[i] = top_3_periods[0, i]

    tempo_est = np.take(bpms, best_period)
    return tempo_est

def onset_detection(y, sr):
    #y = audioFilter(y, sr)
    
    # Superflux
    n_fft = 1024
    hop_length = int(librosa.time_to_samples(1./200, sr=sr))
    lag = 2
    n_mels = 138
    fmin = 27.5
    fmax = 16000.
    max_size = 3

    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, fmin=fmin, fmax=fmax, n_mels=n_mels)

    odf_sf = librosa.onset.onset_strength(S=librosa.power_to_db(S, ref=np.max), sr=sr, hop_length=hop_length, lag=lag, max_size=max_size)

    onset_sf = librosa.onset.onset_detect(onset_envelope=odf_sf, sr=sr, hop_length=hop_length, units='time')

    #frame_time = librosa.frames_to_time(np.arange(len(odf_sf)), sr=sr, hop_length=hop_length)

    onset_sf = onset_sf * 1000
    onset_sf = onset_sf.astype(np.int64)
    return onset_sf


def bpm_for_time(bpms, current_time):
    for i in range(1, len(bpms)):
        if current_time < bpms[i][1]:
            return bpms[i - 1][0]
    return bpms[-1][0]  # Return the last BPM if current_time is beyond the last BPM change start time

def createClickTrack(y, sr, clicks, name):
    #print(clicks)
    click_dynamic = librosa.clicks(times=clicks, sr=sr, click_freq=660,
                               click_duration=0.25, length=len(y))
    y_with_clicks = y + click_dynamic
    sf.write("Music+Beatmaps/"+name+".mp3", y_with_clicks, sr)

def audioFilter(y, sr):
    # And compute the spectrogram magnitude and phase
    S_full, phase = librosa.magphase(librosa.stft(y))

    # We'll compare frames using cosine similarity, and aggregate similar frames
    # by taking their (per-frequency) median value.
    #
    # To avoid being biased by local continuity, we constrain similar frames to be
    # separated by at least 2 seconds.
    #
    # This suppresses sparse/non-repetetitive deviations from the average spectrum,
    # and works well to discard vocal elements.

    S_filter = librosa.decompose.nn_filter(S_full,
                                           aggregate=np.median,
                                           metric='cosine',
                                           width=int(librosa.time_to_frames(2, sr=sr)))

    # The output of the filter shouldn't be greater than the input
    # if we assume signals are additive.  Taking the pointwise minimum
    # with the input spectrum forces this.
    S_filter = np.minimum(S_full, S_filter)

    # We can also use a margin to reduce bleed between the vocals and instrumentation masks.
    # Note: the margins need not be equal for foreground and background separation
    margin_i, margin_v = 2, 10 # 2 and 10
    power = 1 # usually is 2

    mask_i = librosa.util.softmask(S_filter,
                                   margin_i * (S_full - S_filter),
                                   power=power)

    mask_v = librosa.util.softmask(S_full - S_filter,
                                   margin_v * S_filter,
                                   power=power)

    # Once we have the masks, simply multiply them with the input spectrum
    # to separate the components

    S_foreground = mask_v * S_full
    S_background = mask_i * S_full

    y_foreground = librosa.istft(S_foreground* phase)
    y = y_foreground
    return y

# ## SLICE THE MUSIC
# # Define start and end times in seconds
# start_time = 76  # Start at 5 seconds
# end_time = 96   # End at 10 seconds

# # Convert start and end times to sample indices
# start_sample = int(start_time * sr)
# end_sample = int(end_time * sr)

# # Slice the y array
# y = y[start_sample:end_sample]

# ## Band pass filter
# lowcut = 300.0  # Low cutoff frequency, Hz
# highcut = 3000.0  # High cutoff frequency, Hz
# order = 4  # Filter order

# # Normalize the frequencies by the Nyquist frequency (sr / 2)
# nyquist = 0.5 * sr
# low = lowcut / nyquist
# high = highcut / nyquist

# # Create the filter coefficients
# b, a = signal.butter(order, [low, high], btype='band')

# # Apply the filter to the signal
# y = signal.filtfilt(b, a, y)

# ## AUDIO FINGERPRINTING
# y_within, sr_within = librosa.load("nATALIE.mp3", sr=None)
# y_find, _ = librosa.load("nATALIECUT2.mp3", sr=None)

# c = signal.correlate(y_within, y_find, mode='full', method='fft')

# # Calculate time values in seconds
# time_values = np.arange(len(c)) / sr_within

# # Plot the scatter of correlation values by time
# plt.figure(figsize=(10, 6))
# plt.scatter(time_values[::100], c[::100], s=10, color='blue', alpha=0.5)
# plt.xlabel('Time (seconds)')
# plt.ylabel('Correlation Value')
# plt.title('Correlation Values by Time')
# plt.grid(True)
# plt.show()

if __name__ == '__main__':
    print("script run by user")