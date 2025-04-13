import cantera as ct
import csv
from numpy import *
import pandas as pd
from matplotlib import pyplot as plt
# from Blend_Mass_Fractions import BlendingMassFractions

reaction_path = 'gri30.yaml'

def mixing(gas_a,gas_b,phi):
    res_a = ct.Reservoir(gas_a)
    res_b = ct.Reservoir(gas_b)
    downstream = ct.Reservoir(gas_b)

    mixer = ct.IdealGasReactor(gas_b)
    M_air = gas_a.density
    M_fuel = gas_b.density
    print('Air density is',M_air)
    print('Fuel density is',M_fuel)
    
    ct.MassFlowController(res_a, mixer, mdot=69/phi)
    ct.MassFlowController(res_b, mixer, mdot=28)

    outlet = ct.Valve(mixer, downstream, K=10.0)
    sim = ct.ReactorNet([mixer])
    sim.advance_to_steady_state()

    # view the state of the gas in the mixer
    return mixer

# Solve the first flame
def RQL(phi_first, phi_last):
    Tin = 800
    P = 30*ct.one_atm
    grid_initial = linspace(0,0.03,20)	# Flame length
    gas_init = ct.Solution(reaction_path)
    #bl_ratio = blending_ratio
    phi = phi_first
    reactants = {'NH3':1, 'O2':1/phi, 'N2':3.76/phi}
    gas_init.TPX = Tin, P, reactants
    f1 = ct.FreeFlame(gas_init, grid_initial)
    f1.energy_enabled = True
    tol_ss = [1.0e-5, 1.0e-9] # [rtol atol] for steady-state problem
    tol_ts = [1.0e-5, 1.0e-9] # [rtol atol] for time stepping
    f1.flame.set_steady_tolerances(default=tol_ss)
    f1.flame.set_transient_tolerances(default=tol_ts)
    f1.set_max_jac_age(50, 50)
    f1.set_refine_criteria(ratio=5, slope=0.5,curve=0.5)
    f1.solve(loglevel=1, refine_grid=True, auto=False) 
    print('T one is',f1.T[-1],'NOx is',1000000*f1.Y[gas_init.species_index('NO')][-1],'ppm')
    gas_c1_boundary = ''
    for i in range(0,gas_init.n_species):
        if i == 0:
            gas_c1_boundary += '%s:%.9f'%(gas_init.species_name(i),f1.Y[gas_init.species_index(gas_init.species_name(i))][-1])
        else:
            gas_c1_boundary += ',%s:%.9f'%(gas_init.species_name(i),f1.Y[gas_init.species_index(gas_init.species_name(i))][-1])
    ##################################################################################################
    # Mix the gases
    gas_a = ct.Solution(reaction_path) # Gas 'a' is the air, right after the HPC
    gas_a.TPY = 800.0, 30*ct.one_atm, 'O2:0.21, N2:0.79'
    # Use conditions from Combustor 1 to initialize the gas to be mixed with HPC air
    gas_b = ct.Solution(reaction_path)
    gas_b.TP = f1.T[-1], 30*ct.one_atm
    gas_b.Y = gas_c1_boundary # Get the gas composition space from excel data of the first
    gas = mixing(gas_a,gas_b,phi_last)
    print('Mixed gas temperature is',gas.thermo.T)

    # Prepare the species from this reactor to the one with Lean burner calculation
    boundary_species_lb = ''
    for i in range(100000):
        try:
            name = gas.thermo.species_name(i)
            y_val = gas.thermo.Y[gas.thermo.species_index(name)]
            if i == 0:
                boundary_species_lb += '%s:%.5f'%(name,y_val)
            else:
                boundary_species_lb += ' ,%s:%.5f'%(name,y_val)
        except:
            break
    
    # Calculate combustor 2 in Well stirred reactor
    gas2 = ct.Solution(reaction_path)
    gas2.TP = gas.thermo.T, gas.thermo.P
    gas2.Y = boundary_species_lb
    length = 0.5  # *approximate* PFR length [m]
    u_0 = 20  # inflow velocity [m/s] # air 
    area = 1.e-3  # cross-sectional area [m**2]
    n_steps = 2000
    mass_flow_rate2 = u_0 * gas2.density * area
    dz = length / n_steps
    r_vol = area * dz
    #############################################################################################################################################################
    # create a new reactor
    r2 = ct.IdealGasReactor(gas2)
    r2.volume = r_vol
    upstream = ct.Reservoir(gas2, name='upstream')
    downstream = ct.Reservoir(gas2, name='downstream')
    m = ct.MassFlowController(upstream, r2, mdot=mass_flow_rate2)
    v = ct.PressureController(r2, downstream, primary=m, K=1e-5)
    sim2 = ct.ReactorNet([r2])
    # define time, space, and other information vectors
    z2 = (arange(n_steps) + 1) * dz
    t_r2 = zeros_like(z2)  # residence time in each reactor
    u2 = zeros_like(z2)
    t2 = zeros_like(z2)
    states2 = ct.SolutionArray(r2.thermo)
    # iterate through the PFR cells
    for n in range(n_steps):
        # Set the state of the reservoir to match that of the previous reactor
        gas2.TDY = r2.thermo.TDY
        upstream.syncState()
        # integrate the reactor forward in time until steady state is reached
        sim2.reinitialize()
        sim2.advance_to_steady_state()
        # compute velocity and transform into time
        u2[n] = mass_flow_rate2 / area / r2.thermo.density
        t_r2[n] = r2.mass / mass_flow_rate2  # residence time in this reactor
        t2[n] = sum(t_r2)
        # write output data
        states2.append(r2.thermo.state)
    print('Final Temperature is ',states2.T,'K')
    print('NOx is',1000000*states2.Y[-1, gas2.species_index('NO')])
    
RQL(1.5,0.4)
    
'''
phi_last = [0.2,0.3,0.4,0.5,0.6,0.7]
phi_first = [1.2,1.3,1.4,1.5,1.6,1.7,1.8]
for bl in [0,1,2,3]:
    Temp = []
    NOXs = []
    COs = []
    phi_v = []
    for phif in phi_first:
        T,NOx,CO = RQL(phif,0.4,bl)
        phi_v.append(phif)
        Temp.append(T)
        NOXs.append(NOx)
        COs.append(CO)
    data = {'phi_f':phi_v,'Temp':Temp,'NOx':NOXs,'COs':COs}
    df = pd.DataFrame(data)
    df.to_csv('RQL_%d_phif.csv'%(bl))

phi_last = [0.2,0.3,0.4,0.5,0.6,0.7,0.8]
for bl in [0,1,2,3]:
    Temp = []
    NOXs = []
    COs = []
    phi_v = []
    for phil in phi_last:
        T,NOx,CO = RQL(1.5,phil,bl)
        phi_v.append(phil)
        Temp.append(T)
        NOXs.append(NOx)
        COs.append(CO)
    data = {'phi_l':phi_v,'Temp':Temp,'NOx':NOXs,'COs':COs}
    df = pd.DataFrame(data)
    df.to_csv('RQL_%d_phil.csv'%(bl))
'''

