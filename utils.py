import sounddevice as sd
import soundfile as sf
import librosa
import numpy as np

def bpm_for_time(bpms, current_time):
    for i in range(1, len(bpms)):
        if current_time < bpms[i][1]:
            return bpms[i - 1][0]
    return bpms[-1][0]  # Return the last BPM if current_time is beyond the last BPM change start time

def createClickTrack(y, sr, clicks, name):
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
    power = 2 # usually is 2

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

    y_foreground = librosa.istft(S_foreground * phase)
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