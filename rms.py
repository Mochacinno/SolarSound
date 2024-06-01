import librosa
import matplotlib.pyplot as plt
import numpy as np

song_name = "sink"
y, sr = librosa.load("Music+Beatmaps/"+song_name+".mp3")
## SLICE THE MUSIC
# Define start and end times in seconds
start_time = 0  # Start at 5 seconds
end_time = 120   # End at 10 seconds

# Convert start and end times to sample indices
start_sample = int(start_time * sr)
end_sample = int(end_time * sr)

# Slice the y array
y = y[start_sample:end_sample]

S = librosa.magphase(librosa.stft(y, window=np.ones, center=False))[0]
rms = librosa.feature.rms(S=S)

times = librosa.times_like(rms)

song_name = "lamp"
y, sr = librosa.load("Music+Beatmaps/"+song_name+".mp3")
## SLICE THE MUSIC
# Define start and end times in seconds
start_time = 0  # Start at 5 seconds
end_time = 120   # End at 10 seconds

# Convert start and end times to sample indices
start_sample = int(start_time * sr)
end_sample = int(end_time * sr)

# Slice the y array
y = y[start_sample:end_sample]

S = librosa.magphase(librosa.stft(y, window=np.ones, center=False))[0]
rms2 = librosa.feature.rms(S=S)

times2 = librosa.times_like(rms)

plt.plot(times, rms[0], label='RMS Energy')
plt.plot(times2, rms2[0], label='RMS Energy')
plt.show()