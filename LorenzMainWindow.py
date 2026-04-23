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


class LorenzMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lorenz System Simulator")
        self.resize(1200, 700)

        self.simulator = LorenzSimulator()
        self.storage = JSONStorage()
        self.visualizer = PlotlyVisualizer()
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
        group = QGroupBox("Parametry")
        layout = QVBoxLayout()
        group.setLayout(layout)
        form = QFormLayout()

        self.sigma_input = QLineEdit("10")
        self.beta_input = QLineEdit("2.6666667")
        self.rho_input = QLineEdit("28")
        self.dt_input = QLineEdit("0.01")
        self.steps_input = QLineEdit("3000")
        self.x0_input = QLineEdit("1.0")
        self.y0_input = QLineEdit("1.0")
        self.z0_input = QLineEdit("1.0")
        self.label_input = QLineEdit("Trajectory")

        self.solver_combo = QComboBox()
        self.solver_combo.addItems(["rk4", "solve_ivp"])

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
            f"background-color: {self.selected_color}; border: 1px solid black;")
        color_btn = QPushButton("Vybrat barvu")
        color_btn.clicked.connect(self._choose_color)
        color_row = QHBoxLayout()
        color_row.addWidget(self.color_preview)
        color_row.addWidget(color_btn)

        for label, widget in [
            ("Sigma", self.sigma_input), ("Beta", self.beta_input),
            ("Rho", self.rho_input), ("dt", self.dt_input),
            ("Steps", self.steps_input),
            ("x0", self.x0_input), ("y0", self.y0_input), ("z0", self.z0_input),
            ("Label", self.label_input),
        ]:
            form.addRow(label, widget)

        form.addRow("Barva", color_row)
        form.addRow("Solver", self.solver_combo)
        form.addRow("B-spline metoda", self.bspline_method_combo)
        form.addRow("Frame stride", self.frame_stride_input)
        form.addRow("Loop", self.loop_checkbox)
        form.addRow("Použít B-spline", self.bspline_checkbox)
        form.addRow("Bodů / interval", self.points_per_interval_input)

        layout.addLayout(form)

        buttons = [
            ("Přidat trajektorii", self._add_trajectory),
            ("Animovaný graf (Plotly)", self._show_animated),
            ("Statický graf (Plotly)", self._show_static),
            ("Porovnání se spline (Plotly)", self._show_comparison),
            ("Export animace → HTML", self._export_animated_html),
            ("Export statický → HTML", self._export_static_html),
            ("Export porovnání → HTML", self._export_comparison_html),
            ("Uložit JSON", self._save_json),
            ("Načíst JSON", self._load_json),
            ("Smazat vybranou", self._remove_selected),
            ("Vyčistit vše", self._clear_all),
            ("Přepočítat vše", self._resimulate_all),
            ("Změnit barvu vybrané", self._change_color),
        ]
        for label, slot in buttons:
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

    # ── Pomocné ──

    def _choose_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.selected_color = c.name()
            self.color_preview.setStyleSheet(
                f"background-color: {self.selected_color}; border: 1px solid black;")

    def _read_form(self):
        dt = float(self.dt_input.text())
        steps = int(self.steps_input.text())
        if dt <= 0:
            raise ValueError("dt musí být > 0.")
        if steps < 2:
            raise ValueError("steps musí být >= 2.")
        return LorenzTrajectory(
            sigma=float(self.sigma_input.text()),
            beta=float(self.beta_input.text()),
            rho=float(self.rho_input.text()),
            dt=dt, steps=steps,
            x0=float(self.x0_input.text()),
            y0=float(self.y0_input.text()),
            z0=float(self.z0_input.text()),
            label=self.label_input.text().strip() or "Trajectory",
            color=self.selected_color,
            use_bspline=self.bspline_checkbox.isChecked(),
            bspline_method=self.bspline_method_combo.currentText(),
            points_per_interval=self.points_per_interval_input.value(),
        )

    def _sync_settings(self):
        self.simulation.frame_stride = self.frame_stride_input.value()
        self.simulation.loop = self.loop_checkbox.isChecked()
        self.simulation.use_bspline = self.bspline_checkbox.isChecked()
        self.simulation.points_per_interval = self.points_per_interval_input.value()
        self.simulation.solver_method = self.solver_combo.currentText()
        self.simulation.bspline_method = self.bspline_method_combo.currentText()

    def _refresh_list(self):
        self.trajectory_list.clear()
        for i, t in enumerate(self.simulation.trajectories, 1):
            self.trajectory_list.addItem(
                f"{i}. {t.label} | {t.color} | "
                f"σ={t.sigma} β={t.beta} ρ={t.rho} "
                f"dt={t.dt} steps={t.steps} pts={len(t.x)}")

    def _selected_traj(self):
        row = self.trajectory_list.currentRow()
        if row < 0:
            raise ValueError("Vyber trajektorii ze seznamu.")
        return self.simulation.trajectories[row]

    def _err(self, text):
        QMessageBox.critical(self, "Chyba", text)

    def _info(self, text):
        QMessageBox.information(self, "Info", text)

    # ── Akce ──

    def _add_trajectory(self):
        try:
            self._sync_settings()
            traj = self._read_form()
            self.simulator.simulate(traj, method=self.simulation.solver_method)
            self.simulation.add_trajectory(traj)
            self._refresh_list()
            self._info(f"Přidáno (solver: {self.simulation.solver_method}).")
        except Exception as e:
            self._err(str(e))

    def _show_animated(self):
        try:
            self._sync_settings()
            if not self.simulation.trajectories:
                raise ValueError("Žádné trajektorie.")
            self.visualizer.show_animated(self.simulation)
        except Exception as e:
            self._err(str(e))

    def _show_static(self):
        try:
            self._sync_settings()
            if not self.simulation.trajectories:
                raise ValueError("Žádné trajektorie.")
            self.visualizer.show_static(self.simulation)
        except Exception as e:
            self._err(str(e))

    def _show_comparison(self):
        try:
            self._sync_settings()
            traj = self._selected_traj()
            self.visualizer.show_comparison(
                traj, bspline_method=self.simulation.bspline_method)
        except Exception as e:
            self._err(str(e))

    def _export_animated_html(self):
        try:
            self._sync_settings()
            if not self.simulation.trajectories:
                raise ValueError("Žádné trajektorie.")
            path, _ = QFileDialog.getSaveFileName(
                self, "Export animace", "", "HTML (*.html)")
            if path:
                self.visualizer.save_html(self.simulation, path, animated=True)
                self._info(f"Animace uložena: {path}")
        except Exception as e:
            self._err(str(e))

    def _export_static_html(self):
        try:
            self._sync_settings()
            if not self.simulation.trajectories:
                raise ValueError("Žádné trajektorie.")
            path, _ = QFileDialog.getSaveFileName(
                self, "Export statický", "", "HTML (*.html)")
            if path:
                self.visualizer.save_html(self.simulation, path, animated=False)
                self._info(f"Statický graf uložen: {path}")
        except Exception as e:
            self._err(str(e))

    def _export_comparison_html(self):
        try:
            self._sync_settings()
            traj = self._selected_traj()
            path, _ = QFileDialog.getSaveFileName(
                self, "Export porovnání", "", "HTML (*.html)")
            if path:
                self.visualizer.save_comparison_html(
                    traj, path, bspline_method=self.simulation.bspline_method)
                self._info(f"Porovnání uloženo: {path}")
        except Exception as e:
            self._err(str(e))

    def _save_json(self):
        try:
            self._sync_settings()
            if not self.simulation.trajectories:
                raise ValueError("Není co uložit.")
            path, _ = QFileDialog.getSaveFileName(
                self, "Uložit", "", "JSON (*.json)")
            if path:
                self.storage.save_simulation(self.simulation, path)
                self._info("Uloženo.")
        except Exception as e:
            self._err(str(e))

    def _load_json(self):
        try:
            path, _ = QFileDialog.getOpenFileName(
                self, "Načíst", "", "JSON (*.json)")
            if path:
                self.simulation = self.storage.load_simulation(path)
                self.frame_stride_input.setValue(self.simulation.frame_stride)
                self.loop_checkbox.setChecked(self.simulation.loop)
                self.bspline_checkbox.setChecked(self.simulation.use_bspline)
                self.points_per_interval_input.setValue(self.simulation.points_per_interval)
                idx = self.solver_combo.findText(self.simulation.solver_method)
                if idx >= 0:
                    self.solver_combo.setCurrentIndex(idx)
                idx2 = self.bspline_method_combo.findText(self.simulation.bspline_method)
                if idx2 >= 0:
                    self.bspline_method_combo.setCurrentIndex(idx2)
                self._refresh_list()
                self._info("Načteno.")
        except Exception as e:
            self._err(str(e))

    def _remove_selected(self):
        try:
            row = self.trajectory_list.currentRow()
            if row < 0:
                raise ValueError("Vyber trajektorii.")
            self.simulation.remove_trajectory(row)
            self._refresh_list()
        except Exception as e:
            self._err(str(e))

    def _clear_all(self):
        self.simulation.clear()
        self._refresh_list()
        self._info("Vyčištěno.")

    def _resimulate_all(self):
        try:
            self._sync_settings()
            if not self.simulation.trajectories:
                raise ValueError("Žádné trajektorie.")
            m = self.simulation.solver_method
            for traj in self.simulation.trajectories:
                self.simulator.simulate(traj, method=m)
            self._refresh_list()
            self._info(f"Přepočítáno (solver: {m}).")
        except Exception as e:
            self._err(str(e))

    def _change_color(self):
        try:
            row = self.trajectory_list.currentRow()
            if row < 0:
                raise ValueError("Vyber trajektorii.")
            c = QColorDialog.getColor()
            if c.isValid():
                self.simulation.trajectories[row].color = c.name()
                self._refresh_list()
                self._info("Barva změněna.")
        except Exception as e:
            self._err(str(e))