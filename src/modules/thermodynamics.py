from molmass import Formula
import cantera as ct

def calc_AdiabeticTemperature(phi, T_init:float=298.15, P_init:float=101325.0) -> float:

    # Define the cantera reaction mechanim
    gas = ct.Solution('h2o2.yaml')

    # Fuel species changed to hydrogen
    fuel_species = 'H2'

    # Set gas state for given phi
    gas.set_equivalence_ratio(phi, fuel_species, 'O2:1.0, N2:3.76')
    gas.TP = T_init, P_init

    # Equilibrate the mixture adiabatically at constant pressure
    gas.equilibrate('HP', solver='gibbs', max_steps=1000)

    tad = gas.T

    return tad

def calc_AirProperties():
    # Given
    T_FUEL: float = 300  # [K]
    P_FUEL: float = 3.0e+5 # [Pa]

    T_AIR: float = 1026.5
    P_AIR: float = 3.0e+5    # [Pa] = 25 bar

    # Constants
    R_UNIV = 8.314462618  # J/(mol·K)

    # Molecular weights (kg/mol)
    MW_O2       = Formula('O2').mass * 1e-3
    MW_N2       = Formula('N2').mass * 1e-3
    MW_NH3      = Formula('NH3').mass * 1e-3

    MW_AIR  = 3.0 * (0.21 * MW_O2 + 0.79 * MW_N2)
    MW_FUEL = 4.0 * MW_NH3

    # Specific gas constants (J/kg.K)
    R_AIR  = R_UNIV / MW_AIR
    R_FUEL = R_UNIV / MW_NH3

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


def calc_AirFuelRatio(MW_AIR:float, MW_FUEL:float, stoic:bool=False) -> float:
    """
    Calculates the air to fuel ratio for hydrogen and air combustion.
    """
    if stoic:
        AFR_STOIC = (MW_AIR / MW_FUEL)*4.76
        print(f"Stoichiometric AFR: {AFR_STOIC:>.6f}")
        return AFR_STOIC
    else:
        AFR = MW_AIR / MW_FUEL
        return AFR

def calc_EquivalenceRatio(AFR_STOIC:float, AFR:float) -> float:
    """
    Calculates the equivalence ratio.
    """

    EQR = AFR_STOIC / AFR
    return EQR

if __name__ == '__main__':
    calc_AirProperties()