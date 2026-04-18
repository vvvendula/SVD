from dataclasses import dataclass, field
from LorenzTrajectory import LorenzTrajectory

@dataclass
class LorenzSimulation:
    trajectories: list = field(default_factory=list)
    frame_stride: int = 20
    loop: bool = True
    title: str = "Lorenz Simulation"
    use_bspline: bool = False
    points_per_interval: int = 5

    MAX_TRAJECTORIES = 5

    def add_trajectory(self, trajectory):
        if len(self.trajectories) >= self.MAX_TRAJECTORIES:
            raise ValueError("Maximum number of trajectories is 5.")
        self.trajectories.append(trajectory)

    def remove_trajectory(self, index: int):
        if 0 <= index < len(self.trajectories):
            self.trajectories.pop(index)

    def clear(self):
        self.trajectories.clear()

    def to_dict(self):
        return {
            "type": "lorenz_simulation",
            "version": 1,
            "title": self.title,
            "frame_stride": self.frame_stride,
            "loop": self.loop,
            "use_bspline": self.use_bspline,
            "points_per_interval": self.points_per_interval,
            "trajectories": [traj.to_dict() for traj in self.trajectories],
        }

    @classmethod
    def from_dict(cls, data):
        sim = cls(
            frame_stride=data.get("frame_stride", 20),
            loop=data.get("loop", True),
            title=data.get("title", "Lorenz Simulation"),
            use_bspline=data.get("use_bspline", False),
            points_per_interval=data.get("points_per_interval", 5),
        )
        for traj_data in data.get("trajectories", []):
            sim.add_trajectory(LorenzTrajectory.from_dict(traj_data))
        return sim