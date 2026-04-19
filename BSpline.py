import numpy as np
from scipy.interpolate import splprep, splev


class BSpline:
    """Dvě metody B-spline vyhlazení: scipy a vlastní Cox-de Boor."""

    # ══════════════════════════════════════════
    # Metoda 1: scipy splprep/splev
    # ══════════════════════════════════════════
    @staticmethod
    def scipy_smooth(traj_array, s=0.0, pocet_novych_bodu=5000):
        """
        traj_array: np.ndarray tvaru (N, 3)
        Vrací: np.ndarray tvaru (pocet_novych_bodu, 3)
        """
        if len(traj_array) < 4:
            return traj_array.copy()

        tck, u = splprep(traj_array.T, s=s)
        u_new = np.linspace(0, 1, pocet_novych_bodu)
        traj_spline = splev(u_new, tck)
        return np.array(traj_spline).T

    @staticmethod
    def scipy_smooth_xyz(x, y, z, smoothing=0.0, points_per_interval=5):
        """
        Varianta pro PlotlyVisualizer – vstup jako 3 seznamy,
        vrací (spline_x, spline_y, spline_z, u_fine).
        """
        if len(x) < 4:
            arr_x = np.array(x, dtype=float)
            arr_y = np.array(y, dtype=float)
            arr_z = np.array(z, dtype=float)
            u_fine = np.linspace(0, 1, max(len(x), 1))
            return arr_x, arr_y, arr_z, u_fine

        try:
            points = np.array([x, y, z], dtype=float)
            tck, u = splprep(points, s=smoothing, k=min(3, len(x) - 1))
            total_points = (len(x) - 1) * max(1, points_per_interval) + 1
            u_fine = np.linspace(0, 1, total_points)
            sx, sy, sz = splev(u_fine, tck)
            return np.array(sx), np.array(sy), np.array(sz), u_fine
        except Exception:
            arr_x = np.array(x, dtype=float)
            arr_y = np.array(y, dtype=float)
            arr_z = np.array(z, dtype=float)
            u_fine = np.linspace(0, 1, max(len(x), 1))
            return arr_x, arr_y, arr_z, u_fine

    # ══════════════════════════════════════════
    # Metoda 2: vlastní Cox-de Boor
    # ══════════════════════════════════════════
    @staticmethod
    def _cox_de_boor(i, k, t, knots):
        if k == 0:
            if t == knots[-1] and knots[i] <= t <= knots[i + 1]:
                return 1.0
            if knots[i] <= t < knots[i + 1]:
                return 1.0
            return 0.0

        denom1 = knots[i + k] - knots[i]
        term1 = 0.0
        if denom1 > 0:
            term1 = ((t - knots[i]) / denom1) * BSpline._cox_de_boor(i, k - 1, t, knots)

        denom2 = knots[i + k + 1] - knots[i + 1]
        term2 = 0.0
        if denom2 > 0:
            term2 = ((knots[i + k + 1] - t) / denom2) * BSpline._cox_de_boor(i + 1, k - 1, t, knots)

        return term1 + term2

    @staticmethod
    def cox_de_boor_smooth(traj_array, k=3, pocet_novych_bodu=300):
        """
        Vlastní implementace B-spline pomocí Cox-de Boor algoritmu.
        traj_array: np.ndarray tvaru (N, 3)
        Vrací: np.ndarray tvaru (pocet_novych_bodu, 3)
        """
        n = len(traj_array) - 1
        if n < 1:
            return traj_array.copy()

        k = min(k, n)
        knots = np.concatenate(([0] * k, np.linspace(0, 1, n - k + 2), [1] * k))

        t_values = np.linspace(0, 1, pocet_novych_bodu)
        vysledna_krivka = np.zeros((pocet_novych_bodu, 3))

        for idx, t in enumerate(t_values):
            bod = np.zeros(3)
            for i in range(n + 1):
                bod += BSpline._cox_de_boor(i, k, t, knots) * traj_array[i]
            vysledna_krivka[idx] = bod

        return vysledna_krivka

    @staticmethod
    def cox_de_boor_smooth_xyz(x, y, z, k=3, points_per_interval=5):
        """
        Varianta pro PlotlyVisualizer – vstup jako 3 seznamy.
        """
        traj = np.column_stack((x, y, z))
        total_points = max((len(x) - 1) * points_per_interval + 1, 2)
        result = BSpline.cox_de_boor_smooth(traj, k=k, pocet_novych_bodu=total_points)
        u_fine = np.linspace(0, 1, len(result))
        return result[:, 0], result[:, 1], result[:, 2], u_fine