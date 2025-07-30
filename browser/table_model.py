from PySide6.QtCore import Qt, QAbstractTableModel


class PandasTableModel(QAbstractTableModel):
    def __init__(self, df, columns=None, ignore_columns=None, parent=None):
        super().__init__(parent)
        self.df = df
        if columns:
            self.columns = columns
        else:
            self.columns = df.columns.tolist()

        if ignore_columns:
            self.columns = [
                col for col in self.columns if col not in ignore_columns
            ]

    def rowCount(self, parent=None):
        return len(self.df)

    def columnCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            col_name = self.columns[col]
            return str(self.df.iloc[row][col_name])

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columns[section]
            else:
                return str(section)
        return None

    def update_data(self, new_df):
        self.layoutAboutToBeChanged.emit()
        self.df = new_df.reset_index(drop=True)  # still full
        self.layoutChanged.emit()

    def set_columns(self, columns):
        self.beginResetModel()
        self.columns = columns
        self.df = self.df_all[self.columns]
        self.endResetModel()

    def sort(self, column, order=Qt.AscendingOrder):
        col_name = self.columns[column]
        self.layoutAboutToBeChanged.emit()
        ascending = order == Qt.AscendingOrder
        self.df = self.df.sort_values(col_name, ascending=ascending)
        self.df.reset_index(drop=True, inplace=True)
        self.layoutChanged.emit()
