import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

# Mechanism
gas = ct.Solution('gri30.yaml')

# Fuel and air properties
T_FUEL = 500.0     # K
P_FUEL = 1.5e6     # Pa

T_AIR = 800.0      # K
P_AIR = 1.2e6      # Pa

P_MIX = 1.0e6      # [Pa] Desired combustion pressure (can be avg or another value)
phi_range = np.linspace(0.5, 1.5, 21)
T_ad_list = []

for phi in phi_range:
    # 1. Set fuel stream
    fuel = ct.Solution('gri30.yaml')
    fuel.set_equivalence_ratio(phi=1.0, fuel='NH3', oxidizer='O2:1.0')  # Just NH3
    fuel.TP = T_FUEL, P_FUEL
    fuel_mole_frac = {'NH3': 1.0}

    # 2. Set air stream
    air = ct.Solution('gri30.yaml')
    air.TP = T_AIR, P_AIR
    air_mole_frac = {'O2': 1.0, 'N2': 3.76}

    # 3. Determine stoichiometric O2 per mol NH3
    # 4 NH3 + 3 O2 ⇒ O2/NH3 = 0.75 ⇒ at phi = 1.0
    O2_per_NH3 = 0.75
    air_O2_moles = (O2_per_NH3 / phi)
    air_mole_frac_scaled = {k: v * air_O2_moles for k, v in air_mole_frac.items()}

    # Combine streams
    total_moles = 1.0 + air_O2_moles * (1.0 + 3.76)
    X_mix = {}

    for sp in gas.species_names:
        x_fuel = fuel_mole_frac.get(sp, 0.0)
        x_air = air_mole_frac_scaled.get(sp, 0.0)
        X_mix[sp] = (x_fuel + x_air) / total_moles

    # Set mixed stream (isenthalpic)
    mix = ct.Solution('gri30.yaml')
    h_fuel = fuel.enthalpy_mole
    h_air = air.enthalpy_mole

    h_mix = (1.0 * h_fuel + air_O2_moles * (1 + 3.76) * h_air) / total_moles

    mix.TP = 300, P_MIX  # Initial guess
    mix.X = X_mix
    mix.HP = h_mix, P_MIX  # Set enthalpy and pressure
    mix.equilibrate('HP')

    T_ad_list.append(mix.T)

# Plot
plt.plot(phi_range, T_ad_list)
plt.xlabel("Equivalence Ratio (ϕ)")
plt.ylabel("Adiabatic Flame Temperature [K]")
plt.title("NH₃-Air Combustion with Different Inlet Conditions")
plt.grid(True)
plt.show()
