import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QListWidget, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QSpinBox,
    QCheckBox, QColorDialog
)
from PySide6.QtGui import QColor

from LorenzTrajecktory import LorenzTrajectory
from LorenzSimulation import LorenzSimulation
from LorenzSimulator import LorenzSimulator
from JSONtoStorage import JSONStorage
from PlotlyVisualizer import PlotlyVisualizer


class LorenzMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lorenz System Simulator")
        self.resize(1100, 650)

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

        left_panel = self._build_form_panel()
        right_panel = self._build_list_panel()

        main_layout.addWidget(left_panel, 0)
        main_layout.addWidget(right_panel, 1)

    def _build_form_panel(self):
        group = QGroupBox("Parametry trajektorie")
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

        self.frame_stride_input = QSpinBox()
        self.frame_stride_input.setMinimum(1)
        self.frame_stride_input.setMaximum(10000)
        self.frame_stride_input.setValue(20)

        self.loop_checkbox = QCheckBox()
        self.loop_checkbox.setChecked(True)

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
        form.addRow("Frame stride", self.frame_stride_input)
        form.addRow("Loop", self.loop_checkbox)

        layout.addLayout(form)

        self.add_btn = QPushButton("Přidat trajektorii")
        self.show_btn = QPushButton("Zobrazit graf")
        self.save_json_btn = QPushButton("Uložit simulaci JSON")
        self.load_json_btn = QPushButton("Načíst simulaci JSON")
        self.export_html_btn = QPushButton("Export HTML player")
        self.remove_btn = QPushButton("Smazat vybranou")
        self.clear_btn = QPushButton("Vyčistit vše")
        self.resimulate_btn = QPushButton("Přepočítat načtené trajektorie")
        self.change_color_btn = QPushButton("Změnit barvu vybrané trajektorie")

        self.add_btn.clicked.connect(self.add_trajectory)
        self.show_btn.clicked.connect(self.show_plot)
        self.save_json_btn.clicked.connect(self.save_simulation)
        self.load_json_btn.clicked.connect(self.load_simulation)
        self.export_html_btn.clicked.connect(self.export_html)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.clear_btn.clicked.connect(self.clear_all)
        self.resimulate_btn.clicked.connect(self.resimulate_all)
        self.change_color_btn.clicked.connect(self.change_selected_trajectory_color)

        layout.addWidget(self.add_btn)
        layout.addWidget(self.show_btn)
        layout.addWidget(self.save_json_btn)
        layout.addWidget(self.load_json_btn)
        layout.addWidget(self.export_html_btn)
        layout.addWidget(self.remove_btn)
        layout.addWidget(self.clear_btn)
        layout.addWidget(self.resimulate_btn)
        layout.addWidget(self.change_color_btn)
        layout.addStretch()

        return group

    def _build_list_panel(self):
        group = QGroupBox("Trajektorie")
        layout = QVBoxLayout()
        group.setLayout(layout)

        self.trajectory_list = QListWidget()
        layout.addWidget(self.trajectory_list)

        return group

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
            sigma=sigma,
            beta=beta,
            rho=rho,
            dt=dt,
            steps=steps,
            x0=x0,
            y0=y0,
            z0=z0,
            label=label,
            color=self.selected_color
        )

    def _update_simulation_settings(self):
        self.simulation.frame_stride = self.frame_stride_input.value()
        self.simulation.loop = self.loop_checkbox.isChecked()

    def refresh_list(self):
        self.trajectory_list.clear()
        for i, traj in enumerate(self.simulation.trajectories, start=1):
            self.trajectory_list.addItem(
                f"{i}. {traj.label} | color={traj.color} | "
                f"sigma={traj.sigma}, beta={traj.beta}, rho={traj.rho}, "
                f"dt={traj.dt}, steps={traj.steps}, points={len(traj.x)}"
            )

    def show_error(self, text):
        QMessageBox.critical(self, "Chyba", text)

    def show_info(self, text):
        QMessageBox.information(self, "Info", text)

    def add_trajectory(self):
        try:
            self._update_simulation_settings()
            traj = self._read_form()
            self.simulator.simulate(traj)
            self.simulation.add_trajectory(traj)
            self.refresh_list()
            self.show_info("Trajektorie byla přidána a spočítána.")
        except Exception as e:
            self.show_error(str(e))

    def show_plot(self):
        try:
            self._update_simulation_settings()
            if not self.simulation.trajectories:
                raise ValueError("Nejsou k dispozici žádné trajektorie.")
            self.visualizer.show(self.simulation)
        except Exception as e:
            self.show_error(str(e))

    def save_simulation(self):
        try:
            self._update_simulation_settings()
            if not self.simulation.trajectories:
                raise ValueError("Není co uložit.")

            path, _ = QFileDialog.getSaveFileName(
                self,
                "Uložit simulaci",
                "",
                "JSON files (*.json)"
            )
            if path:
                self.storage.save_simulation(self.simulation, path)
                self.show_info("Simulace byla uložena do JSON.")
        except Exception as e:
            self.show_error(str(e))

    def load_simulation(self):
        try:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Načíst simulaci",
                "",
                "JSON files (*.json)"
            )
            if path:
                self.simulation = self.storage.load_simulation(path)
                self.frame_stride_input.setValue(self.simulation.frame_stride)
                self.loop_checkbox.setChecked(self.simulation.loop)
                self.refresh_list()
                self.show_info("Simulace byla načtena.")
        except Exception as e:
            self.show_error(str(e))

    def export_html(self):
        try:
            self._update_simulation_settings()
            if not self.simulation.trajectories:
                raise ValueError("Není co exportovat.")

            path, _ = QFileDialog.getSaveFileName(
                self,
                "Export HTML playeru",
                "",
                "HTML files (*.html)"
            )
            if path:
                self.visualizer.save_html(self.simulation, path)
                self.show_info("HTML player byl uložen.")
        except Exception as e:
            self.show_error(str(e))

    def remove_selected(self):
        try:
            row = self.trajectory_list.currentRow()
            if row < 0:
                raise ValueError("Vyber trajektorii k odstranění.")
            self.simulation.remove_trajectory(row)
            self.refresh_list()
        except Exception as e:
            self.show_error(str(e))

    def clear_all(self):
        self.simulation.clear()
        self.refresh_list()
        self.show_info("Všechny trajektorie byly odstraněny.")

    def resimulate_all(self):
        try:
            if not self.simulation.trajectories:
                raise ValueError("Nejsou žádné trajektorie k přepočtu.")

            for traj in self.simulation.trajectories:
                self.simulator.simulate(traj)

            self.refresh_list()
            self.show_info("Všechny trajektorie byly znovu přepočítány.")
        except Exception as e:
            self.show_error(str(e))

    def change_selected_trajectory_color(self):
        try:
            row = self.trajectory_list.currentRow()
            if row < 0:
                raise ValueError("Vyber trajektorii, které chceš změnit barvu.")

            color = QColorDialog.getColor()
            if not color.isValid():
                return

            self.simulation.trajectories[row].color = color.name()
            self.refresh_list()
            self.show_info("Barva trajektorie byla změněna.")
        except Exception as e:
            self.show_error(str(e))


def main():
    app = QApplication(sys.argv)
    window = LorenzMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()