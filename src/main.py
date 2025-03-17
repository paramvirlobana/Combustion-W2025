#===========================================================
# Program written for  Combustion MECH 6191 - Winter 2025
#                        PROJECT
# Author:
#   -- Paramvir Lobana --
#===========================================================

import os
import numpy as np
import pandas as pd
import cantera as ct

# User imports
import modules.utilities as ut

# Define directories and other system variables
SCRIPT_DIR          = os.path.dirname(os.path.realpath(__file__))
MECHANISM_DIR       = os.path.join(SCRIPT_DIR, 'data/Nitrogen/Glarborg/')
Glarborg           = os.path.join(MECHANISM_DIR, 'Glarborg.yaml')

def main():


    # This is just an example for mixing
    gas_a = ct.Solution('air.yaml')
    gas_a.TPX = 300.0, ct.one_atm, 'O2:0.21, N2:0.78, AR:0.01'
    rho_a = gas_a.density

    gas_b = ct.Solution(Glarborg)
    gas_b.TPX = 300.0, ct.one_atm, 'NH3:1'
    rho_b = gas_b.density

    res_a = ct.Reservoir(gas_a, name='Air Reservoir')
    res_b = ct.Reservoir(gas_b, name='Fuel Reservoir')
    downstream = ct.Reservoir(gas_a, name='Outlet Reservoir')

    gas_b.TPX = 300.0, ct.one_atm, 'O2:0.21, N2:0.78, AR:0.01'
    mixer = ct.IdealGasReactor(gas_b, name='Mixer')

    mfc1 = ct.MassFlowController(res_a, mixer, mdot=rho_a*2.5/0.21, name="Air Inlet")
    mfc2 = ct.MassFlowController(res_b, mixer, mdot=rho_b*1.0, name="Fuel Inlet")

    outlet = ct.Valve(mixer, downstream, K=10.0, name="Valve")

    sim = ct.ReactorNet([mixer])

    sim.advance_to_steady_state()

    # view the state of the gas in the mixer
    print(mixer.thermo.report())
    


if __name__ == '__main__':
    ut.printHead()
    main()