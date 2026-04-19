import numpy as np
import plotly.graph_objects as go


class PlotlyVisualizer:

    def _create_bspline_curve(self, x, y, z, smoothing=0.0,
                               points_per_interval=5,
                               bspline_method="scipy"):
        if bspline_method == "cox_de_boor":
            return BSpline.cox_de_boor_smooth_xyz(
                x, y, z, k=3, points_per_interval=points_per_interval
            )
        else:
            return BSpline.scipy_smooth_xyz(
                x, y, z, smoothing=smoothing,
                points_per_interval=points_per_interval
            )

    def create_animated_figure(self, simulation):
        trajectories = simulation.trajectories
        if not trajectories:
            raise ValueError("No trajectories to visualize.")

        frame_stride = max(1, simulation.frame_stride)
        use_bspline = getattr(simulation, "use_bspline", False)
        points_per_interval = max(1, getattr(simulation, "points_per_interval", 5))
        bspline_method = getattr(simulation, "bspline_method", "scipy")

        prepared_trajectories = []

        for traj in trajectories:
            original_len = len(traj.x)
            if original_len == 0:
                continue

            if use_bspline:
                spline_x, spline_y, spline_z, u_fine = self._create_bspline_curve(
                    traj.x, traj.y, traj.z,
                    smoothing=0.0,
                    points_per_interval=points_per_interval,
                    bspline_method=bspline_method
                )
            else:
                spline_x = np.array(traj.x, dtype=float)
                spline_y = np.array(traj.y, dtype=float)
                spline_z = np.array(traj.z, dtype=float)
                u_fine = np.linspace(0, 1, max(original_len, 1))

            prepared_trajectories.append({
                "label": traj.label, "color": traj.color,
                "x": spline_x, "y": spline_y, "z": spline_z,
                "u_fine": u_fine, "original_len": original_len
            })

        if not prepared_trajectories:
            raise ValueError("No valid trajectory data to visualize.")

        max_original_len = max(t["original_len"] for t in prepared_trajectories)

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
            idx = np.searchsorted(traj_data["u_fine"], u_target, side="right") - 1
            return max(0, min(idx, len(traj_data["x"]) - 1))

        # Počáteční stopy
        initial_step = frame_indices[0]
        initial_traces = []
        for td in prepared_trajectories:
            sim_step = min(initial_step, td["original_len"] - 1)
            end_idx = end_idx_for_sim_step(td, sim_step)
            initial_traces.append(go.Scatter3d(
                x=td["x"][:end_idx + 1], y=td["y"][:end_idx + 1],
                z=td["z"][:end_idx + 1],
                mode="lines", line=dict(color=td["color"], width=4),
                name=td["label"]
            ))

        # Snímky
        frames = []
        for sim_step in frame_indices:
            frame_data = []
            for td in prepared_trajectories:
                eff = min(sim_step, td["original_len"] - 1)
                end_idx = end_idx_for_sim_step(td, eff)
                frame_data.append(go.Scatter3d(
                    x=td["x"][:end_idx + 1], y=td["y"][:end_idx + 1],
                    z=td["z"][:end_idx + 1],
                    mode="lines", line=dict(color=td["color"], width=4),
                    name=td["label"]
                ))
            frames.append(go.Frame(data=frame_data, name=str(sim_step)))

        play_args = {
            "frame": {"duration": 50, "redraw": True},
            "fromcurrent": True,
            "transition": {"duration": 0},
            "mode": "immediate"
        }

        sliders = [{
            "steps": [
                {"args": [[str(s)], {"frame": {"duration": 0, "redraw": True},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                 "label": str(s), "method": "animate"}
                for s in frame_indices
            ],
            "transition": {"duration": 0},
            "x": 0.1, "len": 0.8,
            "currentvalue": {"prefix": "Simulační krok: "}
        }]

        updatemenus = [{
            "type": "buttons", "showactive": False,
            "buttons": [
                {"label": "Play", "method": "animate", "args": [None, play_args]},
                {"label": "Pause", "method": "animate",
                 "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}]}
            ],
            "x": 0.1, "y": 0
        }]

        fig = go.Figure(data=initial_traces, frames=frames)
        fig.update_layout(
            title=simulation.title,
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
            updatemenus=updatemenus, sliders=sliders,
            margin=dict(l=0, r=0, b=0, t=40)
        )
        return fig

    def show(self, simulation):
        self.create_animated_figure(simulation).show()

    def save_html(self, simulation, path: str):
        self.create_animated_figure(simulation).write_html(path)