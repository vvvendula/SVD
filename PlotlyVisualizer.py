import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import splprep, splev


class PlotlyVisualizer:
    def _create_bspline_curve(self, x, y, z, smoothing=0.0, points_per_interval=5):
        """
        Vytvoří hustší body pomocí B-spline interpolace.

        Parametry:
        - x, y, z: původní body trajektorie
        - smoothing: parametr vyhlazení spline
        - points_per_interval: počet bodů na jeden interval mezi dvěma původními body

        Návrat:
        - spline_x, spline_y, spline_z, u_fine
        """
        if len(x) < 4:
            arr_x = np.array(x, dtype=float)
            arr_y = np.array(y, dtype=float)
            arr_z = np.array(z, dtype=float)
            if len(x) > 1:
                u_fine = np.linspace(0.0, 1.0, len(x))
            else:
                u_fine = np.array([0.0])
            return arr_x, arr_y, arr_z, u_fine

        try:
            points = np.array([x, y, z], dtype=float)
            tck, u = splprep(points, s=smoothing, k=min(3, len(x) - 1))

            total_intervals = len(x) - 1
            total_points = total_intervals * max(1, points_per_interval) + 1

            u_fine = np.linspace(0.0, 1.0, total_points)
            spline_x, spline_y, spline_z = splev(u_fine, tck)

            return (
                np.array(spline_x),
                np.array(spline_y),
                np.array(spline_z),
                u_fine
            )
        except Exception:
            arr_x = np.array(x, dtype=float)
            arr_y = np.array(y, dtype=float)
            arr_z = np.array(z, dtype=float)
            if len(x) > 1:
                u_fine = np.linspace(0.0, 1.0, len(x))
            else:
                u_fine = np.array([0.0])
            return arr_x, arr_y, arr_z, u_fine

    def create_animated_figure(self, simulation):
        trajectories = simulation.trajectories
        if not trajectories:
            raise ValueError("No trajectories to visualize.")

        frame_stride = max(1, simulation.frame_stride)
        use_bspline = getattr(simulation, "use_bspline", False)
        points_per_interval = max(1, getattr(simulation, "points_per_interval", 5))

        prepared_trajectories = []

        for traj in trajectories:
            original_len = len(traj.x)
            if original_len == 0:
                continue

            if use_bspline:
                spline_x, spline_y, spline_z, u_fine = self._create_bspline_curve(
                    traj.x,
                    traj.y,
                    traj.z,
                    smoothing=0.0,
                    points_per_interval=points_per_interval
                )
            else:
                spline_x = np.array(traj.x, dtype=float)
                spline_y = np.array(traj.y, dtype=float)
                spline_z = np.array(traj.z, dtype=float)
                if original_len > 1:
                    u_fine = np.linspace(0.0, 1.0, original_len)
                else:
                    u_fine = np.array([0.0])

            prepared_trajectories.append({
                "label": traj.label,
                "color": traj.color,
                "x": spline_x,
                "y": spline_y,
                "z": spline_z,
                "u_fine": u_fine,
                "original_len": original_len
            })

        if not prepared_trajectories:
            raise ValueError("No valid trajectory data to visualize.")

        max_original_len = max(traj["original_len"] for traj in prepared_trajectories)

        frame_indices = list(range(1, max_original_len, frame_stride))
        if not frame_indices:
            frame_indices = [max_original_len - 1]
        elif frame_indices[-1] != max_original_len - 1:
            frame_indices.append(max_original_len - 1)

        def sim_index_to_u(index, original_len):
            if original_len <= 1:
                return 0.0
            return index / (original_len - 1)

        def end_idx_for_sim_step(traj_data, sim_step):
            u_target = sim_index_to_u(sim_step, traj_data["original_len"])
            u_fine = traj_data["u_fine"]
            idx = np.searchsorted(u_fine, u_target, side="right") - 1
            return max(0, min(idx, len(traj_data["x"]) - 1))

        initial_traces = []
        initial_step = frame_indices[0]

        for traj in prepared_trajectories:
            if initial_step >= traj["original_len"]:
                sim_step = traj["original_len"] - 1
            else:
                sim_step = initial_step

            end_idx = end_idx_for_sim_step(traj, sim_step)

            initial_traces.append(
                go.Scatter3d(
                    x=traj["x"][:end_idx + 1],
                    y=traj["y"][:end_idx + 1],
                    z=traj["z"][:end_idx + 1],
                    mode="lines",
                    line=dict(color=traj["color"], width=4),
                    name=traj["label"]
                )
            )

        frames = []
        for sim_step in frame_indices:
            frame_data = []
            for traj in prepared_trajectories:
                effective_step = min(sim_step, traj["original_len"] - 1)
                end_idx = end_idx_for_sim_step(traj, effective_step)

                frame_data.append(
                    go.Scatter3d(
                        x=traj["x"][:end_idx + 1],
                        y=traj["y"][:end_idx + 1],
                        z=traj["z"][:end_idx + 1],
                        mode="lines",
                        line=dict(color=traj["color"], width=4),
                        name=traj["label"]
                    )
                )

            frames.append(go.Frame(data=frame_data, name=str(sim_step)))

        play_args = {
            "frame": {"duration": 50, "redraw": True},
            "fromcurrent": True,
            "transition": {"duration": 0},
            "mode": "immediate"
        }

        sliders = [
            {
                "steps": [
                    {
                        "args": [
                            [str(sim_step)],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 0}
                            }
                        ],
                        "label": str(sim_step),
                        "method": "animate"
                    }
                    for sim_step in frame_indices
                ],
                "transition": {"duration": 0},
                "x": 0.1,
                "len": 0.8,
                "currentvalue": {"prefix": "Simulační krok: "}
            }
        ]

        updatemenus = [
            {
                "type": "buttons",
                "showactive": False,
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [None, play_args]
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0}
                            }
                        ]
                    }
                ],
                "x": 0.1,
                "y": 0
            }
        ]

        fig = go.Figure(data=initial_traces, frames=frames)

        fig.update_layout(
            title=simulation.title,
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z"
            ),
            updatemenus=updatemenus,
            sliders=sliders,
            margin=dict(l=0, r=0, b=0, t=40)
        )

        return fig

    def show(self, simulation):
        fig = self.create_animated_figure(simulation)
        fig.show()

    def save_html(self, simulation, path: str):
        fig = self.create_animated_figure(simulation)
        fig.write_html(path)