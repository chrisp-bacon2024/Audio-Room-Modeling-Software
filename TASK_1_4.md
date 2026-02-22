# Task 1.4 expansion: Delay and gain for each path

## Goal

For the **direct path** (source to receiver) and the **four first-order reflection paths** (source to wall to receiver), compute:

1. **Delay** (seconds): time for sound to travel that path.
2. **Level** (linear gain): how much the signal is attenuated (inverse distance + optional reflection loss).

Produce a single list of **5** items: `(delay_sec, gain_linear)` — one for direct, four for the first-order reflections. This list is the input for task 1.5 to build the RIR.

---

## 1. Path lengths

You need **5 path lengths** (same units as your room, e.g. feet):

- **Direct:** `path_length(room.source, room.receiver)`.
- **Four reflections:** For each image from `room.image_sources_first_order()`, the path length is the distance from that image point to the receiver. Your `path_length(p1, p2)` expects objects with `.x` and `.y`. So either:
  - Add a helper `path_length_xy(x1, y1, x2, y2) -> float` and use `path_length_xy(img['x'], img['y'], room.receiver.x, room.receiver.y)`, or
  - Build a minimal object with `.x` and `.y` from the image dict and call your existing `path_length`.

Use one consistent unit (feet or metres); the next step uses speed of sound in that same unit.

---

## 2. Delay (seconds)

Formula: `delay_sec = path_length / speed_of_sound`

**Speed of sound:**
- **Metres per second:** 343 m/s.
- **Feet per second:** 1125 ft/s (approx).

If your room is in feet, use 1125 so path length in feet gives delay in seconds.

Example: path length 10 ft → delay = 10 / 1125 ≈ 0.00889 s.

---

## 3. Gain (linear)

**a) Inverse-distance law:** `gain_linear = 1 / (path_length + eps)`  
Use small `eps` (e.g. 1e-6) to avoid division by zero.

**b) Reflection loss (first-order paths only):** Multiply by a reflection coefficient per bounce (e.g. 0.7). So for a **reflected** path:
`gain_linear = (1 / (path_length + eps)) * reflection_coefficient`

For the **direct** path do **not** multiply by the reflection coefficient.

Summary:
- **Direct path:** `gain = 1 / (path_length + eps)`.
- **Each first-order path:** `gain = (1 / (path_length + eps)) * reflection_coefficient`.

Use a constant (e.g. 0.7) for all four walls for now.

---

## 4. What to implement

Method on Room2D or standalone function:

`reflection_paths_first_order(self_or_room, speed_of_sound=1125.0, reflection_coefficient=0.7, eps=1e-6) -> list[tuple[float, float]]`

Return **5** tuples `(delay_sec, gain_linear)` in this order:
1. Direct path.
2. Left wall reflection.
3. Bottom wall reflection.
4. Right wall reflection.
5. Top wall reflection.

(Same order as `image_sources_first_order()` for the four reflections.)

---

## 5. Sanity checks

- Direct path has the **smallest** delay; reflected paths have **larger** delays.
- Direct path gain is **larger** than any reflected path (reflections have extra loss).

---

## 6. Summary table

| Step | Action |
|------|--------|
| 1 | Get direct path length: `path_length(room.source, room.receiver)`. |
| 2 | Get four reflection path lengths: distance from each image to receiver (add `path_length_xy` or equivalent). |
| 3 | For each of the 5: `delay_sec = path_length / speed_of_sound`. |
| 4 | For each: `gain = 1 / (path_length + eps)`; for the 4 reflections multiply by `reflection_coefficient`. |
| 5 | Return list of 5 tuples: direct first, then left, bottom, right, top. |
