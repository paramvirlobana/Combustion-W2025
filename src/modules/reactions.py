import sys
import numpy as np
import pandas as pd
import cantera as ct
from inputs import *

def rich(
    eqr: float, mixture:ct.composite.Solution
) -> tuple:
    """
    Function for calculating the reaction characteristics in the rich burn zone.
   
    Inputs:
    ------
    - eqr_rich: equivalence ratio for the rich zone
    - air: cantera air
    - fuel: cantera fuel
    - mixture: init mixture gas
   
    Returns:
    -------
    - flame: solved FreeFlame object
    - gas_mix: cantera Solution object with the mixed state
    - outlet_state: string of species mass fractions at the outlet
    """

    # Solve flame simulation
    initial_grid = np.linspace(0, 0.059917, 101)
    flame = ct.FreeFlame(mixture, initial_grid)
    flame.energy_enabled = True
    flame.set_refine_criteria(ratio=3, slope=0.2, curve=0.2)
    
    try:
        flame.solve(loglevel=1, refine_grid=True, auto=False)
        solution_successful = True
    except:
        flame.set_refine_criteria(ratio=3, slope=0.1, curve=0.1)
        try:
            flame.solve(loglevel=1, refine_grid=True, auto=True)
            solution_successful = True
        except:
            solution_successful = False
    
    if solution_successful:
        print(f'Phi={eqr}: Outlet temperature = {flame.T[-1]:.1f} K')
        try:
            no_index = mixture.species_index('NO')
            print(f'NOx at outlet: {1000000*flame.Y[no_index][-1]:.2f} ppm')
        except ValueError:
            print("NO species not found in mechanism")

        outlet_state = ''
        #print("\n\n")
        #print(f"{'Species':<20} {'Mass Fraction':>15}")
        #print("-" * 50)
        for i in range(0, mixture.n_species):
            species_name = mixture.species_name(i)
            species_mass_fraction = flame.Y[mixture.species_index(species_name)][-1]
            if i == 0:
                outlet_state += f'{species_name}:{species_mass_fraction:.9f}'
            else:
                outlet_state += f',{species_name}:{species_mass_fraction:.9f}'
            #print(f"{species_name:<20} {species_mass_fraction:>15.9f}")
        #print("\n\n")

        return flame, mixture, outlet_state
    
    else:
        print("Flame solution failed. Returning None.")
        return None, mixture, None

def quench(GEOM:dict):
    print("Computing MIXING zone.")

def lean(
    gas:ct.composite.Solution, mdot:float, geom:dict
) -> None:
    print("Computing LEAN zone.")

    n_steps = 2000
    dz = geom['length'] / n_steps
    r_vol = geom['area'] * dz

    # Make a new reactor for lean burn
    lean_reactor = ct.IdealGasReactor(gas)
    lean_reactor.volume = r_vol
    upstream = ct.Reservoir(gas, name='upstream')
    downstream = ct.Reservoir(gas, name='downstream')
    m = ct.MassFlowController(upstream, lean_reactor, mdot=mdot)
    v = ct.PressureController(lean_reactor, downstream, primary=m, K=1e-5)
    sim2 = ct.ReactorNet([lean_reactor])

    # define time, space, and other information vectors
    z2 = (np.arange(n_steps) + 1) * dz
    t_r2 = np.zeros_like(z2)  # residence time in each reactor
    u2 = np.zeros_like(z2)
    t2 = np.zeros_like(z2)
    states2 = ct.SolutionArray(lean_reactor.thermo)

    # iterate through the PFR cells
    for n in range(n_steps):
        # Set the state of the reservoir to match that of the previous reactor
        gas.TDY = lean_reactor.thermo.TDY
        upstream.syncState()
        # integrate the reactor forward in time until steady state is reached
        sim2.reinitialize()
        sim2.advance_to_steady_state()
        # compute velocity and transform into time
        u2[n] = mdot / geom['area'] / lean_reactor.thermo.density
        t_r2[n] = lean_reactor.mass / mdot  # residence time in this reactor
        t2[n] = sum(t_r2)
        # write output data
        states2.append(lean_reactor.thermo.state)

    print('Final Temperature is ',states2.T,'K')
    print(f"NOx is {1000000*states2.Y[-1, gas.species_index('NO')]} ppm")

    return gas


def mixing(
    gas_a:ct.composite.Solution, gas_b:ct.composite.Solution, mdot_a:float, mdot_b:float
) -> tuple:
    """
    Description:
    -----------
    This function mixes two gases.
    https://cantera.org/3.1/examples/python/reactors/mix1.html#sphx-glr-examples-python-reactors-mix1-py

    Inputs:
    ------
    gas_a: This is the combustion gas obtained from the first part of the reaction.
    gas_b: This is the quench air obtained from the HPC.
    EQR  : The equivalence ratio of the mixture.

    Returns:
    ------
    boundary species for lean burn
    
    """

    # Create reservoirs for storing mixture data.
    reservoir_a = ct.Reservoir(gas_a, name='gas a res')
    reservoir_b = ct.Reservoir(gas_b, name='gas b res')
    downstream  = ct.Reservoir(gas_b, name='outlet reservoir')

    # Create a reactor for the mixer. A reactor is required instead of a reservoir, 
    # since the state will change with time if the inlet mass flow rates change or if there 
    # is chemistry occurring. FROM CANTERA DOCUMENTATION
    mixer = ct.IdealGasReactor(gas_a, name='Mixer')

    # Create the mass flow controllers.
    mfc1 = ct.MassFlowController(reservoir_a, mixer, mdot=mdot_a, name="gas_a")
    mfc2 = ct.MassFlowController(reservoir_b, mixer, mdot=mdot_b, name="gas_b")


    outlet = ct.Valve(mixer, downstream, K=10.0, name="Valve")
    sim = ct.ReactorNet([mixer])

    sim.advance_to_steady_state()
    print(mixer.thermo.report())

    # Prepare the species from this reactor to the one with Lean burner calculation
    boundary_species:str = ''
    for i in range(100000):
        try:
            name = mixer.thermo.species_name(i)
            y_val = mixer.thermo.Y[mixer.thermo.species_index(name)]
            if i == 0:
                boundary_species += '%s:%.8f'%(name,y_val)
            else:
                boundary_species += ' ,%s:%.8f'%(name,y_val)
        except:
            break
   
    return mixer, boundary_species
