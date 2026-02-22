# Task 1.5 expansion: Build and plot the RIR

## Goal

Turn the list of 5 paths from `reflection_paths_first_order()` (each with `delay` in seconds and `gain` in linear amplitude) into a **discrete room impulse response (RIR)**: a 1D array where each path is a **dirac** (a single sample with that gain at the time corresponding to that delay). Sum all diracs into one RIR, then plot it (time in ms vs amplitude). This RIR can later be convolved with a dry signal to hear the "room."

---

## 1. From delay (seconds) to sample index

- **Sample rate:** e.g. 48000 Hz (48 kHz). Use a constant or parameter.
- **Formula:** For a path with `delay` in seconds,
  ```text
  sample_index = round(delay * sample_rate)
  ```
  So delay 0.005 s at 48 kHz → index 240. Keep `sample_index` as an integer (no fractional indexing).

- **Bounds:** If `sample_index` is past the end of your RIR array, skip that path or extend the array. Typically you choose an RIR **length** first (e.g. 0.5 s or 1.0 s), so `num_samples = round(length_sec * sample_rate)`, and you only add a dirac if `sample_index < num_samples`.

---

## 2. Building the RIR array

- Start with an array of zeros: length = `num_samples` (e.g. `length_sec * sample_rate`).
- For each path in the list from `reflection_paths_first_order()`:
  - `delay_sec = path["delay"]`, `gain = path["gain"]`.
  - `idx = round(delay_sec * sample_rate)`.
  - If `0 <= idx < num_samples`, add the gain to that sample: `rir[idx] += gain`.
- **Why add?** If two paths had the same delay (unlikely in first-order), they would sum. For first-order with distinct delays, each index gets at most one contribution.

**Output:** A 1D numpy array (or list) of length `num_samples`, with a few non-zero values (one per path) and zeros elsewhere.

---

## 3. Optional: normalize the RIR

- You can leave the RIR as-is (direct path will have the largest value).
- Or **normalize** so the direct peak is 1.0: find the max absolute value, then `rir = rir / max_val`. That makes the direct path hit 1.0 and reflections proportionally smaller; useful for plotting and for convolution later.

---

## 4. Plotting

- **X-axis:** Time in **milliseconds**. For sample index `n`, time in seconds is `n / sample_rate`, so time in ms is `(n / sample_rate) * 1000`. Use a time vector: `times_ms = (np.arange(num_samples) / sample_rate) * 1000`.
- **Y-axis:** Amplitude (the RIR values).
- Use **matplotlib**: `plt.plot(times_ms, rir)` or `plt.stem(times_ms, rir)` for a spike view. Label axes ("Time (ms)", "Amplitude"), add a title ("Room impulse response (first order)").

You should see: one spike at t ≈ 0 (direct), then a few later spikes (early reflections). The direct spike should be tallest if you didn’t normalize by the direct only.

---

## 5. What to implement

**Suggested functions (e.g. in a new file `rir.py` or in the same module):**

| Function | Purpose |
|----------|--------|
| `build_rir(paths, sample_rate, length_sec)` | `paths` is the list of 5 dicts from `reflection_paths_first_order()`. Return 1D array of length `length_sec * sample_rate`. Place gain at `round(delay * sample_rate)` for each path. |
| `plot_rir(rir, sample_rate)` | Plot RIR: time (ms) vs amplitude. Optional: save figure to file. |

**Signatures:**

```python
def build_rir(
    paths: list[dict[str, float]],
    sample_rate: int = 48000,
    length_sec: float = 0.5,
) -> np.ndarray:
    """Build RIR from list of {'delay': sec, 'gain': linear}."""

def plot_rir(rir: np.ndarray, sample_rate: int = 48000) -> None:
    """Plot RIR with time in ms on x-axis."""
```

**Typical usage:**

```python
room = Room2D(...)
paths = room.reflection_paths_first_order()
rir = build_rir(paths, sample_rate=48000, length_sec=0.5)
plot_rir(rir, sample_rate=48000)
```

---

## 6. Sanity checks

- **Length:** RIR length in samples = `length_sec * sample_rate` (e.g. 0.5 * 48000 = 24000).
- **Non-zero count:** You should have 5 non-zero (or near-zero) spikes for first-order; the rest zeros.
- **Plot:** Direct path (first spike) at left; reflections to the right, with increasing delay. Delays should match the path lengths (e.g. a path 10 ft long → delay ≈ 10/1125 ≈ 8.9 ms at 1125 ft/s).

---

## 7. Summary

| Step | Action |
|------|--------|
| 1 | Choose `sample_rate` (e.g. 48000) and `length_sec` (e.g. 0.5). |
| 2 | Allocate array of zeros, length = `length_sec * sample_rate`. |
| 3 | For each path: `idx = round(delay * sample_rate)`; if in range, `rir[idx] += gain`. |
| 4 | Optionally normalize so max value is 1.0. |
| 5 | Plot: x = time in ms, y = RIR amplitude. |

Task 1.6 (optional) is to export this RIR as a WAV file so you can load it in Ableton and use it as an impulse for a convolution reverb.
