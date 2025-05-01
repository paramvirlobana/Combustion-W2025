#===========================================================
# Program written for  Combustion MECH 6191 - Winter 2025
#                        PROJECT
# Author:
#   -- Paramvir Lobana --
#===========================================================

import numpy as np
import os
import sys
import itertools
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from time import time
import cantera as ct
import argparse

# User imports
import modules.utilities as ut
import modules.thermodynamics as thermo
import modules.reactions as rt

# Import inputs
from inputs import *

# Configurations
sns.set_theme(style="ticks")
palette = sns.color_palette("rocket_r")


# Define directories and other system variables
SCRIPT_DIR      =   os.path.dirname(os.path.realpath(__file__))
FIG_DIR         =   os.path.join('/home/cfd_guru/workdir/Combustion-W2025/report', 'figs')
DATA_DIR        =   os.path.join(SCRIPT_DIR, 'output')

MECHANISM_DIR   =   os.path.join(SCRIPT_DIR, 'data', 'SanDiego')
SanDiegoMech    =   os.path.join(MECHANISM_DIR, 'SanDiego.yaml')

def main(
    args
):

    startTime = time()
    save_flag:bool = args.data

    if args.primary:
        AFR_STOIC = primary(save_flag)

    # Define the inputs for the secondary air calculations.

    if args.secondary:
        secondary()

    if args.rql:
        RQL(eqr_rich=1.24, eqr_lean=0.42)

    endTime = time()
    print("") 
    print("STATS:")
    print("-"*6)
    print(f"Program took {(endTime - startTime):10.03f}s to execute.")

def primary(save_flag:bool):

    DENSITY_AIR, DENSITY_FUEL, MW_AIR, MW_FUEL = thermo.calc_AirProperties()
    AFR_STOIC = thermo.calc_AirFuelRatio(MW_AIR, MW_FUEL, stoic=True)

    # Design variables
    iters = 51
    V_FUEL_RANGE    =   np.linspace(60, 110, iters)
    V_AIR_RANGE     =   np.linspace(40, 90, iters)

    data_store = []

    for V_FUEL, V_AIR in itertools.product(V_FUEL_RANGE, V_AIR_RANGE):

        mf_fuel         =   DENSITY_FUEL * A_FUEL * V_FUEL
        mf_air_primary  =   DENSITY_AIR  * A_AIR  * V_AIR

        afr_rich        =   mf_air_primary / mf_fuel
        eqr_rich        =   AFR_STOIC / afr_rich

        # Calculate the momentum flux
        momentum_flux = (DENSITY_FUEL * (V_FUEL)**2) / (DENSITY_AIR * V_AIR ** 2)

        data_store.append({
            'EQR_RICH'          :       eqr_rich,
            'AFR_RICH'          :       afr_rich,
            'V_FUEL'            :       V_FUEL,
            'MASSFLOW_FUEL'     :       mf_fuel,
            'V_AIR'             :       V_AIR,
            'MASSFLOW_AIR_P'    :       mf_air_primary,
            'J'                 :       momentum_flux,
        })

    df = pd.DataFrame(data_store)
    print(df)

    df = df[(df['EQR_RICH'] >= 1.24) & (df['EQR_RICH'] < 1.25)]
    df = df[(df['J'] > 2) & (df['J'] < 3)]


    print(df)

    if save_flag:
        df_out = df.round(6)
        ut.make_dir(DATA_DIR)
        df_out.to_csv(os.path.join(DATA_DIR, 'd_points.csv'), index=False)

    if '--plot' in sys.argv:
        
        g = sns.relplot(
            data=df,
            x="EQR_RICH", y="J", col="V_FUEL", hue="V_AIR",
            kind="scatter", palette=palette, col_wrap=3,
            height=4, aspect=.75, facet_kws=dict(sharex=False),
        )

        ut.make_dir(FIG_DIR)

        plt.savefig(FIG_DIR + '/plt_comp.png', format='png')
        plt.savefig(FIG_DIR + '/plt_comp.eps', format='eps')
    
    return AFR_STOIC


