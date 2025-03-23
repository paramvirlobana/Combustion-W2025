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

# Define directories and other system variables
SCRIPT_DIR          = os.path.dirname(os.path.realpath(__file__))
MECHANISM_DIR       = os.path.join(SCRIPT_DIR, 'data', 'Nitrogen', 'Glarborg/')
Glarborg            = os.path.join(MECHANISM_DIR, 'Glarborg.yaml')

# Geometrical Inputs
R_AIR_OUTER     =   14.29/1000      # [m]
R_AIR_INNER     =   6.87/1000       # [m]
R_FUEL          =   6.67/1000       # [m]

A_AIR           =   np.pi * (R_AIR_OUTER**2 - R_AIR_INNER**2)
A_FUEL          =   np.pi * R_FUEL**2


print(A_AIR, A_FUEL)

def main():
    startTime = time()

    DENSITY_AIR, DENSITY_FUEL, MW_AIR, MW_FUEL = thermo.calc_AirProperties()
    AFR_STOIC = thermo.calc_AirFuelRatio(MW_AIR, MW_FUEL, stoic=True)

    # Design variables
    EQR_RICH_RANGE = np.linspace(1.0, 1.3, 21)

    data_store = []

    for EQR_RICH in EQR_RICH_RANGE:

        AFR_RICH = AFR_STOIC / EQR_RICH

        data_store.append({
            'EQR_RICH':     EQR_RICH,
            'AFR_RICH':     AFR_RICH,
        })

    df = pd.DataFrame(data_store)
    print(df)






    endTime = time()
    print("")
    print("STATS:")
    print("-"*6)
    print(f"Program took {(endTime - startTime):10.03f}s to execute.")


if __name__ == '__main__':
    ut.printHead()
    main()