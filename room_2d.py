"""2D rectangular room model for acoustic simulation.

Defines a room (floor plan), a source and receiver position,
path_length() for direct distance, image-source positions for first-order
reflections, and reflection_paths_first_order() for delay and gain of each
path. Used as the basis for RIR computation. Units are feet; acoustics
constants (speed of sound, reflection coefficient) come from constants.
"""

import math
from constants import SPEED_OF_SOUND, EPSILON, REFLECTION_COEFFICIENT


class Source2D:
    """A point source in 2D (e.g. speaker position)."""

    def __init__(self, position: tuple[float, float]) -> None:
        """Set source position in feet. position is (x, y)."""
        self.x = position[0]
        self.y = position[1]


class Receiver2D:
    """A receiver/listener position in 2D."""

    def __init__(self, position: tuple[float, float]) -> None:
        """Set receiver position in feet. position is (x, y)."""
        self.x = position[0]
        self.y = position[1]


class Room2D:
    """Rectangular 2D room with one source and one receiver.

    Room spans (0, 0) to (width, length) in feet. Used for
    geometric acoustics (image-source, path lengths).
    """

    def __init__(
        self,
        width: float,
        length: float,
        source: Source2D,
        receiver: Receiver2D,
    ) -> None:
        """Create a room with dimensions and source/receiver positions.

        Args:
            width: Room width (x) in feet.
            length: Room length (y) in feet.
            source: Source position.
            receiver: Receiver position.
        """
        self.x = 0 - width / 2
        self.y = 0
        self.width = width
        self.length = length
        if source.x > self.x and source.x < self.x + self.width and source.y < self.y and source.y > self.y - self.length:
            self.source = source
        else:
            raise ValueError("Source position is outside of the room.")
        if receiver.x > self.x and receiver.x < self.x + self.width and receiver.y < self.y and receiver.y > self.y - self.length:
            self.receiver = receiver
        else:
            raise ValueError("Receiver position is outside of the room.")
    
    def image_sources_first_order(self) -> list[Source2D]:
        """First-order image sources: one reflection off each of the four walls.

        For each wall, the source is mirrored across that wall to form an
        "image source." The straight-line distance from an image to the
        receiver equals the reflected path length (source → wall → receiver).
        Used to compute delays and levels for early reflections in the RIR.

        Returns:
            List of four Source2D positions, in order: left, bottom, right, top.
            The distance from each image to ``self.receiver`` (via path_length)
            is the one-bounce path length for that wall.
        """
        image_sources = []

        source = self.source

        left_wall = {'x': self.x}
        bottom_wall = {'y': self.y - self.length}
        right_wall = {'x': self.x + self.width}
        top_wall = {'y': self.y}

        walls = [left_wall, bottom_wall, right_wall, top_wall]
        for wall in walls:
            if 'x' in wall.keys():
                source_x_distance = abs(wall['x'] - source.x)
                if wall['x'] > source.x:
                    image_x = wall['x'] + source_x_distance
                else:
                    image_x = wall['x'] - source_x_distance
                image_y = source.y
            if 'y' in wall.keys():
                source_y_distance = abs(wall['y'] - source.y)
                if wall['y'] > source.y:
                    image_y = wall['y'] + source_y_distance
                else:
                    image_y = wall['y'] - source_y_distance
                image_x = source.x
            
            image_sources.append(Source2D(position=(image_x, image_y)))
        
        return image_sources

    @property
    def direct_path_length(self) -> float:
        """Direct path length from source to receiver (same units as room)."""
        return path_length(self.source, self.receiver)

    def reflection_paths_first_order(self) -> list[dict[str, float]]:
        """Delay and gain for direct path plus four first-order reflections.

        Uses inverse-distance law for gain and a per-bounce reflection
        coefficient for reflected paths. Speed of sound and coefficients
        are taken from the constants module.

        Returns:
            List of 5 dicts, each with keys ``'delay'`` (seconds) and
            ``'gain'`` (linear). Order: direct, then left, bottom, right,
            top wall reflections. Use this list to build the RIR (place
            a dirac at each delay with the corresponding gain).
        """
        image_sources = self.image_sources_first_order()

        paths = []

        direct_path_length = self.direct_path_length
        direct_delay = direct_path_length / SPEED_OF_SOUND
        direct_gain = 1 / (direct_path_length + EPSILON)
        paths.append({'delay': direct_delay, 'gain': direct_gain})

        for image_source in image_sources:
            image_path_length = path_length(image_source, self.receiver)
            image_delay = image_path_length / SPEED_OF_SOUND
            image_gain = 1 / (image_path_length + EPSILON) * REFLECTION_COEFFICIENT
            paths.append({'delay': image_delay, 'gain': image_gain})
        
        return paths



def path_length(p1: Source2D | Receiver2D, p2: Source2D | Receiver2D) -> float:
    """Euclidean distance between two 2D points in feet.

    Args:
        p1: First point (source or receiver).
        p2: Second point (source or receiver).

    Returns:
        Distance in feet.
    """
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)


if __name__ == "__main__":
    # Sanity checks for reflection_paths_first_order (Task 1.4)
    room = Room2D(
        width=5.0,
        length=4.0,
        source=Source2D((-1.0, -2.0)),
        receiver=Receiver2D((1.0, -1.0)),
    )
    paths = room.reflection_paths_first_order()
    assert len(paths) == 5, f"expected 5 paths, got {len(paths)}"
    direct = paths[0]
    assert "delay" in direct and "gain" in direct
    assert direct["delay"] > 0 and direct["gain"] > 0
    for i, p in enumerate(paths[1:], start=1):
        assert p["delay"] >= direct["delay"], f"path {i} delay should be >= direct"
        assert p["gain"] <= direct["gain"], f"path {i} gain should be <= direct"
    expected_delay = room.direct_path_length / SPEED_OF_SOUND
    expected_gain = 1 / (room.direct_path_length + EPSILON)
    assert abs(direct["delay"] - expected_delay) < 1e-12
    assert abs(direct["gain"] - expected_gain) < 1e-12
    print("reflection_paths_first_order: all checks passed.")