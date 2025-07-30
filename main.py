import sys
import os
import numpy as np
import ast

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableView, QLabel, QComboBox,
    QPushButton, QCheckBox, QListWidget, QFileDialog
)
from PySide6.QtCore import Qt
import pyqtgraph as pg

from browser.audioplayer import AudioPlayer
from browser.data_model import SampleDataModel
from browser.table_model import PandasTableModel


class MainWindow(QWidget):
    """
    Main application window for the Sample Browser.
    Displays audio sample metadata, scatter plot, similarity search,
    and playback controls.
    """

    def __init__(self, csv_path):
        """
        Initialize the main window and all UI elements.
        If the CSV file or Samples folder is not found, prompt the user.
        """
        super().__init__()
        self.setWindowTitle("Sample Browser")

        # === Load Data ===
        try:
            self.data_model = SampleDataModel(csv_path)
        except FileNotFoundError:
            print("Samples data CSV not found, please select manually.")
            csv_path = self.select_csv_file()
            if not csv_path:
                print("No file selected. Exiting.")
                sys.exit(1)
            self.data_model = SampleDataModel(csv_path)

        # === Check Samples folder ===
        self.folderpath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'Samples'
        )
        if not os.path.exists(self.folderpath):
            self.folderpath = self.select_samples_folder()
            if not self.folderpath:
                print("No folder selected, exiting.")
                sys.exit(1)

        # === Initialize audio player ===
        self.audio_player = AudioPlayer()
        self.selected_file = None
        self.sample_path = None

        self.last_sorted_column = -1
        self.last_sort_order = Qt.AscendingOrder

        # === Initialize main table model ===
        self.table_model = PandasTableModel(
            self.data_model.df_filtered,
            columns=['stem', 'duration', 'channels',
                     'tonality', 'tempo', 'bit_depth']
        )

        # === Feature list for similarity ===
        numeric_cols = self.get_numeric_columns()
        self.feature_list = QListWidget()
        self.feature_list.setSelectionMode(QListWidget.MultiSelection)
        self.feature_list.addItems(numeric_cols)

        # === Layout ===
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_player_controls()
        self.init_regex_filter_controls()
        self.init_table_view()
        self.init_feature_selection(numeric_cols)
        self.init_scatter_plot()
        self.init_similarity_output(numeric_cols)
        self.init_signals()

        # === Initial updates ===
        self.update_info_label()
        self.update_plot()

    def get_numeric_columns(self):
        """
        Return numeric columns excluding unwanted ones.
        """
        numeric_cols = self.data_model.df_filtered.select_dtypes(
            include=[np.number]
        ).columns.tolist()
        return [col for col in numeric_cols if col not in ['idx', 'distance']]

    def select_csv_file(self):
        """
        Prompt user to select CSV file.
        """
        options = QFileDialog.Options()
        if sys.platform == "darwin":
            options |= QFileDialog.DontUseNativeDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Samples Data CSV", "",
            "CSV Files (*.csv)", options=options
        )
        return path

    def select_samples_folder(self):
        """
        Prompt user to select the Samples folder.
        """
        options = QFileDialog.Options()
        if sys.platform == "darwin":
            options |= QFileDialog.DontUseNativeDialog
        return QFileDialog.getExistingDirectory(
            self, "Select Samples Folder", options=options
        )

    def init_player_controls(self):
        """
        Initialize audio player buttons and loop checkbox.
        """
        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")
        self.loop_check = QCheckBox("Loop")

        player_layout = QHBoxLayout()
        player_layout.addWidget(self.play_btn)
        player_layout.addWidget(self.stop_btn)
        player_layout.addWidget(self.loop_check)
        self.layout.addLayout(player_layout)

    def init_regex_filter_controls(self):
        """
        Initialize search box, info label, random sample button,
        and show-all checkbox.
        """
        regex_layout = QHBoxLayout()
        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Search stems...")
        regex_layout.addWidget(self.regex_input)

        self.info_label = QLabel("Files found:")
        regex_layout.addWidget(self.info_label)

        self.random_button = QPushButton("Select Random Sample")
        regex_layout.addWidget(self.random_button)

        self.show_all_cols_checkbox = QCheckBox("Show all Features")
        regex_layout.addWidget(self.show_all_cols_checkbox)

        self.layout.addLayout(regex_layout)

    def init_table_view(self):
        """
        Initialize table view for displaying metadata.
        """
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSortingEnabled(True)
        self.layout.addWidget(self.table_view)

        header = self.table_view.horizontalHeader()
        header.resizeSection(0, 150)  # stem
        header.resizeSection(1, 150)  # duration

    def init_feature_selection(self, numeric_cols):
        """
        Initialize scatter plot axis selectors and color feature selector.
        """
        axis_layout = QHBoxLayout()

        # X Axis
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Axis:"))
        self.x_combo = QComboBox()
        x_layout.addWidget(self.x_combo)
        x_layout.addStretch()

        # Y Axis
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y Axis:"))
        self.y_combo = QComboBox()
        y_layout.addWidget(self.y_combo)
        y_layout.addStretch()

        xy_layout = QVBoxLayout()
        xy_layout.addLayout(x_layout)
        xy_layout.addLayout(y_layout)
        axis_layout.addLayout(xy_layout)

        # Color feature
        color_layout = QVBoxLayout()
        color_layout.addWidget(QLabel(
            "Optional: select a third feature for color gradient.\n"
            "Orange = high, Blue = low, White = no value."
        ))
        color_select_layout = QHBoxLayout()
        self.color_combo = QComboBox()
        color_select_layout.addWidget(self.color_combo)

        self.color_feature_checkbox = QCheckBox("Show in scatter plot")
        self.color_feature_checkbox.setChecked(True)
        color_select_layout.addWidget(self.color_feature_checkbox)

        color_layout.addLayout(color_select_layout)
        axis_layout.addLayout(color_layout)

        self.layout.addLayout(axis_layout)

        # Populate combos
        scatter_cols = numeric_cols
        self.x_combo.addItems(scatter_cols)
        self.y_combo.addItems(scatter_cols)
        self.color_combo.addItems(scatter_cols)

        # Set defaults if possible
        try:
            idx = scatter_cols.index('spectral_centroid')
            self.x_combo.setCurrentIndex(idx)
            index = scatter_cols.index('temporal_centroid')
            self.color_combo.setCurrentIndex(index)
        except ValueError:
            print("'spectral_centroid' or 'temporal_centroid' not found!")

    def init_scatter_plot(self):
        """
        Initialize scatter plot widget and its layers.
        """
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        self.scatter = pg.ScatterPlotItem(size=8, pen=None)
        self.plot_widget.addItem(self.scatter)

        self.highlight = pg.ScatterPlotItem(
            size=15, pen=pg.mkPen('r', width=2)
        )
        self.plot_widget.addItem(self.highlight)

    def init_similarity_output(self, numeric_cols):
        """
        Initialize similarity search UI: features, method, sorted results.
        """
        similarity_output_layout = QHBoxLayout()

        # Left controls
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel(
            "Select features and method for similarity search:"
        ))

        self.calc_dist_btn = QPushButton("Similarity Search")
        left_layout.addWidget(self.calc_dist_btn)

        select_method_layout = QHBoxLayout()
        self.master_checkbox = QCheckBox("Select all features")
        self.similarity_combo = QComboBox()
        self.similarity_combo.addItems(["Euclidean", "Cosine"])
        select_method_layout.addWidget(self.master_checkbox)
        select_method_layout.addWidget(self.similarity_combo)
        left_layout.addLayout(select_method_layout)

        self.feature_list = QListWidget()
        self.feature_list.setSelectionMode(QListWidget.MultiSelection)
        self.feature_list.addItems(numeric_cols)
        left_layout.addWidget(self.feature_list)

        # Right output
        right_layout = QVBoxLayout()
        self.show_color_checkbox = QCheckBox(
            "Show similarity color gradient (red = less similar)"
        )
        right_layout.addWidget(self.show_color_checkbox)

        self.sorted_table_model = PandasTableModel(
            self.data_model.df_filtered, columns=['stem', 'distance']
        )
        self.sorted_table_view = QTableView()
        self.sorted_table_view.setModel(self.sorted_table_model)
        self.sorted_table_view.setSortingEnabled(True)
        header = self.sorted_table_view.horizontalHeader()
        header.resizeSection(0, 200)
        header.resizeSection(1, 200)
        right_layout.addWidget(self.sorted_table_view)

        right_layout.addWidget(QLabel(
            "Info: Smaller distance = more similar sample"
        ))

        similarity_output_layout.addLayout(left_layout)
        similarity_output_layout.addLayout(right_layout)
        self.layout.addLayout(similarity_output_layout)

    def init_signals(self):
        """
        Connect signals to their respective slots.
        """
        self.regex_input.textChanged.connect(self.update_filter)
        self.show_all_cols_checkbox.stateChanged.connect(
            self.toggle_all_columns
        )
        self.random_button.clicked.connect(self.select_random_sample)

        self.x_combo.currentIndexChanged.connect(self.update_plot)
        self.y_combo.currentIndexChanged.connect(self.update_plot)
        self.color_combo.currentIndexChanged.connect(self.update_plot)
        self.color_feature_checkbox.stateChanged.connect(self.update_plot)
        self.show_color_checkbox.stateChanged.connect(self.update_plot)

        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn.clicked.connect(self.audio_player.stop)
        self.loop_check.stateChanged.connect(self.toggle_loop)

        self.table_view.clicked.connect(self.table_row_clicked)
        self.table_view.horizontalHeader().sectionClicked.connect(
            self.handle_header_clicked
        )

        self.scatter.sigClicked.connect(self.scatter_point_clicked)

        self.calc_dist_btn.clicked.connect(self.compute_similarity)
        self.master_checkbox.stateChanged.connect(self.toggle_all_features)
        self.sorted_table_view.horizontalHeader().sectionClicked.connect(
            self.handle_sorted_header_clicked
        )
        self.sorted_table_view.clicked.connect(self.sorted_table_row_clicked)

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

    def select_random_sample(self):
        """
        Select a random sample from the filtered DataFrame.
        """
        if self.data_model.df_filtered.empty:
            print("No samples available!")
            return

        # Select a random row index
        random_index = np.random.choice(self.data_model.df_filtered.index)
        row_pos = self.data_model.df_filtered.index.get_loc(random_index)

        # Select the sample by row position
        self.select_sample_by_row(row_pos)

        # Highlight in table and scatter plot
        self.table_view.selectRow(row_pos)
        for s in self.scatter.points():
            if s.data() == random_index:
                self.highlight.setData([{'pos': s.pos()}])
                break

        # Select in sorted table
        self.select_in_sorted_table(self.selected_file)

        # Highlight the selected point in the scatter plot
        self.highlight.setData([{'pos': self.scatter.points()[row_pos].pos()}])

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
    # get csv path (same directory as this script)
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'samples_data.csv'
    )
    window = MainWindow(csv_path)
    window.resize(800, 1100)
    window.show()
    sys.exit(app.exec())
