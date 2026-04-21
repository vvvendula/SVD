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

    def create_unified_figure(self, simulation):
        trajectories = simulation.trajectories
        if not trajectories:
            raise ValueError("Žádné trajektorie k vizualizaci.")

        frame_stride = max(1, simulation.frame_stride)
        use_bspline = simulation.use_bspline
        ppi = max(1, simulation.points_per_interval)
        bs_method = simulation.bspline_method

        prepared = []
        for traj in trajectories:
            if len(traj.x) == 0: continue
            
            if use_bspline:
                sx, sy, sz, uf = self._get_bspline_data(traj.x, traj.y, traj.z, ppi, bs_method)
            else:
                sx, sy, sz = np.array(traj.x), np.array(traj.y), np.array(traj.z)
                uf = np.linspace(0, 1, len(sx))

            prepared.append({
                "label": traj.label, "color": traj.color,
                "x": sx, "y": sy, "z": sz, "u_fine": uf,
                "original_len": len(traj.x)
            })

        max_orig_len = max(p["original_len"] for p in prepared)
        indices = list(range(0, max_orig_len, frame_stride))
        if indices[-1] != max_orig_len - 1:
            indices.append(max_orig_len - 1)

        fig = go.Figure()
        num_trajs = len(prepared)

        
        for td in prepared:
            fig.add_trace(go.Scatter3d(
                x=td["x"], y=td["y"], z=td["z"],
                mode="lines", name=f"{td['label']} (Plná)",
                line=dict(color=td["color"], width=3),
                visible=True
            ))

        
        for td in prepared:
            fig.add_trace(go.Scatter3d(
                x=[td["x"][0]], y=[td["y"][0]], z=[td["z"][0]],
                mode="lines", name=td["label"],
                line=dict(color=td["color"], width=4),
                visible=False
            ))

        def get_end_idx(td, step_idx):
            u = 0.0 if td["original_len"] <= 1 else step_idx / (td["original_len"] - 1)
            i = np.searchsorted(td["u_fine"], min(1.0, max(0.0, u)), side="right") - 1
            return max(0, min(i, len(td["x"]) - 1))

        
        frames = []
        for step in indices:
            frame_data = []
            for i in range(num_trajs):
                frame_data.append(go.Scatter3d(x=prepared[i]["x"], y=prepared[i]["y"], z=prepared[i]["z"]))
            for td in prepared:
                ei = get_end_idx(td, min(step, td["original_len"] - 1))
                frame_data.append(go.Scatter3d(x=td["x"][:ei+1], y=td["y"][:ei+1], z=td["z"][:ei+1]))
            frames.append(go.Frame(data=frame_data, name=str(step)))

        fig.frames = frames

        
        vis_static = [True] * num_trajs + [False] * num_trajs
        vis_anim = [False] * num_trajs + [True] * num_trajs

        
        animation_slider = {
            "steps": [
                {"args": [[str(s)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                 "label": str(s), "method": "animate"} for s in indices
            ],
            "x": 0.1, "len": 0.8, "currentvalue": {"prefix": "Krok: "}
        }

        play_pause_menu = {
            "type": "buttons", "showactive": False, "x": 0.1, "y": 0, "visible": False, 
            "buttons": [
                {"label": "▶ Play", "method": "animate",
                 "args": [None, {"frame": {"duration": 30, "redraw": True}, "fromcurrent": True}]},
                {"label": "⏸ Pause", "method": "animate",
                 "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
            ]
        }

        fig.update_layout(
            updatemenus=[
              
                {
                    "type": "buttons", "direction": "left", "x": 0.1, "y": 1.15,
                    "buttons": [
                        {
                            "label": "📊 Statický pohled", 
                            "method": "update", 
                            "args": [
                                {"visible": vis_static}, 
                                {
                                    "title": "Lorenz Simulation - Statický",
                                    "sliders": [],  
                                    "updatemenus[1].visible": False 
                                }
                            ]
                        },
                        {
                            "label": "🎥 Animace", 
                            "method": "update", 
                            "args": [
                                {"visible": vis_anim}, 
                                {
                                    "title": "Lorenz Simulation - Animace",
                                    "sliders": [animation_slider], 
                                    "updatemenus[1].visible": True  
                                }
                            ]
                        }
                    ]
                },
                play_pause_menu 
            ],
            sliders=[], 
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
            title=simulation.title,
            margin=dict(l=0, r=0, b=0, t=50)
        )
        return fig

    # ══════════════════════════════════════════════
    # Veřejné metody
    # ══════════════════════════════════════════════

    def show_comparison(self, traj, **kwargs):
        self.create_comparison_figure(traj, **kwargs).show()


    def save_html(self, simulation, path: str):
        fig = self.create_unified_figure(simulation)
        fig.write_html(path)

    def save_comparison_html(self, traj, path: str, **kwargs):
        self.create_comparison_figure(traj, **kwargs).write_html(path)

    def show(self, simulation):
        self.create_unified_figure(simulation).show()

    def save_html(self, simulation, path: str):
        self.create_unified_figure(simulation).write_html(path)