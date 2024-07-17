import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide6 import QtCore, QtUiTools, QtWidgets
from shiboken6 import wrapInstance

def getDock(name="ShaderCreatorDock"):
    deleteDock(name)  # Check if exists already and delete accordingly
    cmds.HypershadeWindow() #create a window
    panel = cmds.getPanel(up=True)
    ctrl = cmds.workspaceControl(name, dockToMainWindow = ('right',0), label="Arnold Shader Creator")  # Docks the window in the right at first
    #Ensure that the Hypershade panel is open before running this script, as docking will not work if the target panel is not available.

    qtctrl = omui.MQtUtil.findControl(ctrl)  # Returns the memory address of our new dock
    ptr = wrapInstance(int(qtctrl), QtWidgets.QWidget)  # Convert memory address to a long integer
    return ptr

def deleteDock(name="ShaderCreatorDock"):
    if cmds.workspaceControl(name, query=True, exists=True):
        cmds.deleteUI(name)

class ArnoldShaderCreator(QtWidgets.QWidget):  # Change to QWidget instead of QMainWindow

    def __init__(self, parent=None):
        super(ArnoldShaderCreator, self).__init__(parent)
        ui_path = "/Users/ramyogeshwaran/Documents/Yogi/GitHub Repo/QtUi/Shader_Creator.ui"  # Replace with the path to your .ui file
        self.ui = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.setWindowTitle("Arnold Shader Creator")
        self.setLayout(layout)

def createArnoldShaderCreator():
    dock = getDock()
    arnold_shader_creator = ArnoldShaderCreator(parent=dock)
    dock.layout().addWidget(arnold_shader_creator)

createArnoldShaderCreator()

