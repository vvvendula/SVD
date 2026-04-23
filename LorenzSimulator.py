import numpy as np
from scipy.integrate import solve_ivp
from LorenzTrajectory import LorenzTrajectory


class LorenzSimulator:

    DIVERGENCE_THRESHOLD = 1e6  # ← maximální povolená hodnota

    @staticmethod
    def derivatives_tuple(x, y, z, sigma, beta, rho):
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        return dx, dy, dz

    @staticmethod
    def derivatives_ivp(t, stav, sigma, rho, beta):
        x, y, z = stav
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        return [dx, dy, dz]

    def _simulate_rk4(self, traj: LorenzTrajectory):
        dt = traj.dt
        steps = traj.steps
        sigma, beta, rho = traj.sigma, traj.beta, traj.rho
        x, y, z = traj.x0, traj.y0, traj.z0
        threshold = self.DIVERGENCE_THRESHOLD

        t_val, x_val, y_val, z_val = [0.0], [x], [y], [z]

        for i in range(1, steps):
            k1x, k1y, k1z = self.derivatives_tuple(x, y, z, sigma, beta, rho)
            k2x, k2y, k2z = self.derivatives_tuple(
                x + 0.5*dt*k1x, y + 0.5*dt*k1y, z + 0.5*dt*k1z, sigma, beta, rho)
            k3x, k3y, k3z = self.derivatives_tuple(
                x + 0.5*dt*k2x, y + 0.5*dt*k2y, z + 0.5*dt*k2z, sigma, beta, rho)
            k4x, k4y, k4z = self.derivatives_tuple(
                x + dt*k3x, y + dt*k3y, z + dt*k3z, sigma, beta, rho)

            x += (dt/6.0) * (k1x + 2*k2x + 2*k3x + k4x)
            y += (dt/6.0) * (k1y + 2*k2y + 2*k3y + k4y)
            z += (dt/6.0) * (k1z + 2*k2z + 2*k3z + k4z)

            # ═══ DETEKCE DIVERGENCE ═══
            if abs(x) > threshold or abs(y) > threshold or abs(z) > threshold:
                print(f"[WARNING] Divergence na kroku {i} (t={i*dt:.4f}), "
                      f"dt={dt} je příliš velké! Simulace ořezána.")
                break

            t_val.append(i * dt)
            x_val.append(x)
            y_val.append(y)
            z_val.append(z)

        traj.t, traj.x, traj.y, traj.z = t_val, x_val, y_val, z_val
        return traj

    def _simulate_solve_ivp(self, traj: LorenzTrajectory):
        t_max = traj.dt * traj.steps
        t_eval = np.linspace(0, t_max, traj.steps)
        threshold = self.DIVERGENCE_THRESHOLD

        def event_divergence(t, stav, sigma, rho, beta):
            return threshold - max(abs(stav[0]), abs(stav[1]), abs(stav[2]))
        event_divergence.terminal = True
        event_divergence.direction = -1

        reseni = solve_ivp(
            self.derivatives_ivp, [0, t_max],
            [traj.x0, traj.y0, traj.z0],
            args=(traj.sigma, traj.rho, traj.beta),
            t_eval=t_eval, method="RK45",
            events=event_divergence,
        )

        traj.t = reseni.t.tolist()
        traj.x = reseni.y[0].tolist()
        traj.y = reseni.y[1].tolist()
        traj.z = reseni.y[2].tolist()

        if reseni.t_events[0].size > 0:
            print(f"[WARNING] solve_ivp divergence na t={reseni.t_events[0][0]:.4f}! Ořezáno.")

        return traj

    def simulate(self, traj: LorenzTrajectory, method: str = "rk4"):
        if method == "solve_ivp":
            return self._simulate_solve_ivp(traj)
        return self._simulate_rk4(traj)