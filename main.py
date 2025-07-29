import sys
import os
import ast
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableView, QLabel, QComboBox,
    QPushButton, QCheckBox
)
from scipy.spatial import cKDTree
from browser.audioplayer import AudioPlayer
from browser.data_model import SampleDataModel
from browser.table_model import PandasTableModel

import pyqtgraph as pg


class MainWindow(QWidget):
    def __init__(self, csv_path):
        super().__init__()
        self.setWindowTitle("Sample Datenbrowser")
        self.kdtree = None

        # Model
        self.data_model = SampleDataModel(csv_path)
        self.table_model = PandasTableModel(
            self.data_model.df_filtered,
            columns=['stem', 'duration', 'channels',
                     'tonality', 'tempo', 'bit_depth',]
        )
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)

        self.audio_player = AudioPlayer()
        self.selected_file = None

        # Layouts
        self.layout = QVBoxLayout()

        self.plot_widget = pg.PlotWidget()
        self.scatter = pg.ScatterPlotItem(
            size=5, pen=None, brush=pg.mkBrush(0, 0, 255, 120)
        )
        self.plot_widget.addItem(self.scatter)

        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Suche in Samples...")
        self.info_label = QLabel("Dateien gefiltert:")

        self.table_view.setModel(self.table_model)

        self.x_combo = QComboBox()
        self.y_combo = QComboBox()

        self.scatter_cols = [
            'duration', 'tempo', 'brightness',
            'loudness', 'spectral_centroid',
            'hardness', 'depth', 'roughness',
            'warmth', 'sharpness'
        ]

        self.x_combo.addItems(self.scatter_cols)
        self.y_combo.addItems(self.scatter_cols)

        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")
        self.loop_check = QCheckBox("Loop")

        # Player Layout
        player_layout = QHBoxLayout()
        player_layout.addWidget(self.play_btn)
        player_layout.addWidget(self.stop_btn)
        player_layout.addWidget(self.loop_check)

        self.layout.addLayout(player_layout)

        axis_layout = QHBoxLayout()
        axis_layout.addWidget(QLabel("X-Achse:"))
        axis_layout.addWidget(self.x_combo)
        axis_layout.addWidget(QLabel("Y-Achse:"))
        axis_layout.addWidget(self.y_combo)

        self.layout.addWidget(self.regex_input)
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.table_view)
        self.layout.addLayout(axis_layout)
        self.layout.addWidget(self.plot_widget)
        self.setLayout(self.layout)

        # Signals
        self.regex_input.textChanged.connect(self.update_filter)
        self.x_combo.currentIndexChanged.connect(self.update_plot)
        self.y_combo.currentIndexChanged.connect(self.update_plot)

        self.scatter.sigClicked.connect(self.circle_clicked)

        self.update_info_label()
        self.update_plot()

        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn.clicked.connect(self.audio_player.stop)
        self.loop_check.stateChanged.connect(self.toggle_loop)

        self.table_view.clicked.connect(self.table_row_clicked)

    def update_filter(self, pattern):
        filtered = self.data_model.filter_by_regex(pattern)
        self.table_model.update_data(filtered)
        self.update_info_label()
        self.update_plot()

    def update_info_label(self):
        n = len(self.data_model.df_filtered)
        self.info_label.setText(f"{n} Dateien gefunden")

    def update_plot(self):
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()
        df = self.data_model.df_filtered

        if x_col not in df.columns or y_col not in df.columns or df.empty:
            return

        x = df[x_col].values
        y = df[y_col].values

        self.scatter.setData(x, y)

        self.kdtree = cKDTree(np.column_stack([x, y]))

    def table_row_clicked(self, index):
        row = index.row()
        self.select_sample(row)

    def circle_clicked(self, scatter_plot, points):
        pos = points[0].pos()
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()
        _, idx = self.kdtree.query([pos.x(), pos.y()])
        self.select_sample(idx)
        self.table_view.selectRow(idx)

    def select_sample(self, idx):
        self.selected_file = self.data_model.df_filtered.iloc[idx]['stem']
        dir_path = self.data_model.df_filtered.iloc[idx]['dir']
        dir_path = ast.literal_eval(dir_path)
        self.sample_path = os.path.join(
            os.getcwd(), 'Samples', *dir_path, f"{self.selected_file}.wav"
        )
        print(f"Ausgewählt: {self.selected_file}")

    def play_audio(self):
        if not self.selected_file:
            print("Keine Datei ausgewählt!")
            return

        self.audio_player.load_audio(self.sample_path)
        self.audio_player.play()

    def toggle_loop(self, state):
        self.audio_player.set_loop(bool(state))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    csv_path = os.path.join(os.getcwd(), 'ap', 'samples_data.csv')
    window = MainWindow(csv_path)
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())
