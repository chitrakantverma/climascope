"""Latitude weights for regular, equally spaced longitude grids."""
from math import cos, isfinite, radians


def latitude_weights(latitudes):
    values = [float(value) for value in latitudes]
    if not values or any(not isfinite(value) or abs(value) > 90 for value in values):
        raise ValueError("Latitude must contain finite values between -90 and 90 degrees.")
    if len(set(values)) != len(values):
        raise ValueError("Duplicate latitude coordinates are not supported.")
    if len(values) > 2:
        steps = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        if any(abs(step - steps[0]) > max(1e-6, abs(steps[0]) * 1e-4) for step in steps):
            raise ValueError("Area weighting requires a regular latitude grid.")
    weights = [max(0.0, cos(radians(value))) if abs(value) < 90 else 0.0 for value in values]
    if sum(weights) <= 0:
        raise ValueError("The grid must contain latitude bands with positive area.")
    return weights
