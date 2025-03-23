import os
import numpy as np
import cantera as ct

from mendeleev import element

# Define directories and other system variables
SCRIPT_DIR          = os.path.dirname(os.path.realpath(__file__))
MECHANISM_DIR       = os.path.join(SCRIPT_DIR, 'data/Nitrogen/Glarborg/')
Glarborg           = os.path.join(MECHANISM_DIR, 'Glarborg.yaml')


def main():
    EQR_GLOBAL  = 0.4
    EQR_RICH    = np.linspace(1.0, 1.3, 11)

    o_mass = element('O').mass
    h_mass = element('H').mass
    n_mass = element('N').mass


    AF_STOIC = (3 * (o_mass * 2 + 3.76 * n_mass * 2)) / (4 * (n_mass + 3 * h_mass))
    print(AF_STOIC)
    

    return tad

def calc_AirProperties():
    # Given
    T_FUEL: float = 298.0  # [K]
    P_FUEL: float = 2e+6 # [Pa]

    T_AIR: float = 700.0
    P_AIR: float = 15e5    # [Pa] = 15 bar

    # Constants
    R_UNIV = 8.314462618  # J/(mol·K)

    # Molecular weights (kg/mol)
    MW_O2  = Formula('O2').mass * 1e-3
    MW_N2  = Formula('N2').mass * 1e-3
    MW_H2  = Formula('H2').mass * 1e-3


    MW_AIR  = 0.21 * MW_O2 + 0.79 * MW_N2
    MW_FUEL = 2.0 * MW_H2

    # Specific gas constants (J/kg.K)
    R_AIR  = R_UNIV / MW_AIR
    R_FUEL = R_UNIV / MW_H2

    # Densities [kg/m^3]
    DENSITY_AIR  = P_AIR  / (R_AIR  * T_AIR)
    DENSITY_FUEL = P_FUEL / (R_FUEL * T_FUEL)

    print(f"{'Quantity':<20} {'Value':>15} {'Unit':<10}")
    print("-" * 50)
    print(f"{'Air Density':<20} {DENSITY_AIR:>15.6f} {'kg/m3':<10}")
    print(f"{'Air Temperature':<20} {T_AIR:>15.1f} {'K':<10}")
    print(f"{'Air Pressure':<20} {P_AIR:>15.1f} {'Pa':<10}")
    print("-" * 50)
    print(f"{'Fuel Density':<20} {DENSITY_FUEL:>15.6f} {'kg/m3':<10}")
    print(f"{'Fuel Temperature':<20} {T_FUEL:>15.1f} {'K':<10}")
    print(f"{'Fuel Pressure':<20} {P_FUEL:>15.1f} {'Pa':<10}")
    print("-" * 50)

    return DENSITY_AIR, DENSITY_FUEL, MW_AIR, MW_FUEL



if __name__ == '__main__':
    main()