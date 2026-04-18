from scipy.interpolate import splprep, splev
import numpy as np

def vyhlad_krivku(traj, s, pocet_novych_bodu):

    #vytvoreni parametru
    tck, u = splprep(traj.T, s=s)

    #nove parametry pro interpolaci
    u_new = np.linspace(0, 1, pocet_novych_bodu)

    #interpolace pomocí b-spline
    traj_spline = splev(u_new, tck)

    return np.array(traj_spline).T