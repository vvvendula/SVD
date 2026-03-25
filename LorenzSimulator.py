class LorenzSimulator:
    def derivatives(self, x, y, z, sigma, beta, rho):
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        return dx, dy, dz

    def simulate(self, trajectory):
        dt = trajectory.dt
        steps = trajectory.steps

        x = trajectory.x0
        y = trajectory.y0
        z = trajectory.z0

        t_values = [0.0]
        x_values = [x]
        y_values = [y]
        z_values = [z]

        for i in range(1, steps):
            k1x, k1y, k1z = self.derivatives(
                x, y, z,
                trajectory.sigma, trajectory.beta, trajectory.rho
            )

            k2x, k2y, k2z = self.derivatives(
                x + 0.5 * dt * k1x,
                y + 0.5 * dt * k1y,
                z + 0.5 * dt * k1z,
                trajectory.sigma, trajectory.beta, trajectory.rho
            )

            k3x, k3y, k3z = self.derivatives(
                x + 0.5 * dt * k2x,
                y + 0.5 * dt * k2y,
                z + 0.5 * dt * k2z,
                trajectory.sigma, trajectory.beta, trajectory.rho
            )

            k4x, k4y, k4z = self.derivatives(
                x + dt * k3x,
                y + dt * k3y,
                z + dt * k3z,
                trajectory.sigma, trajectory.beta, trajectory.rho
            )

            x += (dt / 6.0) * (k1x + 2 * k2x + 2 * k3x + k4x)
            y += (dt / 6.0) * (k1y + 2 * k2y + 2 * k3y + k4y)
            z += (dt / 6.0) * (k1z + 2 * k2z + 2 * k3z + k4z)

            t_values.append(i * dt)
            x_values.append(x)
            y_values.append(y)
            z_values.append(z)

        trajectory.t = t_values
        trajectory.x = x_values
        trajectory.y = y_values
        trajectory.z = z_values

        return trajectory