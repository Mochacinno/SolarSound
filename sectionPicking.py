import numpy as np

# Input data
times = np.array([
    0.60371882, 6.61768707, 21.38557823, 21.84997732, 32.25251701,
    32.74013605, 42.46929705, 42.9569161, 53.15047619, 63.87809524,
    75.99891156, 77.81006803, 98.4061678, 98.89378685, 119.1415873,
    124.83047619, 129.52090703, 139.50548753, 140.41106576, 160.03192744,
    177.53977324, 180.92988662, 186.61877551, 187.10639456, 207.0523356,
    208.0275737, 228.11283447, 241.20888889
])
labels = np.array([4, 8, 1, 2, 1, 8, 1, 2, 5, 8, 2, 7, 9, 3, 5, 8, 1, 9, 0, 2, 9, 6, 2, 7, 9, 3, 4])

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
