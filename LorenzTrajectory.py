from dataclasses import dataclass, field


#dataclass pro jednu konkretni trajektorii systemu, uchovani vstupnich parametru, poc. podminek a nasledne vypocitanych dat
@dataclass
class LorenzTrajectory:
    #fyzikalni parametry systemu
    sigma: float
    beta: float
    rho: float
    #parametry numericke integrace
    dt: float
    steps: int
   #pocatecni podminky
    x0: float = 1.0
    y0: float = 1.0
    z0: float = 1.0
    #data pro GUI
    label: str = "Trajectory"
    color: str = "blue"


#vysledna data, ktera se naplni v LorenzSimulatoru
    t: list = field(default_factory=list)
    x: list = field(default_factory=list)
    y: list = field(default_factory=list)
    z: list = field(default_factory=list)


#pro ulozeni trajektorie do souboru JSON, JSON neumi ukldat objekty, ale jen texty a cisla
    def to_dict(self):
        return {
            "sigma": self.sigma,
            "beta": self.beta,
            "rho": self.rho,
            "dt": self.dt,
            "steps": self.steps,
            "x0": self.x0,
            "y0": self.y0,
            "z0": self.z0,
            "label": self.label,
            "color": self.color,
            "t": self.t,
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    @classmethod

    #vytvari novou intancni LorenzTrajectory z nactenych dat z JSON
    def from_dict(cls, data):
        obj = cls(
            sigma=data["sigma"],
            beta=data["beta"],
            rho=data["rho"],
            dt=data["dt"],
            steps=data["steps"],
            x0=data.get("x0", 1.0),
            y0=data.get("y0", 1.0),
            z0=data.get("z0", 1.0),
            label=data.get("label", "Trajectory"),
            color=data.get("color", "blue"),
        )

        
        obj.t = data.get("t", [])
        obj.x = data.get("x", [])
        obj.y = data.get("y", [])
        obj.z = data.get("z", [])
        return obj