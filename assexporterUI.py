"""
Script Name: assExporterUI.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script can export multiple meshes into Ass files in the set Directory
"""
import maya.cmds as cmds
import maya.OpenMaya as om 
 
class ASSEXPORT():
    """
    This is a Gear class that lets us create a gear and modify it , if required.
     
    Methods:
        __init__: Initializes the Gear class.
        buildUI: builds the base window for the exporter 
        exportObjects : runs the exporter function.

    """
    def __init__(self,my_sel):
        self.windowName = "AssExporter"
        self.dir = "No Directory is Selected"
        self.objects = my_sel
        self.message = ""

    def buildUI(self,*args):
        if cmds.window(self.windowName,query=True,exists= True):
            cmds.deleteUI(self.windowName)
        cmds.window(self.windowName,rtf=True,s=False)
        column1 = cmds.columnLayout()
        row1 = cmds.rowLayout(numberOfColumns=2)
        self.dir = cmds.fileDialog2(cap="Select your Export folder",fm=3)
        cmds.text("Selected Directory: ")
        cmds.text(self.dir)
        cmds.setParent(column1)
        row3 = cmds.rowLayout(numberOfColumns=1)
        length = len(self.objects)
        cmds.text("Number of Objects to Export: " + str(length))
        cmds.setParent(column1)
        row2 = cmds.rowLayout(numberOfColumns=2)
        cmds.button(label="Export",command = self.exportObjects,width= 250, height = 50)
        cmds.button(label="Set Directory",command = self.buildUI,width= 250, height = 50)
        cmds.setParent(column1)
        cmds.showWindow()



    def exportObjects(self,*args):
        for obj in self.objects:
            obj_name = obj.replace("_GEO","")
            obj_name = obj_name.split("|")
            obj_name = obj_name[-1]
            file_name = obj_name + ".ass"  # Use the modified object name
            file_path = self.dir[0] +"/"+file_name  # Replace with your directory path
            print(file_path)
            cmds.setAttr('defaultRenderGlobals.currentRenderer', 'arnold', type='string')
            # Export selected object as .ass file with the object's name
            cmds.arnoldExportAss(f=file_path, mask=255+2048,shg=True, s=True)
            om.MGlobal.displayInfo("Exported Files Succesfully")
            self.message = "Exported Files Succesfully!"
        self.messageDisplay()

    
    def messageDisplay(self,*args):
        cmds.text(self.message)


if __name__=="__main__":
    selection = cmds.ls(sl=True)
    if not selection:
        raise ValueError("Nothing is Selected! Please select a mesh")
    obj1 = ASSEXPORT(selection)
    obj1.buildUI()