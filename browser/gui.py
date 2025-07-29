import sys
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.spatial import cKDTree
import os
import ast
import soundfile as sf
import soundcard as sc


class ScatterPlotWidget(QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df

        # KD-Tree vorbereiten (initial)
        self.kdtree = None

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.x_combo = QComboBox()
        self.y_combo = QComboBox()

        numeric_cols = self.df.select_dtypes(include=['number']).columns

        self.x_combo.addItems(numeric_cols)
        self.y_combo.addItems(numeric_cols)

        self.info_label = QLabel("Klicke auf einen Punkt")

        self.x_combo.currentTextChanged.connect(self.update_plot)
        self.y_combo.currentTextChanged.connect(self.update_plot)

        # Layout
        layout = QVBoxLayout()
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("X-Achse:"))
        combo_layout.addWidget(self.x_combo)
        combo_layout.addWidget(QLabel("Y-Achse:"))
        combo_layout.addWidget(self.y_combo)

        layout.addLayout(combo_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.info_label)

        self.setLayout(layout)

        # Signals
        self.canvas.mpl_connect('button_press_event', self.on_click)

        self.default_speaker = sc.default_speaker()

        self.update_plot()

    def update_plot(self):
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()

        self.ax.clear()
        self.ax.scatter(
            self.df[x_col], self.df[y_col],
            s=2, rasterized=True
        )
        self.ax.set_xlabel(x_col)
        self.ax.set_ylabel(y_col)

        self.kdtree = cKDTree(self.df[[x_col, y_col]].values)

        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()

        _, idx = self.kdtree.query([event.xdata, event.ydata])

        stem = self.df.iloc[idx]['stem']
        dir_path = self.df.iloc[idx]['dir']
        dir_path = ast.literal_eval(dir_path)
        full_path = os.path.join(
            os.getcwd(), 'Samples', *dir_path, f"{stem}.wav"
        )

        self.info_label.setText(f"Ausgewählt: {stem}")

        # button zum Abspielen

        self.play_sample(full_path)

    def play_sample(self, file_path):
        """Play audio file using soundfile."""
        try:
            data, samplerate = sf.read(file_path)
            with self.default_speaker.player(samplerate=samplerate) as player:
                player.play(data)
        except Exception as e:
            print(f"Fehler beim Abspielen der Datei {file_path}: {e}")


class MainWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle("Sample Library Browser")

        widget = ScatterPlotWidget(df)
        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    use_cols = ['stem', 'dir']  # Basis-Spalten
    csv_path = os.path.join(os.getcwd(), 'ap', 'samples_data.csv')
    df = pd.read_csv(csv_path)

    # if len(df) > 10000:
    #     df = df.sample(n=10000, random_state=42)

    window = MainWindow(df)
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())