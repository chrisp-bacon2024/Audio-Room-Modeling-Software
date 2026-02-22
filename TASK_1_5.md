# Task 1.5 expansion: Build and plot the RIR

## Goal

Turn the 5 paths from `reflection_paths_first_order()` (each with `delay` in seconds and `gain` linear) into a **discrete RIR**: a 1D array where each path is a **dirac** (one sample with that gain at that delay). Sum into one array, then plot time (ms) vs amplitude.

---

## 1. Delay to sample index

- Sample rate: e.g. **48000 Hz**.
- `sample_index = round(delay * sample_rate)` (integer).
- RIR length: e.g. **0.5 s** → `num_samples = round(0.5 * 48000)`. Only add a dirac if `0 <= sample_index < num_samples`.

---

## 2. Build the RIR

- Start with zeros: length `num_samples`.
- For each path: `idx = round(path["delay"] * sample_rate)`; if in range, `rir[idx] += path["gain"]`.
- Optional: normalize so max value is 1.0.

---

## 3. Plot

- X-axis: time in **ms**: `(np.arange(num_samples) / sample_rate) * 1000`.
- Y-axis: RIR amplitude.
- Use `matplotlib`: `plt.plot(times_ms, rir)` or `plt.stem(times_ms, rir)`.

You should see one spike (direct) then four later spikes (reflections).

---

## 4. Functions to implement

| Function | Purpose |
|----------|--------|
| `build_rir(paths, sample_rate=48000, length_sec=0.5)` | Return 1D array; paths = list of `{"delay": sec, "gain": linear}`. |
| `plot_rir(rir, sample_rate=48000)` | Plot RIR with time in ms. |

**Usage:** `paths = room.reflection_paths_first_order()` → `rir = build_rir(paths)` → `plot_rir(rir)`.

---

## 5. Sanity checks

- 5 non-zero spikes; direct (first) at smallest delay; delays match path lengths (e.g. ~9 ms for 10 ft at 1125 ft/s).

Full detail: [docs/task_1_5_expansion.md](docs/task_1_5_expansion.md).
