import sounddevice as sd
import soundfile as sf
import librosa
import numpy as np

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
    power = 3 # usually is 2

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