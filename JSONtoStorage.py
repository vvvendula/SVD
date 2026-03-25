import json
from LorenzTrajecktory import LorenzTrajectory
from LorenzSimulation import LorenzSimulation


class JSONStorage:
    def save_trajectory(self, trajectory: LorenzTrajectory, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(trajectory.to_dict(), f, ensure_ascii=False, indent=2)

    def load_trajectory(self, path: str) -> LorenzTrajectory:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return LorenzTrajectory.from_dict(data)

    def save_simulation(self, simulation: LorenzSimulation, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(simulation.to_dict(), f, ensure_ascii=False, indent=2)

    def load_simulation(self, path: str) -> LorenzSimulation:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return LorenzSimulation.from_dict(data)