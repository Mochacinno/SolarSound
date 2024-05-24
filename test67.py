import numpy as np

# Measure time in seconds
measure_time = 3.2272496629488905

# Onset times in seconds within the measure
onsets = [3.23, 3.48, 3.65, 4.11, 4.41, 4.74, 5.04, 5.34, 5.5, 5.64]

def quantize_onsets(onsets, measure_time, max_subdivision):
    # Calculate the time interval for each subdivision
    subdivision_interval = measure_time / max_subdivision
    print(subdivision_interval)

    # Calculate the grid points within the range of onset_start to onset_end
    grid_points = np.arange(min(onsets), max(onsets) + subdivision_interval, subdivision_interval)
    
    # Quantize the onsets to the nearest grid point
    quantized_onsets = [min(grid_points, key=lambda x: abs(x - onset)) for onset in onsets]

    return quantized_onsets

def calculate_total_error(onsets, quantized_onsets):
    # Calculate the total quantization error
    return sum(abs(o - q) for o, q in zip(onsets, quantized_onsets))

# Define possible subdivisions to test (e.g., 1/4th, 1/8th, 1/16th notes)
subdivision_levels = [4, 8, 16, 32, 64]  # Corresponds to 1/4, 1/8, 1/16, 1/32 notes

best_subdivision = None
min_error = float('inf')
best_quantized_onsets = None

for subdivision in subdivision_levels:
    quantized_onsets = quantize_onsets(onsets, measure_time, subdivision)
    error = calculate_total_error(onsets, quantized_onsets)
    print(f"Subdivision: {subdivision}, Error: {error}, Quantized Onsets: {quantized_onsets}")

    if error < min_error:
        min_error = error
        best_subdivision = subdivision
        best_quantized_onsets = quantized_onsets



print(f"Best Subdivision: {best_subdivision}, Minimum Error: {min_error}")
print(f"Best Quantized Onsets: {best_quantized_onsets}")
