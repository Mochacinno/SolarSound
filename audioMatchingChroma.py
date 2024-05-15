import numpy as np
from math import sqrt
import librosa
import matplotlib.pyplot as plt

# Load audio file and extract chroma features
y, sr = librosa.load("nATALIE.mp3")
y = librosa.effects.harmonic(y=y)
chroma = librosa.feature.chroma_stft(y=y, sr=sr)

def compute_similarity_matrix_slow(chroma):
    """Slow but straightforward way to compute time time similarity matrix"""
    num_samples = chroma.shape[1]
    time_time_similarity = np.zeros((num_samples, num_samples))
    for i in range(num_samples):
        for j in range(num_samples):
            # For every pair of samples, check similarity
            time_time_similarity[i, j] = 1 - (
                np.linalg.norm(chroma[:, i] - chroma[:, j]) / sqrt(12))

    return time_time_similarity


matrix = compute_similarity_matrix_slow(chroma)

librosa.display.specshow(matrix, y_axis='time', x_axis='time', sr=sr)
plt.colorbar()
plt.set_cmap("hot_r")
plt.show()