import numpy as np
import plotly.graph_objects as go
from BSpline import BSpline


class PlotlyVisualizer:

    def _get_bspline_data(self, x, y, z, smoothing=0.0, points_per_interval=5, method="scipy"):
        if method == "cox_de_boor":
            return BSpline.cox_de_boor_smooth_xyz(x, y, z, k=3,
                                                   points_per_interval=points_per_interval)
        return BSpline.scipy_smooth_xyz(x, y, z, smoothing=smoothing,
                                        points_per_interval=points_per_interval)

<<<<<<< Updated upstream
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
=======
>>>>>>> Stashed changes
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
        fig = go.Figure(data=[
            go.Scatter3d(x=orig_x, y=orig_y, z=orig_z, mode="lines+markers",
                         marker=dict(size=2, color="red"),
                         line=dict(color="red", width=2, dash="dash"),
                         name="Numerická trajektorie"),
            go.Scatter3d(x=smooth[:, 0], y=smooth[:, 1], z=smooth[:, 2],
                         mode="lines", line=dict(color="blue", width=3),
                         name=f"B-spline ({bspline_method})")
        ])
        fig.update_layout(
            title=f"Porovnání: {traj.label} – numerická vs. B-spline ({bspline_method})",
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
            margin=dict(l=0, r=0, b=0, t=40))
        return fig

<<<<<<< Updated upstream
    # ══════════════════════════════════════════════
    # Veřejné metody
    # ══════════════════════════════════════════════
    def show_animated(self, simulation):
        self.create_animated_figure(simulation).show()

    def show_static(self, simulation):
        self.create_static_figure(simulation).show()
