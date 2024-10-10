import maya.cmds as cmds
import maya.OpenMayaUI as omui
#from PySide6 import QtCore, QtUiTools, QtWidgets
from PySide2 import QtCore, QtUiTools, QtWidgets
#from shiboken6 import wrapInstance
from shiboken2 import wrapInstance

def getDock(name="UICreatorDock"):
    deleteDock(name)  # Check if exists already and delete accordingly
    cmds.HypershadeWindow() #create a window
    panel = cmds.getPanel(up=True)
    ctrl = cmds.workspaceControl(name, dockToMainWindow = ('right',0), label="Custom UI Label")  # Docks the window in the right at first
    #Ensure that the Hypershade panel is open before running this script, as docking will not work if the target panel is not available.

    qtctrl = omui.MQtUtil.findControl(ctrl)  # Returns the memory address of our new dock
    ptr = wrapInstance(int(qtctrl), QtWidgets.QWidget)  # Convert memory address to a long integer
    return ptr

def deleteDock(name="UICreatorDock"):
    if cmds.workspaceControl(name, query=True, exists=True):
        cmds.deleteUI(name)

class ClassName(QtWidgets.QWidget):  # Change to QWidget instead of QMainWindow

    def __init__(self, parent=None):
        super(ClassName, self).__init__(parent)
        ui_path = "/jobs/tvcResources/bangComms/waranr/Scripts/Git_Repository/QtUI/Shader_Creator.ui"  # Replace with the path to your .ui file
        self.ui = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.setWindowTitle("My UI")
        self.setLayout(layout)

def createArnoldShaderCreator():
    dock = getDock()
    myUI = ClassName(parent=dock)
    dock.layout().addWidget(myUI)

createArnoldShaderCreator()
