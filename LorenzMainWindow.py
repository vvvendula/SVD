from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QListWidget, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QSpinBox,
    QCheckBox, QColorDialog, QComboBox
)

from LorenzTrajectory import LorenzTrajectory
from LorenzSimulation import LorenzSimulation
from LorenzSimulator import LorenzSimulator
from JSONtoStorage import JSONStorage
from PlotlyVisualizer import PlotlyVisualizer
from MatplotlibVisualizer import MatplotlibVisualizer


class LorenzMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lorenz System Simulator")
        self.resize(1200, 700)

        self.simulator = LorenzSimulator()
        self.storage = JSONStorage()
        self.plotly_vis = PlotlyVisualizer()
        self.mpl_vis = MatplotlibVisualizer()
        self.simulation = LorenzSimulation()
        self.selected_color = "blue"

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        main_layout.addWidget(self._build_form_panel(), 0)
        main_layout.addWidget(self._build_list_panel(), 1)

    def _build_form_panel(self):
        group = QGroupBox("Parametry trajektorie")
        layout = QVBoxLayout()
        group.setLayout(layout)
        form = QFormLayout()

        # Vstupy
        self.sigma_input = QLineEdit("10")
        self.beta_input = QLineEdit("2.6666667")
        self.rho_input = QLineEdit("28")
        self.dt_input = QLineEdit("0.01")
        self.steps_input = QLineEdit("3000")
        self.x0_input = QLineEdit("1.0")
        self.y0_input = QLineEdit("1.0")
        self.z0_input = QLineEdit("1.0")
        self.label_input = QLineEdit("Trajectory")

        # Výběr solveru
        self.solver_combo = QComboBox()
        self.solver_combo.addItems(["rk4", "solve_ivp"])

        # Výběr B-spline metody
        self.bspline_method_combo = QComboBox()
        self.bspline_method_combo.addItems(["scipy", "cox_de_boor"])

        self.frame_stride_input = QSpinBox()
        self.frame_stride_input.setRange(1, 10000)
        self.frame_stride_input.setValue(20)

        self.loop_checkbox = QCheckBox()
        self.loop_checkbox.setChecked(True)

        self.bspline_checkbox = QCheckBox()
        self.bspline_checkbox.setChecked(False)

        self.points_per_interval_input = QSpinBox()
        self.points_per_interval_input.setRange(1, 100)
        self.points_per_interval_input.setValue(5)

        self.color_preview = QLabel("      ")
        self.color_preview.setStyleSheet(
            f"background-color: {self.selected_color}; border: 1px solid black;"
        )
        self.choose_color_btn = QPushButton("Vybrat barvu")
        self.choose_color_btn.clicked.connect(self.choose_color)

        color_layout = QHBoxLayout()
        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(self.choose_color_btn)

        form.addRow("Sigma", self.sigma_input)
        form.addRow("Beta", self.beta_input)
        form.addRow("Rho", self.rho_input)
        form.addRow("dt", self.dt_input)
        form.addRow("Steps", self.steps_input)
        form.addRow("x0", self.x0_input)
        form.addRow("y0", self.y0_input)
        form.addRow("z0", self.z0_input)
        form.addRow("Label", self.label_input)
        form.addRow("Barva", color_layout)
        form.addRow("Solver", self.solver_combo)
        form.addRow("B-spline metoda", self.bspline_method_combo)
        form.addRow("Frame stride", self.frame_stride_input)
        form.addRow("Loop", self.loop_checkbox)
        form.addRow("Použít B-spline", self.bspline_checkbox)
        form.addRow("Bodů / interval", self.points_per_interval_input)

        layout.addLayout(form)

        # ── Tlačítka ──
        buttons = {
            "Přidat trajektorii": self.add_trajectory,
            "Plotly graf": self.show_plotly,
            "Matplotlib graf": self.show_matplotlib,
            "Matplotlib porovnání (spline)": self.show_matplotlib_comparison,
            "Matplotlib animace (MP4)": self.show_matplotlib_animation,
            "Uložit JSON": self.save_simulation,
            "Načíst JSON": self.load_simulation,
            "Export HTML": self.export_html,
            "Smazat vybranou": self.remove_selected,
            "Vyčistit vše": self.clear_all,
            "Přepočítat vše": self.resimulate_all,
            "Změnit barvu vybrané": self.change_selected_trajectory_color,
        }

        for label, slot in buttons.items():
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        layout.addStretch()
        return group

    def _build_list_panel(self):
        group = QGroupBox("Trajektorie")
        layout = QVBoxLayout()
        group.setLayout(layout)
        self.trajectory_list = QListWidget()
        layout.addWidget(self.trajectory_list)
        return group

    # ── Pomocné metody ──

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_preview.setStyleSheet(
                f"background-color: {self.selected_color}; border: 1px solid black;"
            )

    def _read_form(self):
        sigma = float(self.sigma_input.text())
        beta = float(self.beta_input.text())
        rho = float(self.rho_input.text())
        dt = float(self.dt_input.text())
        steps = int(self.steps_input.text())
        x0 = float(self.x0_input.text())
        y0 = float(self.y0_input.text())
        z0 = float(self.z0_input.text())
        label = self.label_input.text().strip() or "Trajectory"

        if dt <= 0:
            raise ValueError("dt musí být > 0.")
        if steps < 2:
            raise ValueError("steps musí být >= 2.")

        return LorenzTrajectory(
            sigma=sigma, beta=beta, rho=rho,
            dt=dt, steps=steps,
            x0=x0, y0=y0, z0=z0,
            label=label, color=self.selected_color
        )

    def _update_simulation_settings(self):
        self.simulation.frame_stride = self.frame_stride_input.value()
        self.simulation.loop = self.loop_checkbox.isChecked()
        self.simulation.use_bspline = self.bspline_checkbox.isChecked()
        self.simulation.points_per_interval = self.points_per_interval_input.value()
        self.simulation.solver_method = self.solver_combo.currentText()
        self.simulation.bspline_method = self.bspline_method_combo.currentText()

    def refresh_list(self):
        self.trajectory_list.clear()
        for i, traj in enumerate(self.simulation.trajectories, start=1):
            self.trajectory_list.addItem(
                f"{i}. {traj.label} | {traj.color} | "
                f"σ={traj.sigma} β={traj.beta} ρ={traj.rho} "
                f"dt={traj.dt} steps={traj.steps} pts={len(traj.x)}"
            )

    def show_error(self, text):
        QMessageBox.critical(self, "Chyba", text)

    def show_info(self, text):
        QMessageBox.information(self, "Info", text)

    def _get_selected_traj(self):
        row = self.trajectory_list.currentRow()
        if row < 0:
            raise ValueError("Vyber trajektorii ze seznamu.")
        return self.simulation.trajectories[row]

    # ── Akce ──

    def add_trajectory(self):
        try:
            self._update_simulation_settings()
            traj = self._read_form()
            method = self.simulation.solver_method
            self.simulator.simulate(traj, method=method)
            self.simulation.add_trajectory(traj)
            self.refresh_list()
            self.show_info(f"Trajektorie přidána (solver: {method}).")
        except Exception as e:
            self.show_error(str(e))

    def show_plotly(self):
        try:
            self._update_simulation_settings()
            if not self.simulation.trajectories:
                raise ValueError("Žádné trajektorie.")
            self.plotly_vis.show(self.simulation)
        except Exception as e:
            self.show_error(str(e))

    def show_matplotlib(self):
        try:
            if not self.simulation.trajectories:
                raise ValueError("Žádné trajektorie.")
            self.mpl_vis.plot_multiple(self.simulation.trajectories)
        except Exception as e:
            self.show_error(str(e))

    def show_matplotlib_comparison(self):
        try:
            self._update_simulation_settings()
            traj = self._get_selected_traj()
            method = self.simulation.bspline_method
            self.mpl_vis.plot_comparison(traj, bspline_method=method)
        except Exception as e:
            self.show_error(str(e))

    def show_matplotlib_animation(self):
        try:
            self._update_simulation_settings()
            traj = self._get_selected_traj()
            path, _ = QFileDialog.getSaveFileName(
                self, "Uložit animaci", "video.mp4", "MP4 (*.mp4)"
            )
            if path:
                method = self.simulation.solver_method
                self.mpl_vis.animate(traj, solver_method=method, save_path=path)
                self.show_info(f"Animace uložena: {path}")
        except Exception as e:
            self.show_error(str(e))

    def save_simulation(self):
        try:
            self._update_simulation_settings()
            if not self.simulation.trajectories:
                raise ValueError("Není co uložit.")
            path, _ = QFileDialog.getSaveFileName(
                self, "Uložit simulaci", "", "JSON (*.json)"
            )
            if path:
                self.storage.save_simulation(self.simulation, path)
                self.show_info("Simulace uložena.")
        except Exception as e:
            self.show_error(str(e))

    def load_simulation(self):
        try:
            path, _ = QFileDialog.getOpenFileName(
                self, "Načíst simulaci", "", "JSON (*.json)"
            )
            if path:
                self.simulation = self.storage.load_simulation(path)
                self.frame_stride_input.setValue(self.simulation.frame_stride)
                self.loop_checkbox.setChecked(self.simulation.loop)
                self.bspline_checkbox.setChecked(self.simulation.use_bspline)
                self.points_per_interval_input.setValue(self.simulation.points_per_interval)

                idx_solver = self.solver_combo.findText(self.simulation.solver_method)
                if idx_solver >= 0:
                    self.solver_combo.setCurrentIndex(idx_solver)

                idx_bs = self.bspline_method_combo.findText(self.simulation.bspline_method)
                if idx_bs >= 0:
                    self.bspline_method_combo.setCurrentIndex(idx_bs)

                self.refresh_list()
                self.show_info("Simulace načtena.")
        except Exception as e:
            self.show_error(str(e))

    def export_html(self):
        try:
            self._update_simulation_settings()
            if not self.simulation.trajectories:
                raise ValueError("Není co exportovat.")
            path, _ = QFileDialog.getSaveFileName(
                self, "Export HTML", "", "HTML (*.html)"
            )
            if path:
                self.plotly_vis.save_html(self.simulation, path)
                self.show_info("HTML uložen.")
        except Exception as e:
            self.show_error(str(e))

    def remove_selected(self):
        try:
            row = self.trajectory_list.currentRow()
            if row < 0:
                raise ValueError("Vyber trajektorii.")
            self.simulation.remove_trajectory(row)
            self.refresh_list()
        except Exception as e:
            self.show_error(str(e))

    def clear_all(self):
        self.simulation.clear()
        self.refresh_list()
        self.show_info("Vše odstraněno.")

    def resimulate_all(self):
        try:
            self._update_simulation_settings()
            if not self.simulation.trajectories:
                raise ValueError("Žádné trajektorie.")
            method = self.simulation.solver_method
            for traj in self.simulation.trajectories:
                self.simulator.simulate(traj, method=method)
            self.refresh_list()
            self.show_info(f"Vše přepočítáno (solver: {method}).")
        except Exception as e:
            self.show_error(str(e))

    def change_selected_trajectory_color(self):
        try:
            row = self.trajectory_list.currentRow()
            if row < 0:
                raise ValueError("Vyber trajektorii.")
            color = QColorDialog.getColor()
            if color.isValid():
                self.simulation.trajectories[row].color = color.name()
                self.refresh_list()
                self.show_info("Barva změněna.")
        except Exception as e:
            self.show_error(str(e))