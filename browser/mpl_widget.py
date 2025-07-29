from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        

class MplWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.canvas = MplCanvas()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
