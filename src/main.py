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

# User imports
import modules.utilities as ut
import modules.thermodynamics as thermo

# Configurations
sns.set_theme(style="ticks")
palette = sns.color_palette("rocket_r")


# Define directories and other system variables
SCRIPT_DIR      =   os.path.dirname(os.path.realpath(__file__))
MECHANISM_DIR   =   os.path.join(SCRIPT_DIR, 'data', 'Nitrogen', 'Glarborg/')
Glarborg        =   os.path.join(MECHANISM_DIR, 'Glarborg.yaml')

# Geometrical Inputs
R_AIR_OUTER     =   13.972/1000      # [m]
R_AIR_INNER     =   3.934/1000       # [m]
R_FUEL          =   1.1/1000         # [m]

A_AIR           =   np.pi * (R_AIR_OUTER**2 - R_AIR_INNER**2)
A_FUEL          =   np.pi * R_FUEL**2
N_FUEL_HOLES    =   6

def main():
    startTime = time()

    DENSITY_AIR, DENSITY_FUEL, MW_AIR, MW_FUEL = thermo.calc_AirProperties()
    AFR_STOIC = thermo.calc_AirFuelRatio(MW_AIR, MW_FUEL, stoic=True)

    # Design variables
    iters = 21
    EQR_RICH_RANGE  = np.linspace(1.0, 1.3, 21)
    V_FUEL_RANGE    = np.linspace(50, 100, iters)
    V_AIR_RANGE     = np.linspace(30, 80, iters)

    data_store = []

    for EQR_RICH, V_FUEL, V_AIR in itertools.product(EQR_RICH_RANGE, V_FUEL_RANGE, V_AIR_RANGE):

        afr_rich = AFR_STOIC / EQR_RICH

        mf_fuel  = DENSITY_FUEL * A_FUEL * V_FUEL
        mf_air_primary   = DENSITY_AIR * A_AIR * V_AIR * N_FUEL_HOLES

        # Calculate the momentum flux
        momentum_flux = (DENSITY_FUEL * V_FUEL**2) / (DENSITY_AIR * V_AIR ** 2)

        data_store.append({
            'EQR_RICH'          :       EQR_RICH,
            'AFR_RICH'          :       afr_rich,
            'V_FUEL'            :       V_FUEL,
            'MASSFLOW_FUEL'     :       mf_fuel,
            'V_AIR'             :       V_AIR,
            'MASSFLOW_AIR_P'    :       mf_air_primary,
            'J'                 :       momentum_flux,
        })

    df = pd.DataFrame(data_store)
    print(df)

    df = df[(df['J'] > 2.54) & (df['J'] < 2.57)]
    df = df[(df['EQR_RICH'] == 1.24)]

    print(df)

    if '--save' in sys.argv:
        df.round(6)
        DATA_DIR = os.path.join(SCRIPT_DIR, 'output')
        ut.make_dir(DATA_DIR)
        df.to_csv(os.path.join(DATA_DIR, 'd_points.csv'), index=False)

    if '--plot' in sys.argv:
        
        g = sns.relplot(
            data=df,
            x="EQR_RICH", y="J", col="V_FUEL", hue="V_AIR",
            kind="scatter", palette=palette, col_wrap=3,
            height=4, aspect=.75, facet_kws=dict(sharex=False),
        )

        FIG_DIR = os.path.join(SCRIPT_DIR, 'figs')
        ut.make_dir(FIG_DIR)

        plt.savefig(FIG_DIR + '/plt_comp.png', format='png')
        plt.savefig(FIG_DIR + '/plt_comp.eps', format='eps')

    if '--scatter' in sys.argv:
        f, ax = plt.subplots(figsize=(6.5, 6.5))
        sns.scatterplot(x="EQR_RICH", y="J",
            hue="V_FUEL",
            palette="ch:r=-.2,d=.3_r",
            sizes=(1, 8), linewidth=0,
            data=df, ax=ax)
        
        FIG_DIR = os.path.join(SCRIPT_DIR, 'figs')
        ut.make_dir(FIG_DIR)

        plt.savefig(FIG_DIR + '/plt_comp.png', format='png')
        plt.savefig(FIG_DIR + '/plt_comp.eps', format='eps')



    endTime = time()
    print("")
    print("STATS:")
    print("-"*6)
    print(f"Program took {(endTime - startTime):10.03f}s to execute.")


if __name__ == '__main__':
    ut.printHead()
    main()