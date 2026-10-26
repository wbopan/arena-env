# Master a prepared dubbing take

The input `/root/work/dialogue.wav` is a stereo, 16-bit PCM WAV at 16000 Hz. Its two channels are recordings of the same prepared dubbing take. Produce exactly one output file: `/root/work/mastered.wav`, a mono, 16-bit PCM WAV at 16000 Hz with the same number of frames. Do not add or remove silence.

For each input frame, interpret each channel's signed integer sample as its value divided by 32768, then average the two channel values to form a mono sample. Define active samples as those whose absolute mono value is at least 0.015. Compute the RMS over active samples only. Choose the smaller of two positive gains: the gain that makes this RMS equal to -20 dBFS, and the gain that makes the largest absolute mono sample equal to -3 dBFS. Here a level in dBFS is `20 * log10(linear amplitude)`.

Apply that gain to every mono sample. Finally, apply an 80-frame linear fade at each boundary: multiply frame `i`, for `0 <= i < 80`, by `i/80`; multiply frame `N-1-i` by `i/80`. The fades do not overlap. Convert to PCM by multiplying by 32768, rounding to the nearest integer with ties to even, and clipping to the signed 16-bit range. No metadata or additional output is requested.
