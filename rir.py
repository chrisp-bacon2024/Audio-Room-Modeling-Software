import numpy as np
import matplotlib.pyplot as plt


def build_rir(paths: list[dict[str, float]], sample_rate: int = 48000, length_sec: float = 0.5) -> np.ndarray:
    rir = np.zeros(int(length_sec * sample_rate))
    for path in paths:
        idx = round(path["delay"] * sample_rate)
        if 0 <= idx < len(rir):
            rir[idx] += path['gain']
    
    max_value = np.max(np.abs(rir))
    if max_value > 0:
        rir = rir / max_value
    return rir

def plot_rir(rir: np.ndarray, sample_rate: int = 48000) -> None:
    times_ms = (np.arange(len(rir)) / sample_rate) * 1000
    plt.plot(times_ms, rir)
    plt.xlabel('Time (ms)')
    plt.ylabel('Amplitude')
    plt.title('Room Impulse Response')
    plt.show()

if __name__ == "__main__":
    from room_2d import Room2D, Source2D, Receiver2D
    room = Room2D(5.0, 4.0, Source2D((-1.0, -2.0)), Receiver2D((1.0, -1.0)))
    paths = room.reflection_paths_first_order()
    rir = build_rir(paths)
    # rir has length 24000, max 1.0, five spikes
    plot_rir(rir)  # opens plot window