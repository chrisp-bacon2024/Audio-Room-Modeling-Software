"""2D rectangular room model for acoustic simulation.

Defines a room (floor plan), a source and receiver position, and
path_length() for direct distance in feet. Used as the basis for
image-source and RIR computation.
"""

import math


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
    
    def image_sources_first_order(self) -> list[dict[str, float]]:
        """First-order image sources: one reflection off each of the four walls.

        For each wall, the source is mirrored across that wall to form an
        "image source." The straight-line distance from an image to the
        receiver equals the reflected path length (source → wall → receiver).
        Used to compute delays and levels for early reflections in the RIR.

        Returns:
            List of four image positions, in order: left, bottom, right, top.
            Each element is a dict with keys ``'x'`` and ``'y'`` (same units
            as the room, e.g. feet). The distance from ``(img['x'], img['y'])``
            to ``self.receiver`` is the one-bounce path length for that wall.
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
            
            image_sources.append({'x': image_x, 'y': image_y})
        
        return image_sources



def path_length(p1: Source2D | Receiver2D, p2: Source2D | Receiver2D) -> float:
    """Euclidean distance between two 2D points in feet.

    Args:
        p1: First point (source or receiver).
        p2: Second point (source or receiver).

    Returns:
        Distance in feet.
    """
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)