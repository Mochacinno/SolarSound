import numpy as np
from sklearn.cluster import KMeans

# Non-quantized onsets in one measure
onsets_in_measure = [10875, 10945, 11059, 11274, 11379, 11508, 11593, 11738, 11853, 11992, 12102, 12167, 12252, 12381, 12426, 12496]

# Step 1: Calculate time differences between consecutive onsets
intervals = np.diff(onsets_in_measure)
print("Intervals between onsets:", intervals)

# Step 2: Use K-means clustering to find significant interval lengths
def find_clustering_intervals(intervals, n_clusters=3):
    intervals_reshaped = intervals.reshape(-1, 1)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(intervals_reshaped)
    cluster_centers = kmeans.cluster_centers_.flatten()
    return cluster_centers

cluster_centers = find_clustering_intervals(intervals)
print(f"Cluster Centers: {cluster_centers}")

# Step 3: Choose the smallest cluster center as the ideal subdivision
ideal_subdivision = min(cluster_centers)
print(f"Ideal Subdivision Level (from clustering): {ideal_subdivision}")

# Step 4: Determine practical subdivisions based on ideal_subdivision and musical context
# We will look for subdivisions that are multiples of ideal_subdivision and practical in a musical sense.
def find_practical_subdivision(ideal_subdivision):
    possible_subdivisions = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64]  # Common musical subdivisions
    practical_subdivision = ideal_subdivision
    for ps in possible_subdivisions:
        if ps * ideal_subdivision <= max(intervals):
            practical_subdivision = ps * ideal_subdivision
    return practical_subdivision

practical_subdivision = find_practical_subdivision(ideal_subdivision)
print(f"Practical Subdivision Level: {practical_subdivision}")

# Step 5: Quantize the onsets to the practical subdivision
quantized_onsets = [round(onset / practical_subdivision) * practical_subdivision for onset in onsets_in_measure]
print("Quantized Onsets:", quantized_onsets)
