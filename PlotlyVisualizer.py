import plotly.graph_objects as go


class PlotlyVisualizer:
    def create_animated_figure(self, simulation):
        trajectories = simulation.trajectories
        if not trajectories:
            raise ValueError("No trajectories to visualize.")

        frame_stride = max(1, simulation.frame_stride)

        max_len = max(len(traj.x) for traj in trajectories)
        frame_indices = list(range(1, max_len, frame_stride))
        if not frame_indices:
            frame_indices = [max_len - 1]
        elif frame_indices[-1] != max_len - 1:
            frame_indices.append(max_len - 1)

        initial_traces = []
        for traj in trajectories:
            end_idx = min(frame_indices[0], len(traj.x) - 1)
            initial_traces.append(
                go.Scatter3d(
                    x=traj.x[:end_idx + 1],
                    y=traj.y[:end_idx + 1],
                    z=traj.z[:end_idx + 1],
                    mode="lines",
                    line=dict(color=traj.color, width=4),
                    name=traj.label
                )
            )

        frames = []
        for idx in frame_indices:
            frame_data = []
            for traj in trajectories:
                end_idx = min(idx, len(traj.x) - 1)
                frame_data.append(
                    go.Scatter3d(
                        x=traj.x[:end_idx + 1],
                        y=traj.y[:end_idx + 1],
                        z=traj.z[:end_idx + 1],
                        mode="lines",
                        line=dict(color=traj.color, width=4),
                        name=traj.label
                    )
                )
            frames.append(go.Frame(data=frame_data, name=str(idx)))

        play_args = {
            "frame": {"duration": 50, "redraw": True},
            "fromcurrent": True,
            "transition": {"duration": 0},
            "mode": "immediate"
        }

        if simulation.loop:
            play_args["direction"] = "forward"

        sliders = [
            {
                "steps": [
                    {
                        "args": [
                            [str(idx)],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 0}
                            }
                        ],
                        "label": str(idx),
                        "method": "animate"
                    }
                    for idx in frame_indices
                ],
                "transition": {"duration": 0},
                "x": 0.1,
                "len": 0.8,
                "currentvalue": {"prefix": "Krok: "}
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