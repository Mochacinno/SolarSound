import numpy as np
import scipy
import matplotlib.pyplot as plt
import sklearn.cluster
import librosa
import matplotlib.patches as patches




def segmentPicking(labels, times): 
    # needs to both be form of a numpy array
    # Define error window and minimum duration
    error_window = 1
    min_duration = 1.0

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


y, sr = librosa.load("Music+Beatmaps/universe.ogg")


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

    bound_times = librosa.frames_to_time(bound_frames)
    freqs = librosa.cqt_frequencies(n_bins=C.shape[0],
                                    fmin=librosa.note_to_hz('C1'),
                                    bins_per_octave=BINS_PER_OCTAVE)
    return bound_segs, bound_times
#analyse segment timing
print(bound_times)
print(bound_segs)
res = segmentPicking(bound_segs, bound_times)
print(res)

# Plot
colors = plt.get_cmap('Paired', k)
fig, ax = plt.subplots()
librosa.display.specshow(C, y_axis='cqt_hz', sr=sr,
                         bins_per_octave=BINS_PER_OCTAVE,
                         x_axis='time', ax=ax)

for interval, label in zip(zip(bound_times, bound_times[1:]), bound_segs):
    ax.add_patch(patches.Rectangle((interval[0], freqs[0]),
                                   interval[1] - interval[0],
                                   freqs[-1],
                                   facecolor=colors(label),
                                   alpha=0.50))

plt.show()