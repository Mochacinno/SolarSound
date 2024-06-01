import numpy as np

# Measure time in seconds
measure_time = 1.951219512195122

# Onset times in seconds within the measure
onsets = [0.07, 0.56, 0.72, 1.18, 1.63, 1.95]

def calculate_intervals(onsets):
    return np.diff(onsets)

def find_minimum_interval(intervals):
    return min(intervals)

# TO review
def find_best_subdivision_level(measure_time, min_interval):
    print(f"measure_time: {measure_time} with min_interval {min_interval}")
    # Consider common musical subdivisions: 1, 2, 4, 8, 16, 32, etc.
    common_subdivisions = [2**i for i in range(6)]  # Up to 64th note
    for subdivision in common_subdivisions:
        interval = measure_time / subdivision
        print(abs(interval - min_interval))
        if abs(interval - min_interval) < 50:
            return subdivision
    return max(common_subdivisions)



def quantize_onsets(onsets, measure_time, subdivision_level):
    subdivision_interval = measure_time / subdivision_level
    grid_points = np.arange(0, measure_time + subdivision_interval, subdivision_interval)
    quantized_onsets = [min(grid_points, key=lambda x: abs(x - onset)) for onset in onsets]
    return quantized_onsets

intervals = calculate_intervals(onsets)
min_interval = find_minimum_interval(intervals)
ideal_subdivision = find_best_subdivision_level(measure_time, min_interval)
quantized_onsets = quantize_onsets(onsets, measure_time, ideal_subdivision)

print(f"Ideal Subdivision Level: {ideal_subdivision}")
print(f"Quantized Onsets: {quantized_onsets}")
