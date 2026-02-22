# Task 1.4 expansion: Delay and gain for each path

## Goal

For the **direct path** (source → receiver) and the **four first-order reflection paths** (source → wall → receiver), compute:

1. **Delay** (seconds): time for sound to travel that path.
2. **Level** (linear gain): how much the signal is attenuated (inverse distance + optional reflection loss).

Produce a single list of **5** items: `(delay_sec, gain_linear)` — one for direct, four for the first-order reflections. This list is exactly what you need in task 1.5 to build the RIR (place a dirac at each delay with that gain).

---

## 1. Path lengths

You need **5 path lengths** (in the same units as your room, e.g. feet):

- **Direct:** `path_length(room.source, room.receiver)`.
- **Four reflections:** For each image from `room.image_sources_first_order()`, the path length is the distance from that image point to the receiver. Your current `path_length(p1, p2)` expects objects with `.x` and `.y`. So either:
  - Add a small helper that takes two coordinate pairs and returns distance, e.g.  
    `path_length_xy(x1, y1, x2, y2) -> float`  
    and use it as `path_length_xy(img['x'], img['y'], room.receiver.x, room.receiver.y)`, or
  - Build a minimal object (e.g. a type with `.x` and `.y` from the image dict) and call your existing `path_length`.

Use one consistent unit (feet or metres) for all path lengths; the next step uses speed of sound in that same unit.

---

## 2. Delay (seconds)

Formula:

```text
delay_sec = path_length / speed_of_sound
```

**Speed of sound** (use one consistently with your room units):

- In **metres per second:** `343` m/s (common default).
- In **feet per second:** `1125` ft/s (approx).

If your room is in feet, use **1125** so that `path_length` in feet gives delay in seconds. If you prefer to work in metres, convert path lengths to metres first (e.g. divide by 3.281) and use **343**.

Example: path length 10 ft → delay = 10 / 1125 ≈ 0.00889 s.

---

## 3. Gain (linear)

Two parts:

**a) Inverse-distance law (geometric spreading)**  
Sound level drops with distance. A simple model is linear gain proportional to 1/distance:

```text
gain_linear = 1 / (path_length + eps)
```

Use a small `eps` (e.g. `1e-6`) to avoid division by zero. You can later scale this (e.g. so direct path has gain 1.0) when building the RIR; for task 1.4, using `1 / (path_length + eps)` is enough.

**b) Reflection loss (first-order paths only)**  
Each bounce off a wall reduces level. Model this with a **reflection coefficient** per bounce (e.g. `0.7` = 70% reflected, 30% absorbed). So for a **reflected** path:

```text
gain_linear = (1 / (path_length + eps)) * reflection_coefficient
```

For the **direct** path there is no bounce, so do **not** multiply by the reflection coefficient.

Summary:

- **Direct path:** `gain = 1 / (path_length + eps)`.
- **Each first-order path:** `gain = (1 / (path_length + eps)) * reflection_coefficient`.

Typical `reflection_coefficient`: between `0.5` and `0.9` (hard walls). Use a constant (e.g. `0.7`) for all four walls for now; later you can assign different coefficients per wall.

---

## 4. What to implement

**Option A – Method on `Room2D`**

```text
def reflection_paths_first_order(
    self,
    speed_of_sound: float = 1125.0,   # ft/s if room in feet
    reflection_coefficient: float = 0.7,
    eps: float = 1e-6,
) -> list[tuple[float, float]]:
    """Return [(delay_sec, gain_linear), ...] for direct + four first-order paths."""
```

**Option B – Standalone function**

```text
def reflection_paths_first_order(
    room: Room2D,
    speed_of_sound: float = 1125.0,
    reflection_coefficient: float = 0.7,
    eps: float = 1e-6,
) -> list[tuple[float, float]]:
```

Return a list of **5** tuples: `(delay_sec, gain_linear)` in this order:

1. Direct path.
2. Left wall reflection.
3. Bottom wall reflection.
4. Right wall reflection.
5. Top wall reflection.

So: first element = direct; remaining four = same order as `image_sources_first_order()`.

---

## 5. Sanity checks

- **Delays:** Direct path should have the **smallest** delay; reflected paths should have **larger** delays (longer paths).
- **Gains:** Direct path gain should be **larger** than any reflected path (reflections have extra loss from the reflection coefficient).
- **Units:** If you use path length in feet and speed 1125 ft/s, delays will be in seconds. Typical room: direct delay on the order of a few milliseconds (e.g. 0.005 s for ~5 ft).

---

## 6. Summary

| Step | Action |
|------|--------|
| 1 | Get direct path length: `path_length(room.source, room.receiver)`. |
| 2 | Get four reflection path lengths: distance from each image `(img['x'], img['y'])` to `(room.receiver.x, room.receiver.y)` (add `path_length_xy` or equivalent). |
| 3 | For each of the 5 path lengths: `delay_sec = path_length / speed_of_sound`. |
| 4 | For each: `gain = 1 / (path_length + eps)`; for the 4 reflections multiply by `reflection_coefficient`. |
| 5 | Return `[(delay_direct, gain_direct), (delay_left, gain_left), ...]` (5 tuples). |

This list is the input for task 1.5: build the RIR by placing a dirac at each delay with the corresponding gain.
