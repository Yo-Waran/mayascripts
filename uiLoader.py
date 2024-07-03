from PySide2 import QtCore, QtUiTools, QtWidgets

class TestApp(QtWidgets.QWidget):
    def __init__(self):
        super(TestApp, self).__init__()
        central_Widget = QWidget()
        ui_path = "/jobs/tvcResources/bangComms/waranr/Scripts/Git_Repository/QtUI/polyOperate.ui"  # Replace with the path to your .ui file
        self.ui = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
        self.setWindowTitle("Test App")
        
        #externally set a layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)



if __name__ == "__main__":
    win = TestApp()
    win.show()
