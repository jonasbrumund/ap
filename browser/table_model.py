from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class PandasTableModel(QAbstractTableModel):
    def __init__(self, df, columns=None):
        super().__init__()
        self.df_all = df
        # self._df = df.copy()
        self.columns = columns if columns else list(df.columns)
        self.df = self.df_all[self.columns]

    def rowCount(self, parent=QModelIndex()):
        return len(self.df)

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            value = self.df.iloc[index.row(), index.column()]

            # round float values to 2 decimal places
            # !!! DOES NOT WORK?!
            if isinstance(value, float):
                return f"{value:.2f}"
            return str(value)

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columns[section]
            if orientation == Qt.Vertical:
                return str(self.df.index[section])
        return None

    def update_data(self, new_df):
        self.beginResetModel()
        self.df_all = new_df
        self.df = self.df_all[self.columns]
        self.endResetModel()

    def set_columns(self, columns):
        self.beginResetModel()
        self.columns = columns
        self.df = self.df_all[self.columns]
        self.endResetModel()

    def sort(self, column, order=Qt.AscendingOrder):
        col_name = self.columns[column]
        ascending = order == Qt.AscendingOrder

        self.layoutAboutToBeChanged.emit()
        self.df = self.df.sort_values(col_name, ascending=ascending)
        self.df = self.df.reset_index(drop=True)
        self.layoutChanged.emit()

    # def get_df_index(self, row):
    #     """Returns the original index in df_filtered for a given table row."""
    #     return self._df.index[row]
