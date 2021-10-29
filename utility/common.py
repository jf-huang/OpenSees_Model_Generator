"""
Common definitions
"""

# very big, very small numbers used for
# comparing floats and hashing
EPSILON = 1.00E-6
ALPHA = 10000000.00

# gravitational acceleration
G_CONST = 386.22  # in/s**2

# quantities to use for extreme stiffnesses
STIFF_ROT = 1.0e12
STIFF = 1.0e12  # note: too high a value causes convergence problems
TINY = 1.0e-12
