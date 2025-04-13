    # Define the geometry of the plug flow reaction:
    PFR:dict = {
        'length': 0.042881,     # [m]
        'radius': 0.018823,     # [m]
        'area'  : 0.001113,     # [m^2]
        'volume': 0.000048,     # [m^3]
        'vel'   : 20            # [m/s] 
    }
    
    PFR:dict = {
        'length': 0.5,     # [m]
        'radius': 0.018823,     # [m]
        'area'  : 1.e-3,     # [m^2]
        'volume': 0.000048,     # [m^3]
        'vel'   : 20            # [m/s] 
    }
    
    # START RQL sequence
    # RICH BURN ZONE
    flame, rich_mixture, outlet_state = rt.rich(eqr_rich=1.24, air=air, fuel=fuel, mixture=rich_gas)
    print(rich_mixture.report())

    # Mixing step. Mix the riuh_mixture with secondary air
    mdot_rich, mdot_air = secondary(silent=True)
    quench_state, quench_boundary_species = rt.mixing(rich_mixture, air, mdot_rich=mdot_rich, mdot_air=mdot_air)
    print(quench_state.thermo.T, quench_state.thermo.P)

    # Quench
    # Calculate combustor in a well stirred reactor
    lean_gas.TP = quench_state.thermo.T, quench_state.thermo.P
    lean_gas.Y  = quench_boundary_species
    mdot_lean = mdot_rich + mdot_air

    print(quench_boundary_species)

    sys.exit()


    #rt.lean(lean_gas, mdot_lean, PFR)
    #flame2, lean_mixture, outlet_state2 = lean_c(lean_gas)
    lean_mixture = rt.lean(lean_gas, mdot_lean, PFR)
    print(lean_mixture.report())

def lean_c(
    mixture:ct.composite.Solution
) -> tuple:
    
    # Solve flame simulation
    initial_grid = np.linspace(0, 0.042881, 101)
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
        try:
            no_index = mixture.species_index('NO')
            print(f'NOx at outlet: {1000000*flame.Y[no_index][-1]:.2f} ppm')
        except ValueError:
            print("NO species not found in mechanism")

        outlet_state = ''
        print("\n\n")
        print(f"{'Species':<20} {'Mass Fraction':>15}")
        print("-" * 50)
        for i in range(0, mixture.n_species):
            species_name = mixture.species_name(i)
            species_mass_fraction = flame.Y[mixture.species_index(species_name)][-1]
            if i == 0:
                outlet_state += f'{species_name}:{species_mass_fraction:.9f}'
            else:
                outlet_state += f',{species_name}:{species_mass_fraction:.9f}'
            print(f"{species_name:<20} {species_mass_fraction:>15.9f}")
        print("\n\n")

        return flame, mixture, outlet_state
    
    else:
        print("Flame solution failed. Returning None.")
        return None, mixture, None
