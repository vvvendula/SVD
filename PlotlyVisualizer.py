import numpy as np
import plotly.graph_objects as go
from BSpline import BSpline


class PlotlyVisualizer:

    def _get_bspline_data(self, x, y, z, smoothing, points_per_interval, method):
        if method == "cox_de_boor":
            return BSpline.cox_de_boor_smooth_xyz(x, y, z, k=3,
                                                   points_per_interval=points_per_interval)
        return BSpline.scipy_smooth_xyz(x, y, z, smoothing=smoothing,
                                         points_per_interval=points_per_interval)

    # ══════════════════════════════════════════════
    # Animovaný graf (hlavní vizualizace)
    # ══════════════════════════════════════════════
    def create_animated_figure(self, simulation):
        trajectories = simulation.trajectories
        if not trajectories:
            raise ValueError("Žádné trajektorie k vizualizaci.")

        frame_stride = max(1, simulation.frame_stride)
        use_bspline = simulation.use_bspline
        ppi = max(1, simulation.points_per_interval)
        bs_method = simulation.bspline_method

        prepared = []
        for traj in trajectories:
            orig_len = len(traj.x)
            if orig_len == 0:
                continue

            if use_bspline:
                sx, sy, sz, uf = self._get_bspline_data(
                    traj.x, traj.y, traj.z, 0.0, ppi, bs_method)
            else:
                sx = np.array(traj.x, dtype=float)
                sy = np.array(traj.y, dtype=float)
                sz = np.array(traj.z, dtype=float)
                uf = np.linspace(0, 1, max(orig_len, 1))

            prepared.append({
                "label": traj.label, "color": traj.color,
                "x": sx, "y": sy, "z": sz,
                "u_fine": uf, "original_len": orig_len
            })

        if not prepared:
            raise ValueError("Žádná platná data.")

        max_len = max(p["original_len"] for p in prepared)
        indices = list(range(1, max_len, frame_stride))
        if not indices:
            indices = [max_len - 1]
        elif indices[-1] != max_len - 1:
            indices.append(max_len - 1)

        def to_u(idx, orig):
            return 0.0 if orig <= 1 else idx / (orig - 1)

        def end_idx(td, step):
            u = to_u(step, td["original_len"])
            i = np.searchsorted(td["u_fine"], u, side="right") - 1
            return max(0, min(i, len(td["x"]) - 1))

        init_step = indices[0]
        init_traces = []
        for td in prepared:
            s = min(init_step, td["original_len"] - 1)
            ei = end_idx(td, s)
            init_traces.append(go.Scatter3d(
                x=td["x"][:ei+1], y=td["y"][:ei+1], z=td["z"][:ei+1],
                mode="lines", line=dict(color=td["color"], width=4),
                name=td["label"]
            ))

        frames = []
        for step in indices:
            fd = []
            for td in prepared:
                eff = min(step, td["original_len"] - 1)
                ei = end_idx(td, eff)
                fd.append(go.Scatter3d(
                    x=td["x"][:ei+1], y=td["y"][:ei+1], z=td["z"][:ei+1],
                    mode="lines", line=dict(color=td["color"], width=4),
                    name=td["label"]
                ))
            frames.append(go.Frame(data=fd, name=str(step)))

        fig = go.Figure(data=init_traces, frames=frames)
        fig.update_layout(
            title=simulation.title,
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
            updatemenus=[{
                "type": "buttons", "showactive": False,
                "buttons": [
                    {"label": "▶ Play", "method": "animate",
                     "args": [None, {"frame": {"duration": 50, "redraw": True},
                                     "fromcurrent": True,
                                     "transition": {"duration": 0}}]},
                    {"label": "⏸ Pause", "method": "animate",
                     "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                       "mode": "immediate"}]}
                ], "x": 0.1, "y": 0
            }],
            sliders=[{
                "steps": [
                    {"args": [[str(s)], {"frame": {"duration": 0, "redraw": True},
                                         "mode": "immediate",
                                         "transition": {"duration": 0}}],
                     "label": str(s), "method": "animate"}
                    for s in indices
                ],
                "x": 0.1, "len": 0.8,
                "currentvalue": {"prefix": "Krok: "}
            }],
            margin=dict(l=0, r=0, b=0, t=40)
        )
        return fig

    # ══════════════════════════════════════════════
    # Statický graf (bez animace)
    # ══════════════════════════════════════════════
    def create_static_figure(self, simulation):
        trajectories = simulation.trajectories
        if not trajectories:
            raise ValueError("Žádné trajektorie.")

        use_bspline = simulation.use_bspline
        ppi = max(1, simulation.points_per_interval)
        bs_method = simulation.bspline_method

        traces = []
        for traj in trajectories:
            if len(traj.x) == 0:
                continue
            if use_bspline:
                sx, sy, sz, _ = self._get_bspline_data(
                    traj.x, traj.y, traj.z, 0.0, ppi, bs_method)
            else:
                sx, sy, sz = traj.x, traj.y, traj.z

            traces.append(go.Scatter3d(
                x=sx, y=sy, z=sz,
                mode="lines", line=dict(color=traj.color, width=3),
                name=traj.label
            ))

        fig = go.Figure(data=traces)
        fig.update_layout(
            title=simulation.title,
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        return fig

    # ══════════════════════════════════════════════
    # Porovnání: numerická data vs B-spline
    # ══════════════════════════════════════════════
    def create_comparison_figure(self, traj, bspline_method="scipy",
                                  smoothing=1.0, pocet_novych_bodu=5000, k=3):
        if len(traj.x) == 0:
            raise ValueError("Trajektorie nemá data.")

        orig_x = np.array(traj.x, dtype=float)
        orig_y = np.array(traj.y, dtype=float)
        orig_z = np.array(traj.z, dtype=float)

        traj_array = np.column_stack((orig_x, orig_y, orig_z))

        if bspline_method == "cox_de_boor":
            smooth = BSpline.cox_de_boor_smooth(traj_array, k=k,
                                                 pocet_novych_bodu=pocet_novych_bodu)
        else:
            smooth = BSpline.scipy_smooth(traj_array, s=smoothing,
                                           pocet_novych_bodu=pocet_novych_bodu)

        trace_orig = go.Scatter3d(
            x=orig_x, y=orig_y, z=orig_z,
            mode="lines+markers",
            marker=dict(size=2, color="red"),
            line=dict(color="red", width=2, dash="dash"),
            name="Numerická trajektorie"
        )

        trace_spline = go.Scatter3d(
            x=smooth[:, 0], y=smooth[:, 1], z=smooth[:, 2],
            mode="lines",
            line=dict(color="blue", width=3),
            name=f"B-spline ({bspline_method})"
        )

        fig = go.Figure(data=[trace_orig, trace_spline])
        fig.update_layout(
            title=f"Porovnání: {traj.label} – numerická vs. B-spline ({bspline_method})",
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        return fig

    # ══════════════════════════════════════════════
    # Veřejné metody
    # ══════════════════════════════════════════════
    def show_animated(self, simulation):
        self.create_animated_figure(simulation).show()

    def show_static(self, simulation):
        self.create_static_figure(simulation).show()

    def show_comparison(self, traj, **kwargs):
        self.create_comparison_figure(traj, **kwargs).show()

    def save_html(self, simulation, path: str, animated=True):
        if animated:
            fig = self.create_animated_figure(simulation)
        else:
            fig = self.create_static_figure(simulation)
        fig.write_html(path)

    def save_comparison_html(self, traj, path: str, **kwargs):
        self.create_comparison_figure(traj, **kwargs).write_html(path)