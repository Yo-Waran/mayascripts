from PySide6 import QtCore, QtUiTools, QtWidgets

class TestApp(QtWidgets.QWidget):
    def __init__(self):
        super(TestApp, self).__init__()
        central_Widget = QtWidgets.QWidget()
        ui_path = "/Users/ramyogeshwaran/Documents/Yogi/GitHub Repo/QtUi/test.ui"  # Replace with the path to your .ui file
        self.ui = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
        self.setWindowTitle("Test App")
        
        #externally set a layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        #initialize
        self.percent = self.ui.lb_percent
        value = str(self.ui.sld_slider.value()) + " %"
        self.percent.setText(value)

        self.ui.button.setText("Click Me!")
        
        #connections
        self.ui.sld_slider.valueChanged.connect(self.updateUI)

    def updateUI(self):
        value = str(self.ui.sld_slider.value()) + " %"
        self.percent.setText(value)
        




if __name__ == "__main__":
    win = TestApp()
    win.show()

