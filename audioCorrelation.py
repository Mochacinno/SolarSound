import librosa
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

y_within, sr_within = librosa.load("nATALIE.mp3", sr=None)
y_find, _ = librosa.load("nATALIECUT2.mp3", sr=None)

c = signal.correlate(y_within, y_find, mode='full', method='fft')

# Calculate time values in seconds
time_values = np.arange(len(c)) / sr_within

# Plot the scatter of correlation values by time
plt.figure(figsize=(10, 6))
plt.scatter(time_values[::100], c[::100], s=10, color='blue', alpha=0.5)
plt.xlabel('Time (seconds)')
plt.ylabel('Correlation Value')
plt.title('Correlation Values by Time')
plt.grid(True)
plt.show()