=======
    def _prepare_trajectory(self, traj):
        orig_t = np.array(traj.t, dtype=float) if len(traj.t) > 0 \
            else np.arange(len(traj.x)) * traj.dt

        if traj.use_bspline:
            sx, sy, sz, uf = self._get_bspline_data(
                traj.x, traj.y, traj.z,
                smoothing=0.0,
                points_per_interval=traj.points_per_interval,
                method=traj.bspline_method)
            name = f"{traj.label} (B-spline/{traj.bspline_method})"
            curve_t = np.interp(uf, np.linspace(0, 1, len(orig_t)), orig_t)
        else:
            sx = np.array(traj.x, dtype=float)
            sy = np.array(traj.y, dtype=float)
            sz = np.array(traj.z, dtype=float)
            name = traj.label
            curve_t = orig_t

        return {
            "label": traj.label,
            "name": name,
            "color": traj.color,
            "x": [float(v) for v in sx],
            "y": [float(v) for v in sy],
            "z": [float(v) for v in sz],
            "t": [float(v) for v in curve_t],
            "t_max": float(curve_t[-1]),
            "total_len": len(sx),
        }

    @staticmethod
    def _index_at_time(td, t_current):
        if t_current >= td["t_max"]:
            return td["total_len"] - 1
        if t_current <= 0:
            return 0
        idx = int(np.searchsorted(td["t"], t_current, side="right")) - 1
        return max(0, min(idx, td["total_len"] - 1))

    # ══════════════════════════════════════════════
    # Generování tlačítek pro přepínání viditelnosti
    # ══════════════════════════════════════════════
    @staticmethod
    def _build_visibility_buttons(prepared):
        """
        Vytvoří tlačítka:
        - 'Všechny' → zobrazí vše
        - 'T1', 'T2', ... → solo zobrazení jedné trajektorie
        - 'Přepnout T1', ... → toggle jedné trajektorie
        """
        num = len(prepared)
        buttons = []

        # Tlačítko "Všechny zapnout"
        buttons.append({
            "label": "👁 Všechny",
            "method": "restyle",
            "args": [{"visible": [True] * num}],
        })

        # Tlačítko "Všechny vypnout"
        buttons.append({
            "label": "🚫 Žádná",
            "method": "restyle",
            "args": [{"visible": [False] * num}],
        })

        # Solo tlačítka – zobrazí jen jednu trajektorii
        for i, td in enumerate(prepared):
            vis = [False] * num
            vis[i] = True
            buttons.append({
                "label": f"Solo: {td['label']}",
                "method": "restyle",
                "args": [{"visible": vis}],
            })

        return buttons

    def create_unified_figure(self, simulation,
                               num_anim_frames=200,
                               animation_duration_sec=10.0):
        trajectories = simulation.trajectories
        if not trajectories:
            raise ValueError("Žádné trajektorie k vizualizaci.")

        frame_duration_ms = int((animation_duration_sec * 1000) / max(1, num_anim_frames))

        # ── 1) Příprava dat ──
        prepared = []
        for traj in trajectories:
            if len(traj.x) == 0:
                continue
            prepared.append(self._prepare_trajectory(traj))

        if not prepared:
            raise ValueError("Žádné trajektorie s daty.")

        # ── 2) Globální časový rozsah ──
        global_t_max = max(td["t_max"] for td in prepared)
        time_steps = np.linspace(0.0, global_t_max, num_anim_frames)

        num_trajs = len(prepared)
        trace_indices = list(range(num_trajs))

        fig = go.Figure()

        # ── 3) Base traces ──
        for td in prepared:
            fig.add_trace(go.Scatter3d(
                x=td["x"], y=td["y"], z=td["z"],
                mode="lines",
                name=td["name"],
                legendgroup=td["label"],
                showlegend=True,
                visible=True,
                line=dict(color=td["color"], width=3),
            ))

        # ── 4) Animační snímky ──
        frames = []
        for t_cur in time_steps:
            frame_data = []
            for td in prepared:
                ei = self._index_at_time(td, float(t_cur))
                frame_data.append(go.Scatter3d(
                    x=list(td["x"][:ei + 1]),
                    y=list(td["y"][:ei + 1]),
                    z=list(td["z"][:ei + 1]),
                    mode="lines",
                    line=dict(color=td["color"], width=3),
                ))
            frames.append(go.Frame(
                data=frame_data,
                name=f"{t_cur:.2f}",
                traces=trace_indices,
            ))

        # ── 5) Snímek "full" ──
        full_data = [go.Scatter3d(
            x=list(td["x"]), y=list(td["y"]), z=list(td["z"]),
            mode="lines", line=dict(color=td["color"], width=3),
        ) for td in prepared]
        frames.append(go.Frame(data=full_data, name="full", traces=trace_indices))

        fig.frames = frames

        # ── 6) Slider ──
        slider = {
            "steps": [
                {"args": [[f"{t:.2f}"],
                          {"frame": {"duration": frame_duration_ms, "redraw": True},
                           "mode": "immediate"}],
                 "label": f"{t:.1f}",
                 "method": "animate"}
                for t in time_steps
            ],
            "x": 0.1, "len": 0.8,
            "currentvalue": {"prefix": "Čas t = "},
            "visible": True,
        }

        # ── 7) Tlačítka pro viditelnost ──
        visibility_buttons = self._build_visibility_buttons(prepared)

        # ── 8) Layout ──
        fig.update_layout(
            updatemenus=[
                # Řádek 1: Animační tlačítka (vlevo nahoře)
                {
                    "type": "buttons",
                    "direction": "left",
                    "x": 0.0,
                    "y": 1.18,
                    "xanchor": "left",
                    "yanchor": "top",
                    "pad": {"r": 10, "t": 10},
                    "buttons": [
                        {
                            "label": "📊 Statický",
                            "method": "animate",
                            "args": [["full"],
                                     {"frame": {"duration": 0, "redraw": True},
                                      "mode": "immediate"}],
                        },
                        {
                            "label": "▶ Play",
                            "method": "animate",
                            "args": [None, {
                                "frame": {"duration": frame_duration_ms, "redraw": True},
                                "fromcurrent": False,
                                "transition": {"duration": 0},
                            }],
                        },
                        {
                            "label": "⏹ Stop",
                            "method": "animate",
                            "args": [[None],
                                     {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate"}],
                        },
                    ],
                },
                # Řádek 2: Dropdown pro viditelnost (vpravo nahoře)
                {
                    "type": "dropdown",
                    "direction": "down",
                    "x": 1.0,
                    "y": 1.18,
                    "xanchor": "right",
                    "yanchor": "top",
                    "pad": {"r": 10, "t": 10},
                    "showactive": True,
                    "active": 0,
                    "buttons": visibility_buttons,
                },
            ],
            sliders=[slider],
            legend=dict(
                itemclick="toggle",
                itemdoubleclick="toggleothers",
                title=dict(text="Trajektorie (klik = přepnout)"),
                x=1.02,
                y=0.95,
            ),
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
            title=simulation.title,
            margin=dict(l=0, r=0, b=0, t=80),
        )
        return fig
>>>>>>> Stashed changes

    def show_comparison(self, traj, **kwargs):
        self.create_comparison_figure(traj, **kwargs).show()

<<<<<<< Updated upstream
    def save_html(self, simulation, path: str, animated=True):
        if animated:
            fig = self.create_animated_figure(simulation)
        else:
            fig = self.create_static_figure(simulation)
        fig.write_html(path)

=======
>>>>>>> Stashed changes
    def save_comparison_html(self, traj, path: str, **kwargs):
        self.create_comparison_figure(traj, **kwargs).write_html(path)