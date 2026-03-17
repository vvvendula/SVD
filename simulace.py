from lorenz import lorenz
from scipy.integrate import solve_ivp
import numpy as np


def simulace(pocatecni_stav, t_max, pocet_bodu, sigma, rho, beta):
   t_eval=np.linspace(0, t_max, pocet_bodu)

   reseni=solve_ivp(
      lorenz, [0, t_max], pocatecni_stav, args=(sigma, rho, beta), t_eval=t_eval
   )
   trajektorie=reseni.y.T #T je transpozice

   return trajektorie    