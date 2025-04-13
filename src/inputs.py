import numpy as np

# Geometrical Inputs
R_AIR_OUTER     =   7/1000      # [m]
R_AIR_INNER     =   3.934/1000       # [m]
R_FUEL          =   1.6/2000         # [m]

A_AIR           =   np.pi * (R_AIR_OUTER**2 - R_AIR_INNER**2)
N_FUEL_HOLES    =   6
A_FUEL          =   np.pi * R_FUEL**2 * N_FUEL_HOLES


# Fuel and Air propertirs
# Given
T_FUEL: float = 500  # [K]
P_FUEL: float = 1.5e+6 # [Pa] = 15 bar = 1.5 MPa

T_AIR: float = 800
P_AIR: float = 1.2e+6    # [Pa] = 12 bar = 1.2 MPa