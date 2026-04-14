from scipy.interpolate import splprep, splev
import numpy as np

def vyhlad_krivku(traj, s, pocet_novych_bodu):

    # Vytvoření parametrů pro B-spline
    tck, u = splprep(traj.T, s=s)

    # Generování nových parametrů pro interpolaci
    u_new = np.linspace(0, 1, pocet_novych_bodu)

    # Interpolace pomocí B-spline
    traj_spline = splev(u_new, tck)

    return np.array(traj_spline).T