def secondary(silent:bool=True) -> float:

    """
    For the secondary part, the target is to have an equivalence ratio of 0.42.
    How do we get that? Interesting.
    
    """

    DENSITY_AIR, DENSITY_FUEL, MW_AIR, MW_FUEL = thermo.calc_AirProperties()
    AFR_STOIC = thermo.calc_AirFuelRatio(MW_AIR, MW_FUEL, stoic=True)

    # Following is the desgin point selected from the primary calculations.
    EQR_GLOBAL:float = 0.42
    PRIMARY_VARS:dict = {
        'EQR_RICH': 1.245,
        'AFR_RICH': 4.854891, 
        'V_FUEL': 99.0, 
        'MASSFLOW_FUEL': 0.007339, 
        'V_AIR': 65.0, 
        'MASSFLOW_AIR_P': 0.035631, 
        'J': 2.738813
        }

    MASSFLOW_AIR_P = PRIMARY_VARS['MASSFLOW_AIR_P']
    AFR_GLOBAL = AFR_STOIC / EQR_GLOBAL
    MASSFLOW_AIR_GLOBAL = PRIMARY_VARS['MASSFLOW_FUEL'] * AFR_GLOBAL

    MASSFLOW_AIR_S = MASSFLOW_AIR_GLOBAL - MASSFLOW_AIR_P

    if silent:
        print(MASSFLOW_AIR_S)
        return MASSFLOW_AIR_S
    else:
        print("")
        print('Combustor mass flows:')
        print(f"{'Quantity':<20} {'Value':>15} {'Unit':<10}")
        print("-" * 50)
        print(f"{'Global mass flow':<20} {MASSFLOW_AIR_GLOBAL:>15.6f} {'kg/m3':<10}")
        print(f"{'Primary mass flow':<20} {PRIMARY_VARS['MASSFLOW_AIR_P']:>15.6f} {'kg/m3':<10}")
        print(f"{'Secondary mass flow':<20} {MASSFLOW_AIR_S:>15.6f} {'kg/m3':<10}")

def RQL(
    eqr_rich:float, eqr_lean:float
) -> None:
    """
    NOTE:
    This function should have 3 parts:
    1. Rich burn reaction.
    2. Mixing of the secondary air.
    3. Lean burn reaction.

    And also two misc steps:
    1. Before the program runs, need to generate directories.
    """
    print("Initializing the RQL reaction mechanism.")

    # TODO Perform the preprocessing step:
    # Create temp directories for storing data between separate RQL stages.
    # INIT gases

    PFR:dict = {
        'length': 0.5,     # [m]
        'radius': 0.018823,     # [m]
        'area'  : 1.e-3,     # [m^2]
        'volume': 0.000048,     # [m^3]
        'vel'   : 20            # [m/s] 
    }

    fuel        = ct.Solution(SanDiegoMech)
    fuel.TPX    = T_FUEL, P_FUEL, {'NH3': 1.0}

    air         = ct.Solution(SanDiegoMech)
    air.TPX     = T_AIR, P_AIR, {'O2': 1.0, 'N2': 3.76}

    rich_gas_thermo, inlet_bounbdary_species = rt.mixing(gas_a=fuel, gas_b=air, mdot_a=0.007339, mdot_b=0.035631)
    
    # Create the rich burn gas
    rich_gas = ct.Solution(SanDiegoMech)    
    rich_gas.TPY = rich_gas_thermo.thermo.T, rich_gas_thermo.thermo.P, rich_gas_thermo.thermo.Y
    rich_flame, rich_out, rich_outlet_state = rt.rich(eqr=1.24, mixture=rich_gas)
    print(rich_out.report())

    air_secondary         = ct.Solution(SanDiegoMech)
    air_secondary.TPX     = T_AIR, P_AIR, {'O2': 3.0, 'N2': 3*3.76}

    # Mix the output of rich flame with secondary air.
    lean_gas_thermo, lean_inlet_boundary_species = rt.mixing(gas_a=rich_out, gas_b=air_secondary, mdot_a=0.007339+0.035631, mdot_b=secondary())
    
    # Create the lean burn gas
    lean_gas = ct.Solution(SanDiegoMech)
    lean_gas.TPY = lean_gas_thermo.thermo.T, lean_gas_thermo.thermo.P, lean_gas_thermo.thermo.Y
    print(lean_gas.report())

if __name__ == '__main__':


    ut.printHead()

    # Main arguments
    parser = argparse.ArgumentParser(prog='RQL Reactor', description='Simulation for the reaction mechanism for an RQL combustor.')
    parser.add_argument('-p', '--primary',      action='store_true', help='Runs initial calculations for the primary region.')
    parser.add_argument('-s', '--secondary',    action='store_true', help='Runs initial calculations for the secondary air region.')
    parser.add_argument('-r', '--rql',          action='store_true', help='Runs the RQL combustor routine.')

    # Settings
    parser.add_argument('-d', '--data',    action='store_true', help='Save all output data to csv.')

    arguments = parser.parse_args()
    main(arguments)