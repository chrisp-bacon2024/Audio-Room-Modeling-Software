import math
from room_2d import Source2D

def level_db_at_point(point: tuple[float, float], source: Source2D) -> float:
    pX = point[0]
    pY = point[1]
    sX = source.x
    sY = source.y
    sPower = source.power

    d1 = max(math.sqrt((pX - sX) ** 2 + (pY - sY) ** 2), 1e-6) # in feet

    sound_pressure = sPower - 20 * math.log10(d1) - 0.68 # in dB
    return sound_pressure

if __name__ == "__main__":
    source = Source2D((0, 1), 100)
    point = (0, 10)
    print(level_db_at_point(point, source))