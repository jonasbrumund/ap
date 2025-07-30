import sys
import os
import ast
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableView, QLabel, QComboBox,
    QPushButton, QCheckBox
)
from PySide6.QtCore import Qt
from scipy.spatial import cKDTree
import pyqtgraph as pg
from browser.audioplayer import AudioPlayer
from browser.data_model import SampleDataModel
from browser.table_model import PandasTableModel


class MainWindow(QWidget):
    """
    Main application window for the sample browser.
    Shows audio sample metadata, scatter plot, and playback controls.
    """

    def __init__(self, csv_path):
        super().__init__()
        self.setWindowTitle("Sample Browser")

        # Data & audio
        self.data_model = SampleDataModel(csv_path)
        self.audio_player = AudioPlayer()
        self.selected_file = None
        self.sample_path = None
        self.kdtree = None
        self.last_sorted_column = -1
        self.last_sort_order = Qt.AscendingOrder

        # Table model shows selected columns
        self.table_model = PandasTableModel(
            self.data_model.df_filtered,
            columns=['stem', 'duration', 'channels',
                     'tonality', 'tempo', 'bit_depth']
        )

        # Proxy model for sorting and filtering
        # self.proxy_model = QSortFilterProxyModel()
        # self.proxy_model.setSourceModel(self.table_model)

        # --- Widgets ---
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Audio player controls
        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")
        self.loop_check = QCheckBox("Loop")
        player_layout = QHBoxLayout()
        player_layout.addWidget(self.play_btn)
        player_layout.addWidget(self.stop_btn)
        player_layout.addWidget(self.loop_check)
        self.layout.addLayout(player_layout)

        # Regex input for filtering
        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Search stems...")
        self.layout.addWidget(self.regex_input)

        self.info_label = QLabel("Files found:")
        self.layout.addWidget(self.info_label)

        # Table view
        self.table_view = QTableView()
        # self.table_view.setModel(self.proxy_model) # SEHR LANGSAM!!
        self.table_view.setModel(self.table_model)
        self.table_view.setSortingEnabled(True)
        self.layout.addWidget(self.table_view)

        # Axis selection
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(QLabel("X Axis:"))
        self.x_combo = QComboBox()
        axis_layout.addWidget(self.x_combo)

        axis_layout.addWidget(QLabel("Y Axis:"))
        self.y_combo = QComboBox()
        axis_layout.addWidget(self.y_combo)

        self.layout.addLayout(axis_layout)

        # Scatter plot widget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        # Scatter plot items
        self.scatter = pg.ScatterPlotItem(size=8, pen=None)
        self.plot_widget.addItem(self.scatter)

        self.highlight = pg.ScatterPlotItem(
            size=15, pen=pg.mkPen('r', width=2), brush=None
        )
        self.plot_widget.addItem(self.highlight)

        # --- Scatter plot axes ---
        self.scatter_cols = [
            'duration', 'tempo', 'brightness',
            'loudness', 'spectral_centroid',
            'hardness', 'depth', 'roughness',
            'warmth', 'sharpness'
        ]
        self.x_combo.addItems(self.scatter_cols)
        self.y_combo.addItems(self.scatter_cols)

        # --- Signals ---
        self.regex_input.textChanged.connect(self.update_filter)
        self.x_combo.currentIndexChanged.connect(self.update_plot)
        self.y_combo.currentIndexChanged.connect(self.update_plot)

        self.scatter.sigClicked.connect(self.scatter_point_clicked)

        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn.clicked.connect(self.audio_player.stop)
        self.loop_check.stateChanged.connect(self.toggle_loop)

        self.table_view.clicked.connect(self.table_row_clicked)

        self.header = self.table_view.horizontalHeader()
        self.header.sectionClicked.connect(self.handle_header_clicked)

        # --- Init plot ---
        self.update_info_label()
        self.update_plot()

    def update_filter(self, pattern):
        """
        Filter samples based on regex input.
        """
        filtered = self.data_model.filter_by_regex(pattern)
        self.table_model.update_data(filtered)
        self.update_info_label()
        self.update_plot()

    def update_info_label(self):
        """
        Update info label with the number of matching files.
        """
        n = len(self.data_model.df_filtered)
        self.info_label.setText(f"{n} files found")

    def update_plot(self):
        """
        Update scatter plot based on axis selection and filtered data.
        """
        df = self.table_model.df
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()

        # Clear previous data
        if x_col not in df.columns or y_col not in df.columns or df.empty:
            self.scatter.setData([])
            return

        x = df[x_col].values
        y = df[y_col].values

        # Store index mapping for click lookup
        spots = []
        for idx, (px, py) in enumerate(zip(x, y)):
            original_idx = df.index[idx]
            spots.append({
                'pos': (px, py),
                'data': original_idx,  # row index in df_filtered
                'brush': pg.mkBrush(0, 0, 255, 120)
            })

        self.scatter.setData(spots)

        # Clear highlight
        self.highlight.setData([])

        # Rebuild KDTree for manual fallback (if you need it)
        self.kdtree = cKDTree(np.column_stack([x, y]))

    def scatter_point_clicked(self, plot, points, index):
        """
        Handle clicks on scatter plot points.
        """
        if not points:
            return

        point = points[0]
        original_idx = point.data()

        # Find the row position in current df
        try:
            row_pos = self.table_model.df.index.get_loc(original_idx)
        except KeyError:
            print("Index not in current table model!")
            return

        self.select_sample_by_row(row_pos)

        # Highlight selected point
        self.highlight.setData([{'pos': point.pos()}])

    def table_row_clicked(self, index):
        """
        Handle table row click and highlight in scatter plot.
        """
        # Get the row in the sorted DataFrame
        view_row = index.row()
        if view_row >= len(self.table_model.df):
            print("Row index out of bounds")
            return

        self.select_sample_by_row(view_row)

        # Get the original index
        original_idx = self.table_model.df.index[view_row]

        # # Use the row data
        # row = self.table_model.df.iloc[view_row]

        # # Use this for your audio file path logic
        # self.select_sample(original_idx)

        # Highlight the corresponding point in the scatter plot
        for s in self.scatter.points():
            if s.data() == original_idx:
                self.highlight.setData([{'pos': s.pos()}])
                break

        # # Get selected point pos for highlight
        # df = self.data_model.df_filtered
        # x_col = self.x_combo.currentText()
        # y_col = self.y_combo.currentText()

        # if x_col in df.columns and y_col in df.columns:
        #     px = row[x_col]
        #     py = row[y_col]
        #     self.highlight.setData([{'pos': (px, py)}])

    def select_sample(self, idx):
        """
        Store selected sample info and build full file path.
        """
        row = self.data_model.df_filtered.iloc[idx]
        self.selected_file = row['stem']
        dir_path = ast.literal_eval(row['dir'])
        self.sample_path = os.path.join(
            os.getcwd(), 'Samples', *dir_path, f"{self.selected_file}.wav"
        )

        # Update selected file in table by stem name
        # self.table_view.selectRow(idx)
        print(f"Selected: {self.selected_file}")
        print(idx)

    def select_sample_by_row(self, row_pos):
        """
        Store selected sample info by row position.
        """
        # Always positional!
        row = self.table_model.df.iloc[row_pos]

        self.selected_file = row['stem']
        dir_path = ast.literal_eval(row['dir'])
        self.sample_path = os.path.join(
            os.getcwd(), 'Samples', *dir_path, f"{self.selected_file}.wav"
        )

        print(f"Selected: {self.selected_file}")
        print(f"Row pos: {row_pos}")

    def handle_header_clicked(self, section):
        if section == self.last_sorted_column:
            # Toggle order
            new_order = Qt.DescendingOrder if self.last_sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            # Default to ascending if different column
            new_order = Qt.AscendingOrder

        self.table_model.sort(section, new_order)
        self.last_sorted_column = section
        self.last_sort_order = new_order

    def play_audio(self):
        """
        Play selected audio sample.
        """
        if not self.selected_file:
            print("No file selected!")
            return

        self.audio_player.load_audio(self.sample_path)
        self.audio_player.play()

    def toggle_loop(self, state):
        """
        Toggle loop playback on/off.
        """
        self.audio_player.set_loop(bool(state))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    csv_path = os.path.join(os.getcwd(), 'ap', 'samples_data.csv')
    window = MainWindow(csv_path)
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())
