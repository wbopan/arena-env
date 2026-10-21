import json
from pathlib import Path

import numpy as np
import pytest
from scipy.signal import welch

W = Path("/root/work")
OUT = W / "psd_report.json"
FS = 1024.0
BANDS = [(20, 40), (40, 80), (80, 160), (160, 320)]


def expected():
    x = np.load(W / "strain.npy").astype(np.float64)
    h = np.load(W / "template.npy").astype(np.float64)
    fw, P = welch(x, fs=FS, window="hann", nperseg=512, noverlap=256,
                  detrend="constant", return_onesided=True, scaling="density", average="mean")
    m = (fw >= 20) & (fw <= 400)
    line = float(fw[m][np.argmax(P[m])])
    asd = [float(np.sqrt(np.mean(P[(fw >= lo) & (fw < hi)]))) for lo, hi in BANDS]
    n = len(h)
    hf = np.fft.rfft(h) / FS
    ff = np.arange(len(hf)) * (FS / n)
    S = np.interp(ff, fw, P)
    k = (ff >= 20) & (ff <= 400)
    snr = float(np.sqrt(4.0 * np.sum(np.abs(hf[k]) ** 2 / S[k]) * (FS / n)))
    return line, asd, snr


@pytest.fixture(scope="module")
def out():
    assert OUT.exists(), "psd_report.json missing"
    return json.loads(OUT.read_text())


def test_file_exists():
    assert OUT.exists()


def test_schema(out):
    for key in ("line_frequency_hz", "band_asd", "optimal_snr"):
        assert key in out
    b = out["band_asd"]
    assert len(b) == 4
    for e, (lo, hi) in zip(b, BANDS):
        assert float(e["f_low"]) == lo and float(e["f_high"]) == hi
        assert "asd" in e


def test_line_frequency(out):
    line, _, _ = expected()
    assert abs(float(out["line_frequency_hz"]) - line) < 0.01


def test_band_asd(out):
    _, asd, _ = expected()
    for e, a in zip(out["band_asd"], asd):
        assert abs(float(e["asd"]) - a) <= 1e-3 * abs(a), (e, a)


def test_optimal_snr(out):
    _, _, snr = expected()
    assert abs(float(out["optimal_snr"]) - snr) <= 1e-3 * abs(snr), (out["optimal_snr"], snr)
