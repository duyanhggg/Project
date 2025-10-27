from PyQt5 import QtWidgets, QtGui
import sys

class AutoSorterGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('AutoSorter')
        self.setGeometry(100, 100, 400, 300)

        self.layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel('Welcome to AutoSorter!')
        self.label.setFont(QtGui.QFont('Arial', 16))
        self.layout.addWidget(self.label)

        self.start_button = QtWidgets.QPushButton('Start Sorting')
        self.start_button.clicked.connect(self.start_sorting)
        self.layout.addWidget(self.start_button)

        self.stop_button = QtWidgets.QPushButton('Stop Sorting')
        self.stop_button.clicked.connect(self.stop_sorting)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)

    def start_sorting(self):
        # Logic to start sorting files
        self.label.setText('Sorting started...')

    def stop_sorting(self):
        # Logic to stop sorting files
        self.label.setText('Sorting stopped.')

def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = AutoSorterGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()