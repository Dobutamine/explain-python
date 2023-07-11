import math


def calc_resistance_tube(diameter, length, viscosity=6):
    # resistance is calculated using Poiseuille's Law : R = (8 * n * L) / (PI * r^4)

    # we have to watch the units carefully where we have to make sure that the units in the formula are
    # resistance is in mmHg * s / l
    # L = length in meters from millimeters
    # r = radius in meters from millimeters
    # n = viscosity in mmHg * s from centiPoise

    # convert viscosity from centiPoise to mmHg * s
    n_mmhgs: float = viscosity * 0.001 * 0.00750062

    # convert the length to meters
    length_meters: float = length / 1000.0

    # calculate radius in meters
    radius_meters = diameter / 2 / 1000.0

    # calculate the resistance
    res: float = (8.0 * n_mmhgs * length_meters) / (math.pi *
                                                    math.pow(radius_meters, 4))

    # convert resistance of mmHg * s / mm^3 to mmHg *s / l
    res = res / 1000.0

    return res
