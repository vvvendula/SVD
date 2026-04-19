import numpy as np
from scipy.interpolate import splprep, splev


class BSpline:

    # ── scipy ──
    @staticmethod
    def scipy_smooth(traj_array, s=0.0, pocet_novych_bodu=5000):
        if len(traj_array) < 4:
            return traj_array.copy()
        tck, u = splprep(traj_array.T, s=s)
        u_new = np.linspace(0, 1, pocet_novych_bodu)
        result = splev(u_new, tck)
        return np.array(result).T

    @staticmethod
    def scipy_smooth_xyz(x, y, z, smoothing=0.0, points_per_interval=5):
        if len(x) < 4:
            arr_x, arr_y, arr_z = (np.array(v, dtype=float) for v in (x, y, z))
            return arr_x, arr_y, arr_z, np.linspace(0, 1, max(len(x), 1))
        try:
            tck, u = splprep([x, y, z], s=smoothing, k=min(3, len(x)-1))
            total = (len(x)-1) * max(1, points_per_interval) + 1
            u_fine = np.linspace(0, 1, total)
            sx, sy, sz = splev(u_fine, tck)
            return np.array(sx), np.array(sy), np.array(sz), u_fine
        except Exception:
            arr_x, arr_y, arr_z = (np.array(v, dtype=float) for v in (x, y, z))
            return arr_x, arr_y, arr_z, np.linspace(0, 1, max(len(x), 1))

    # ── Cox-de Boor ──
    @staticmethod
    def _cox_de_boor(i, k, t, knots):
        if k == 0:
            if t == knots[-1] and knots[i] <= t <= knots[i+1]:
                return 1.0
            return 1.0 if knots[i] <= t < knots[i+1] else 0.0

        d1 = knots[i+k] - knots[i]
        t1 = ((t - knots[i]) / d1) * BSpline._cox_de_boor(i, k-1, t, knots) if d1 > 0 else 0.0

        d2 = knots[i+k+1] - knots[i+1]
        t2 = ((knots[i+k+1] - t) / d2) * BSpline._cox_de_boor(i+1, k-1, t, knots) if d2 > 0 else 0.0

        return t1 + t2

    @staticmethod
    def cox_de_boor_smooth(traj_array, k=3, pocet_novych_bodu=300):
        n = len(traj_array) - 1
        if n < 1:
            return traj_array.copy()
        k = min(k, n)
        knots = np.concatenate(([0]*k, np.linspace(0, 1, n-k+2), [1]*k))
        t_values = np.linspace(0, 1, pocet_novych_bodu)
        result = np.zeros((pocet_novych_bodu, 3))
        for idx, t in enumerate(t_values):
            bod = np.zeros(3)
            for i in range(n+1):
                bod += BSpline._cox_de_boor(i, k, t, knots) * traj_array[i]
            result[idx] = bod
        return result

    @staticmethod
    def cox_de_boor_smooth_xyz(x, y, z, k=3, points_per_interval=5):
        traj = np.column_stack((x, y, z))
        total = max((len(x)-1) * points_per_interval + 1, 2)
        result = BSpline.cox_de_boor_smooth(traj, k=k, pocet_novych_bodu=total)
        u_fine = np.linspace(0, 1, len(result))
        return result[:, 0], result[:, 1], result[:, 2], u_fine