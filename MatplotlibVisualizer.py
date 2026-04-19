import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from LorenzSimulator import LorenzSimulator
from LorenzTrajectory import LorenzTrajectory
from BSpline import BSpline


class MatplotlibVisualizer:
    """Matplotlib vizualizace: statický graf, porovnání se spline, animace."""

    def __init__(self):
        self.simulator = LorenzSimulator()

    def _traj_to_array(self, traj: LorenzTrajectory):
        return np.column_stack((traj.x, traj.y, traj.z))

    # ── Statický graf jedné trajektorie ──
    def plot_trajectory(self, traj: LorenzTrajectory):
        data = self._traj_to_array(traj)

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.plot(data[:, 0], data[:, 1], data[:, 2], color=traj.color)
        t_max = traj.dt * traj.steps
        ax.legend([f"t={t_max:.2f}"])
        ax.set_title(f"Trajektorie: {traj.label}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.show()

    # ── Porovnání: numerická trajektorie vs B-spline ──
    def plot_comparison(self, traj: LorenzTrajectory,
                        bspline_method="scipy", s=1.0,
                        pocet_novych_bodu=5000, k=3):
        data = self._traj_to_array(traj)

        if bspline_method == "cox_de_boor":
            data_spline = BSpline.cox_de_boor_smooth(data, k=k,
                                                      pocet_novych_bodu=pocet_novych_bodu)
        else:
            data_spline = BSpline.scipy_smooth(data, s=s,
                                                pocet_novych_bodu=pocet_novych_bodu)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(projection='3d')

        ax.plot(data[:, 0], data[:, 1], data[:, 2],
                color='red', linestyle='--', marker='o', markersize=2,
                label="Numerická trajektorie", linewidth=1, alpha=0.5)

        ax.plot(data_spline[:, 0], data_spline[:, 1], data_spline[:, 2],
                color='blue', linewidth=2,
                label=f"B-spline ({bspline_method})")

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(f"Porovnání: numerická data vs. B-spline ({bspline_method})")
        ax.legend()
        plt.show()

    # ── Animace ──
    def animate(self, traj: LorenzTrajectory,
                solver_method="rk4",
                retain_points=500, frame_count=500, fps=15,
                save_path="video.mp4"):

        t_max = traj.dt * traj.steps
        pocet_bodu = traj.steps
        pocatecni_stav = [traj.x0, traj.y0, traj.z0]

        traj0 = np.empty((0, 3))

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        def update(frame):
            nonlocal traj0, pocatecni_stav

            # Vytvoříme dočasnou trajektorii pro tento kousek
            segment = LorenzTrajectory(
                sigma=traj.sigma, beta=traj.beta, rho=traj.rho,
                dt=t_max / frame_count / max(int(pocet_bodu / frame_count), 1),
                steps=max(int(pocet_bodu / frame_count), 2),
                x0=pocatecni_stav[0],
                y0=pocatecni_stav[1],
                z0=pocatecni_stav[2],
            )
            self.simulator.simulate(segment, method=solver_method)

            segment_data = self._traj_to_array(segment)
            if len(traj0) > 0:
                traj0 = np.append(traj0[:-1], segment_data, axis=0)
            else:
                traj0 = segment_data

            ax.cla()
            display = traj0[-retain_points:]
            ax.plot(display[:, 0], display[:, 1], display[:, 2],
                    color=traj.color)

            current_t = t_max / frame_count * (frame + 1)
            ax.legend([f"t={current_t:.2f}"])
            ax.set_title(traj.label)
            ax.set(xlim=(-20, 20), ylim=(-30, 30), zlim=(0, 50))

            pocatecni_stav = [segment.x[-1], segment.y[-1], segment.z[-1]]

        ani = animation.FuncAnimation(
            fig=fig, func=update, frames=frame_count,
            interval=1000 / fps, repeat=False
        )

        if save_path:
            ani.save(filename=save_path, writer="ffmpeg", fps=fps)
            print(f"Animace uložena: {save_path}")
        else:
            plt.show()

    # ── Více trajektorií najednou ──
    def plot_multiple(self, trajectories: list):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(projection='3d')

        for traj in trajectories:
            data = self._traj_to_array(traj)
            ax.plot(data[:, 0], data[:, 1], data[:, 2],
                    color=traj.color, label=traj.label, linewidth=1)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.legend()
        ax.set_title("Lorenz – více trajektorií")
        plt.show()