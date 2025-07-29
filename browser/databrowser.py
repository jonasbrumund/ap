import sys
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QPushButton, QWidget,
    QVBoxLayout, QHBoxLayout, QComboBox, QLabel
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QAction
import threading
import os
import ast
import soundfile as sf
import soundcard as sc


class PandasModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._df = df

    def rowCount(self, parent=QModelIndex()):
        return len(self._df)

    def columnCount(self, parent=QModelIndex()):
        return len(self._df.columns) + 1  # +1 für Play-Button

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            if index.column() < len(self._df.columns):
                value = self._df.iloc[index.row(), index.column()]
                return str(value)
            elif index.column() == len(self._df.columns):
                return "Play"

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self._df.columns):
                    return self._df.columns[section]
                elif section == len(self._df.columns):
                    return "Play"
        return None


class MainWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()

        self.setWindowTitle("Sample Browser")

        self.model = PandasModel(df)
        self.view = QTableView()
        self.view.setModel(self.model)

        # Klicks abfangen:
        self.view.clicked.connect(self.handle_click)

        # Beispiel-Filter
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All")
        for tonality in sorted(df['tonality'].unique()):
            self.filter_combo.addItem(tonality)
        self.filter_combo.currentTextChanged.connect(self.apply_filter)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Filter by Tonality:"))
        layout.addWidget(self.filter_combo)
        layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.df = df

    def handle_click(self, index):
        if index.column() == len(self.df.columns):
            # Play-Button Spalte
            stem = self.df.iloc[index.row()]["stem"]
            sample_path = self.df.iloc[index.row()]["dir"]
            sample_path = ast.literal_eval(sample_path)
            sample_path = os.path.join(os.getcwd(), 'Samples', '/'.join(sample_path), f'{stem}.wav')
            print(f"Playing: {sample_path}")
            threading.Thread(target=self.play_sample, args=(sample_path,), daemon=True).start()

    def play_sample(self, file_path):
        """Play audio file using soundfile."""
        default_device = sc.default_speaker()
        try:
            data, samplerate = sf.read(file_path)
            default_device.play(data, samplerate)
        except Exception as e:
            print(f"Error playing {file_path}: {e}")

    def apply_filter(self, tonality):
        if tonality == "All":
            filtered_df = self.df
        else:
            filtered_df = self.df[self.df['tonality'] == tonality]
        self.model = PandasModel(filtered_df)
        self.view.setModel(self.model)


if __name__ == "__main__":
    df = pd.read_csv(os.path.join(os.getcwd(), 'ap', 'samples_data.csv'))

    app = QApplication(sys.argv)
    window = MainWindow(df)
    window.show()
    sys.exit(app.exec())
