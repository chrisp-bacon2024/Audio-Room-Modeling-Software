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

    def __init__(self, position: tuple[float, float], power: float = 100) -> None:
        """Set source position in feet. position is (x, y)."""
        self.x = position[0]
        self.y = position[1]
        self.power = power # in dB


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
        return self.image_sources_for_order(1)

    @property
    def direct_path_length(self) -> float:
        """Direct path length from source to receiver (same units as room)."""
        return path_length(self.source, self.receiver)
    
    def image_sources_for_order(self, order: int) -> list[Source2D]:
        """Image sources for a given order of reflections."""
        left_wall = {'x': self.x}
        bottom_wall = {'y': self.y - self.length}
        right_wall = {'x': self.x + self.width}
        top_wall = {'y': self.y}

        walls = [left_wall, bottom_wall, right_wall, top_wall]

        if order == 1:
            source = self.source
            image_sources = []
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
        else:
            prev_order_sources = self.image_sources_for_order(order - 1)
            current_order_sources = []
            for image_source in prev_order_sources:
                for wall in walls:
                    if "x" in wall.keys():
                        source_x_distance = abs(wall["x"] - image_source.x)
                        if wall["x"] > image_source.x:
                            image_x = wall["x"] + source_x_distance
                        else:
                            image_x = wall["x"] - source_x_distance
                        image_y = image_source.y
                    if "y" in wall.keys():
                        source_y_distance = abs(wall["y"] - image_source.y)
                        if wall["y"] > image_source.y:
                            image_y = wall["y"] + source_y_distance
                        else:
                            image_y = wall["y"] - source_y_distance
                        image_x = image_source.x
                    current_order_sources.append(Source2D(position=(image_x, image_y)))
            return current_order_sources

    def reflection_paths_for_order(self, order: int) -> list[dict[str, float]]:
        """Delay and gain for direct path plus all reflections up to and including this order.

        order=1 returns direct + 4 first-order paths (5 total). order=2 returns
        direct + 4 first-order + 16 second-order (21 total). Gain uses
        REFLECTION_COEFFICIENT ** num_bounces per path.
        """
        if order == 1:
            paths = []
            paths.append({
                "delay": self.direct_path_length / SPEED_OF_SOUND,
                "gain": 1 / (self.direct_path_length + EPSILON),
            })
            for img in self.image_sources_for_order(1):
                plen = path_length(img, self.receiver)
                paths.append({
                    "delay": plen / SPEED_OF_SOUND,
                    "gain": (1 / (plen + EPSILON)) * REFLECTION_COEFFICIENT,
                })
            return paths
        prev_paths = self.reflection_paths_for_order(order - 1)
        current_paths = []
        for image_source in self.image_sources_for_order(order):
            plen = path_length(image_source, self.receiver)
            current_paths.append({
                "delay": plen / SPEED_OF_SOUND,
                "gain": (1 / (plen + EPSILON)) * (REFLECTION_COEFFICIENT ** order),
            })
        return prev_paths + current_paths

def path_length(p1: Source2D | Receiver2D, p2: Source2D | Receiver2D) -> float:
    """Euclidean distance between two 2D points in feet.

    Args:
        p1: First point (source or receiver).
        p2: Second point (source or receiver).

    Returns:
        Distance in feet.
    """
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)