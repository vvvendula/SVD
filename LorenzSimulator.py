import numpy as np
from scipy.integrate import solve_ivp
from LorenzTrajectory import LorenzTrajectory


class LorenzSimulator:
    """Jednotný simulátor: podporuje RK4 (vlastní) i scipy solve_ivp."""

    # ── Lorenzovy rovnice ──
    @staticmethod
    def derivatives_tuple(x, y, z, sigma, beta, rho):
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        return dx, dy, dz

    @staticmethod
    def derivatives_ivp(t, stav, sigma, rho, beta):
        """Formát pro scipy solve_ivp."""
        x, y, z = stav
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        return [dx, dy, dz]

    # ── Vlastní RK4 ──
    def _simulate_rk4(self, traj: LorenzTrajectory):
        dt = traj.dt
        steps = traj.steps
        sigma, beta, rho = traj.sigma, traj.beta, traj.rho

        x, y, z = traj.x0, traj.y0, traj.z0
        t_values = [0.0]
        x_values = [x]
        y_values = [y]
        z_values = [z]

        for i in range(1, steps):
            k1x, k1y, k1z = self.derivatives_tuple(x, y, z, sigma, beta, rho)
            k2x, k2y, k2z = self.derivatives_tuple(
                x + 0.5 * dt * k1x, y + 0.5 * dt * k1y, z + 0.5 * dt * k1z,
                sigma, beta, rho
            )
            k3x, k3y, k3z = self.derivatives_tuple(
                x + 0.5 * dt * k2x, y + 0.5 * dt * k2y, z + 0.5 * dt * k2z,
                sigma, beta, rho
            )
            k4x, k4y, k4z = self.derivatives_tuple(
                x + dt * k3x, y + dt * k3y, z + dt * k3z,
                sigma, beta, rho
            )

            x += (dt / 6.0) * (k1x + 2 * k2x + 2 * k3x + k4x)
            y += (dt / 6.0) * (k1y + 2 * k2y + 2 * k3y + k4y)
            z += (dt / 6.0) * (k1z + 2 * k2z + 2 * k3z + k4z)

            t_values.append(i * dt)
            x_values.append(x)
            y_values.append(y)
            z_values.append(z)

        traj.t = t_values
        traj.x = x_values
        traj.y = y_values
        traj.z = z_values
        return traj

    # ── scipy solve_ivp ──
    def _simulate_solve_ivp(self, traj: LorenzTrajectory):
        t_max = traj.dt * traj.steps
        t_eval = np.linspace(0, t_max, traj.steps)
        pocatecni_stav = [traj.x0, traj.y0, traj.z0]

        reseni = solve_ivp(
            self.derivatives_ivp,
            [0, t_max],
            pocatecni_stav,
            args=(traj.sigma, traj.rho, traj.beta),
            t_eval=t_eval,
            method="RK45"
        )

        traj.t = reseni.t.tolist()
        traj.x = reseni.y[0].tolist()
        traj.y = reseni.y[1].tolist()
        traj.z = reseni.y[2].tolist()
        return traj

    # ── Veřejné rozhraní ──
    def simulate(self, traj: LorenzTrajectory, method: str = "rk4"):
        if method == "solve_ivp":
            return self._simulate_solve_ivp(traj)
        else:
            return self._simulate_rk4(traj)