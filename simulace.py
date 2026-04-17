import numpy as np
from LorenzSimulator import LorenzSimulator
from LorenzTrajecktory import LorenzTrajectory

def simulace(pocatecni_stav, t_max, pocet_bodu, sigma, rho, beta):
    """
    Tato funkce propojuje starý skript porovnani_spline.py 
    s vaším novým LorenzSimulatorem.
    """
    simulator = LorenzSimulator()
    
    # Vytvoříme dočasný objekt trajektorie (pozor na překlep Trajecktory s 'k')
    t = LorenzTrajectory(
        sigma=sigma, beta=beta, rho=rho, 
        dt=t_max/pocet_bodu, steps=pocet_bodu,
        x0=pocatecni_stav[0], y0=pocatecni_stav[1], z0=pocatecni_stav[2]
    )
    
    # Spustíme výpočet
    simulator.simulate(t)
    
    # Vrátíme to jako NumPy pole (N x 3), které očekává porovnani_spline.py
    return np.column_stack((t.x, t.y, t.z))