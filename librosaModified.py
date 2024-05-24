import numpy as np
import librosa

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
            #print("yes")
        else:
            best_period[i] = top_3_periods[0, i]

    tempo_est = np.take(bpms, best_period)
    return tempo_est