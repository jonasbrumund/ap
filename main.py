import sys
import os
import ast
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableView, QLabel, QComboBox,
    QPushButton, QCheckBox, QListWidget
)
from PySide6.QtCore import Qt
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
        self.last_sorted_column = -1
        self.last_sort_order = Qt.AscendingOrder

        # Table model only shows selected columns
        self.table_model = PandasTableModel(
            self.data_model.df_filtered,
            columns=[
                'stem', 'duration', 'channels',
                'tonality', 'tempo', 'bit_depth'
            ]
        )

        # Initialize distance computation
        self.feature_list = QListWidget()
        self.feature_list.setSelectionMode(QListWidget.MultiSelection)

        # only use columns with numeric data for distance computation
        numeric_cols = self.data_model.df_filtered.select_dtypes(
            include=[np.number]
        ).columns
        remove_cols = [
            'idx', 'distance'
        ]  # columns to remove from the list
        numeric_cols = [
            col for col in numeric_cols if col not in remove_cols
        ]
        self.feature_list.addItems(numeric_cols)

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

        # === Info Label + Checkbox in eine Zeile ===
        info_layout = QHBoxLayout()

        self.info_label = QLabel("Files found:")
        info_layout.addWidget(self.info_label)

        self.show_all_cols_checkbox = QCheckBox("Show all Features")
        info_layout.addWidget(self.show_all_cols_checkbox)

        info_layout.addStretch()

        self.layout.addLayout(info_layout)

        # Table view
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSortingEnabled(True)
        self.layout.addWidget(self.table_view)
        header = self.table_view.horizontalHeader()
        header.resizeSection(0, 150)  # 'stem'
        header.resizeSection(1, 150)  # 'distance'

        # === Feature selection ===
        axis_layout = QHBoxLayout()

        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Axis:"))
        self.x_combo = QComboBox()
        x_layout.addWidget(self.x_combo)
        x_layout.addStretch()
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y Axis:"))
        self.y_combo = QComboBox()
        y_layout.addWidget(self.y_combo)
        y_layout.addStretch()
        xy_layout = QVBoxLayout()
        xy_layout.addLayout(x_layout)
        xy_layout.addLayout(y_layout)
        axis_layout.addLayout(xy_layout)

        # Color Feature + Checkbox
        color_layout = QVBoxLayout()
        color_layout.addWidget(QLabel(
            "Select third Feature and click the checkbox to show "
            "color gradient in the scatter plot. \nOrange = high "
            "Feature value, Blue = low Feature value, White = no value"
        ))
        color_layout_select = QHBoxLayout()
        self.color_combo = QComboBox()
        color_layout_select.addWidget(self.color_combo)

        self.color_feature_checkbox = QCheckBox("Show in scatter plot")
        self.color_feature_checkbox.setChecked(True)
        color_layout_select.addWidget(self.color_feature_checkbox)

        color_layout.addLayout(color_layout_select)
        axis_layout.addLayout(color_layout)

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
        # use all numeric columns for scatter plot axes except idx
        self.scatter_cols = self.data_model.df_filtered.select_dtypes(
            include=[np.number]
        ).columns.tolist()
        # Remove 'idx' and 'distance' from the list
        self.scatter_cols = [
            col for col in self.scatter_cols
            if col not in ['idx', 'distance']
        ]
        self.x_combo.addItems(self.scatter_cols)
        self.y_combo.addItems(self.scatter_cols)
        self.color_combo.addItems(self.scatter_cols)

        # Set default axes
        try:
            idx = self.scatter_cols.index('spectral_centroid')
            self.x_combo.setCurrentIndex(idx)
            color_feature = self.scatter_cols.index('temporal_centroid')
            self.color_combo.setCurrentIndex(color_feature)
        except ValueError:
            print("'spectral_centroid' not found!")

        # --- Similarity + Output  ---
        similarity_output_layout = QHBoxLayout()

        # === left area ===
        left_layout = QVBoxLayout()

        # Similarity Button
        left_layout.addWidget(QLabel(
            "Select features and method below for similarity search"
        ))
        self.calc_dist_btn = QPushButton("Similarity Search")
        left_layout.addWidget(self.calc_dist_btn)

        # Checkbox + Dropdown
        select_method_layout = QHBoxLayout()
        self.master_checkbox = QCheckBox("select all features")
        self.similarity_combo = QComboBox()
        self.similarity_combo.addItems(["Euclidean", "Cosine"])
        select_method_layout.addWidget(self.master_checkbox)
        select_method_layout.addWidget(self.similarity_combo)
        left_layout.addLayout(select_method_layout)

        # Features list
        self.feature_list = QListWidget()
        self.feature_list.setSelectionMode(QListWidget.MultiSelection)
        self.feature_list.addItems(numeric_cols)
        left_layout.addWidget(self.feature_list)

        # === right area ===
        right_layout = QVBoxLayout()

        self.show_color_checkbox = QCheckBox(
            "show color gradient based on similarity (red = less similar)"
        )
        right_layout.addWidget(self.show_color_checkbox)

        self.sorted_table_view = QTableView()
        self.sorted_table_model = PandasTableModel(
            self.data_model.df_filtered,
            columns=['stem', 'distance']
        )
        self.sorted_table_view.setModel(self.sorted_table_model)
        self.sorted_table_view.setSortingEnabled(True)
        header_sorted = self.sorted_table_view.horizontalHeader()
        header_sorted.resizeSection(0, 200)  # 'stem'
        header_sorted.resizeSection(1, 200)  # 'distance'

        right_layout.addWidget(self.sorted_table_view)
        right_layout.addWidget(QLabel(
            "Info: small distance value = similar sample "
            "based on selected features"
        ))

        # Combine
        similarity_output_layout.addLayout(left_layout)
        similarity_output_layout.addLayout(right_layout)

        self.layout.addLayout(similarity_output_layout)

        # --- Signals ---
        self.regex_input.textChanged.connect(self.update_filter)
        self.show_all_cols_checkbox.stateChanged.connect(
            self.toggle_all_columns
        )
        self.x_combo.currentIndexChanged.connect(self.update_plot)
        self.y_combo.currentIndexChanged.connect(self.update_plot)
        self.color_feature_checkbox.stateChanged.connect(self.update_plot)
        self.color_combo.currentIndexChanged.connect(self.update_plot)
        self.show_color_checkbox.stateChanged.connect(
            self.toggle_distance_checkbox
        )
        self.color_feature_checkbox.stateChanged.connect(
            self.toggle_feature_checkbox
        )

        self.scatter.sigClicked.connect(self.scatter_point_clicked)

        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn.clicked.connect(self.audio_player.stop)
        self.loop_check.stateChanged.connect(self.toggle_loop)

        self.table_view.clicked.connect(self.table_row_clicked)

        self.header = self.table_view.horizontalHeader()
        self.header.sectionClicked.connect(self.handle_header_clicked)

        self.calc_dist_btn.clicked.connect(self.compute_similarity)
        self.master_checkbox.stateChanged.connect(self.toggle_all_features)
        self.sorted_table_view.horizontalHeader().sectionClicked.connect(
            self.handle_sorted_header_clicked
        )
        self.sorted_table_view.clicked.connect(self.sorted_table_row_clicked)
        self.show_color_checkbox.stateChanged.connect(self.update_plot)

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
        self.update_sorted_table()

    def update_info_label(self):
        """
        Update info label with the number of matching files.
        """
        n = len(self.data_model.df_filtered)
        self.info_label.setText(f"{n} files found")

    def toggle_all_columns(self, state):
        """
        Schaltet zwischen allen Columns und den Standard-Spalten um.
        """
        if self.show_all_cols_checkbox.isChecked():
            # all cols except 'idx', 'dir', 'distance'
            all_cols = [
                col for col in self.data_model.df_filtered.columns
                if col not in ['idx', 'dir', 'distance']
            ]
        else:
            # only standard columns for better overview
            all_cols = ['stem', 'duration', 'channels',
                        'tonality', 'tempo', 'bit_depth']

        self.table_model.columns = all_cols
        self.table_model.layoutChanged.emit()
        self.last_sorted_column = -1

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

        # --- Color Coding ---
        use_distance_color = (
            self.show_color_checkbox.isChecked() and
            'distance' in df.columns and df['distance'].notnull().any()
        )

        use_feature_color = (
            self.color_feature_checkbox.isChecked() and
            self.color_combo.currentText() in df.columns and
            df[self.color_combo.currentText()].notnull().any()
        )

        # ensure only one color gradient is active
        if use_distance_color and use_feature_color:
            print(
                "Warning: Both distance and feature color are selected."
                "Using distance color only."
            )
            use_feature_color = False

        if use_distance_color:
            distances = df['distance'].values
            min_dist = np.nanmin(distances)
            max_dist = np.nanmax(distances)
            norm = (distances - min_dist) / (max_dist - min_dist + 1e-9)
            colors = []
            for val in norm:
                val = val ** 0.6  # smoother gradient for visibility
                # Blue (0,0,255) → Red (255,0,0)
                r = int(val * 255)
                g = 0
                b = int((1 - val) * 255)
                colors.append(pg.mkBrush(r, g, b, 200))
        elif use_feature_color:
            feat_col = self.color_combo.currentText()
            values = df[feat_col].values
            # check for NaN values
            valid = ~np.isnan(values)
            if np.any(valid):
                min_val = np.nanmin(values)
                max_val = np.nanmax(values)
                norm = np.full_like(values, 0.5)  # Default mid-gray
                norm[valid] = (
                    (values[valid] - min_val) / (max_val - min_val + 1e-9)
                )
                norm = np.clip(norm, 0, 1)
            else:
                norm = np.zeros_like(values)
            colors = []
            for val, valid_val in zip(norm, valid):
                if not valid_val:
                    colors.append(pg.mkBrush(255, 255, 255, 200))
                else:
                    val = val ** 0.6
                    r = int(val * 255)
                    g = int(val * 165)
                    b = int((1 - val) * 255)
                    colors.append(pg.mkBrush(r, g, b, 200))
        else:
            colors = [pg.mkBrush(0, 0, 255, 120)] * len(df)

        # Store index mapping for click lookup
        spots = []
        for idx, (px, py, col) in enumerate(zip(x, y, colors)):
            original_idx = df.index[idx]
            spots.append({
                'pos': (px, py),
                'data': original_idx,  # row index in df_filtered
                'brush': col
            })

        self.scatter.setData(spots)

        # Clear highlight
        self.highlight.setData([])

    def update_sorted_table(self):
        """
        Shows the sorted output list with only 'stem' and 'distance'.
        """
        df = self.table_model.df.copy()

        # only cols 'stem' & 'distance'
        if 'distance' not in df.columns:
            df['distance'] = np.nan  # Initialize

        df = df[['stem', 'distance']]
        self.sorted_table_model.update_data(df)

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

        # Update table selection
        self.table_view.selectRow(row_pos)

        # Select in sorted table
        self.select_in_sorted_table(self.selected_file)

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

        # Highlight the corresponding point in the scatter plot
        for s in self.scatter.points():
            if s.data() == original_idx:
                self.highlight.setData([{'pos': s.pos()}])
                break

        self.select_in_sorted_table(self.selected_file)

    def sorted_table_row_clicked(self, index):
        """
        Handle click on sorted output list
        """
        view_row = index.row()
        if view_row >= len(self.sorted_table_model.df):
            return

        stem = self.sorted_table_model.df.iloc[view_row]['stem']

        # Find original index
        df = self.table_model.df
        matches = df[df['stem'] == stem]
        if matches.empty:
            print("Kein passender Eintrag in Haupttabelle!")
            return

        original_idx = matches.index[0]
        row_pos = df.index.get_loc(original_idx)

        self.select_sample_by_row(row_pos)

        # Select row in table view
        self.table_view.selectRow(row_pos)

        # Highlight scatter point
        for s in self.scatter.points():
            if s.data() == original_idx:
                self.highlight.setData([{'pos': s.pos()}])
                break

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

    def select_in_sorted_table(self, stem):
        """
        Wählt in der Output-Liste den passenden Eintrag.
        """
        matches = self.sorted_table_model.df[
            self.sorted_table_model.df['stem'] == stem
        ]
        if not matches.empty:
            row = matches.index[0]
            self.sorted_table_view.selectRow(row)

    def handle_header_clicked(self, section):
        if section == self.last_sorted_column:
            # Toggle order
            new_order = (
                Qt.DescendingOrder
                if self.last_sort_order == Qt.AscendingOrder
                else Qt.AscendingOrder
            )
        else:
            # Default to ascending if different column
            new_order = Qt.AscendingOrder

        self.table_model.sort(section, new_order)
        self.last_sorted_column = section
        self.last_sort_order = new_order

    def handle_sorted_header_clicked(self, section):
        order = (
            Qt.DescendingOrder
            if self.last_sort_order == Qt.AscendingOrder
            else Qt.AscendingOrder
        )
        self.sorted_table_model.sort(section, order)
        self.last_sort_order = order

    def compute_similarity(self):
        """
        Compute similarity based on selected features and method.
        """
        if not self.selected_file:
            print("No reference sample selected!")
            return
        selected_items = self.feature_list.selectedItems()
        selected_features = [item.text() for item in selected_items]
        selected_features = [item.text() for item in selected_items]

        if not selected_features:
            print("No feature selected!")
            return

        method = self.similarity_combo.currentText()

        if method == "Euclidean":
            df_sorted = self.data_model.compute_distances(
                self.selected_file, selected_features
            )
        else:
            df_sorted = self.data_model.compute_cosine_distances(
                self.selected_file, selected_features
            )

        # Update MainTable & Plot
        self.table_model.update_data(df_sorted)
        self.data_model.df_filtered = df_sorted
        self.update_plot()

        # Update Output list ['stem', 'distance']
        df_out = df_sorted[['stem', 'distance']].copy()
        self.sorted_table_model.update_data(df_out)

    def toggle_all_features(self, state):
        """
        Toggle selection of all features in the feature list.
        """
        checked = bool(state)
        for i in range(self.feature_list.count()):
            self.feature_list.item(i).setSelected(checked)

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

    def toggle_distance_checkbox(self, state):
        if state:
            self.color_feature_checkbox.setChecked(False)

    def toggle_feature_checkbox(self, state):
        if state:
            self.show_color_checkbox.setChecked(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    csv_path = os.path.join(os.getcwd(), 'ap', 'samples_data.csv')
    window = MainWindow(csv_path)
    window.resize(800, 1100)
    window.show()
    sys.exit(app.exec())
