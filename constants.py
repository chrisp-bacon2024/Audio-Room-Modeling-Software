"""Acoustics constants for 2D room model.

Used by room_2d when computing delays and gains. Room dimensions and
path lengths are in feet; speed of sound is in ft/s.
"""
SPEED_OF_SOUND = 1125.0  # feet per second
EPSILON = 1e-6  # avoid division by zero in gain = 1 / (path_length + eps)
REFLECTION_COEFFICIENT = 0.7  # per-bounce attenuation (0 = absorb, 1 = reflect)
