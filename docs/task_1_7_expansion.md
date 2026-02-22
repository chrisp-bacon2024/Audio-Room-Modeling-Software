# Task 1.7 expansion: Second-order image sources

## Goal

Add **second-order** reflections: paths that bounce off **two** walls before reaching the receiver. You get more image sources (up to 16 for a rectangle), each with a longer path and lower gain (reflection coefficient applied twice). Then feed these into the same RIR pipeline so the plot shows more, later spikes.

---

## 1. What second-order means

- **First-order:** Source mirrored across **one** wall → 4 images (left, bottom, right, top).
- **Second-order:** Take **each** of those 4 first-order images and mirror it across **each** of the 4 walls again → 4 × 4 = **16** second-order images. Each represents a path: source → wall A → wall B → receiver.

So you need: a way to mirror a **point** (x, y) across a **wall** (vertical or horizontal), then apply that twice: first to the real source (to get order 1), then to each order-1 image (to get order 2).

---

## 2. Should you add an n-order function?

**Yes.** A single function that returns image sources for **any** order keeps the logic in one place and makes task 1.8 (refactor with `max_order`) easy.

**Suggested API:**

- **Option A – Per-order function:**  
  `image_sources_for_order(self, order: int) -> list[Source2D]`  
  - `order == 1`: return the same 4 you have now (mirror `self.source` across each wall).  
  - `order == 2`: for each image in `image_sources_for_order(1)`, mirror it across all 4 walls; return the list of 16 (may contain duplicates; that’s OK or you can dedupe by position).  
  - `order > 2`: same idea (mirror each image from order n−1 across all 4 walls), but you’ll get many images.

- **Option B – Up-to-max-order:**  
  `image_sources(self, max_order: int) -> list[list[Source2D]]`  
  Returns a list of lists: `[order_0_images, order_1_images, order_2_images, ...]` where order_0 is empty or just used for direct. Then you flatten when building paths.

**Recommendation:** Add **`image_sources_for_order(self, order: int)`**. For order 1 you can either call your current logic or inline it. For order 2, loop over the 4 first-order images and mirror each across all 4 walls (16 results). That avoids changing the existing `image_sources_first_order` signature and gives a clear place for second-order. Later you can refactor so `reflection_paths(max_order)` calls `image_sources_for_order(1)`, `image_sources_for_order(2)`, … and aggregates.

---

## 3. Mirror helper

To avoid duplicating mirror math, add a small helper that mirrors a point across one wall:

- **Input:** A point `(x, y)` and which wall (e.g. wall index 0..3 or wall type: left / right / bottom / top).
- **Output:** New point `(x', y')` after mirroring.

Your current code already does this inline (vertical wall: mirror x, keep y; horizontal: keep x, mirror y). Extract that into e.g. `_mirror_point_across_wall(self, point: Source2D, wall_index: int) -> Source2D`. The four walls can be the same list you use now (left, bottom, right, top). Then first-order: mirror `self.source` across wall 0, 1, 2, 3. Second-order: for each first-order image, mirror across wall 0, 1, 2, 3.

---

## 4. Gain for second-order

Each second-order path bounces **twice**, so apply the reflection coefficient **twice**:

- **First-order gain:** `gain = (1 / (path_length + eps)) * REFLECTION_COEFFICIENT` (one bounce).
- **Second-order gain:** `gain = (1 / (path_length + eps)) * REFLECTION_COEFFICIENT ** 2` (two bounces).

So when you build the list of (delay, gain) for second-order images, use `REFLECTION_COEFFICIENT ** 2` instead of `REFLECTION_COEFFICIENT`.

---

## 5. Validity (optional for Week 1)

Strictly speaking, not all 16 second-order images correspond to paths that actually stay inside the room (the reflection point on the second wall might be outside the segment). For a **simple** Week 1 implementation you can **skip** validity: add all 16 to the RIR with `coeff**2`. The result will still sound like “more reflections.” You can add a validity check later (e.g. require that the path from image to receiver crosses the room).

---

## 6. What to implement

| Step | Action |
|------|--------|
| 1 | Add a helper: mirror a point across a wall (by wall index or type). Same math as now, just parameterised. |
| 2 | Add `image_sources_for_order(self, order: int) -> list[Source2D]`. For order 1, return current 4. For order 2, get the 4 first-order images, then for each mirror across all 4 walls; return the 16 (or fewer if you dedupe). |
| 3 | Extend path building: either a new method `reflection_paths(self, max_order=2)` or a separate function that takes the room and max_order, calls `image_sources_for_order(1)` and `image_sources_for_order(2)`, computes path length and delay/gain for each (using `REFLECTION_COEFFICIENT ** order` for reflections), and returns one flat list of (delay, gain) including direct. |
| 4 | Build RIR from that list (same `build_rir` as now) and plot. You should see 1 + 4 + 16 = 21 spikes (or fewer if you filter), with later ones smaller. |

---

## 7. Summary

- **Second-order:** 16 images (each first-order image mirrored across all 4 walls). Delay = path_length / speed_of_sound; gain = (1 / (path_length + eps)) * REFLECTION_COEFFICIENT ** 2.
- **n-order function:** Yes — implement `image_sources_for_order(order)` and a mirror helper so you can grow to higher orders or refactor to `reflection_paths(max_order)` in task 1.8.
- **RIR:** Reuse `build_rir` and `plot_rir`; pass the combined list of (delay, gain) from direct + order 1 + order 2.
