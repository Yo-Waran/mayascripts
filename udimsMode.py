"""
Script Name: gearCreator.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script generates a procedural Gear in Maya.
"""

import maya.cmds as cmds

class UDIMS(object):
    def __init__(self):
        self.windowName = "ToUDIMS"
    
    def buildUI(self):
        if cmds.window(self.windowName,query=True,exists= True):
            cmds.deleteUI(self.windowName)
        cmds.window(self.windowName,widthHeight = (180,30),s=False)
        column1 = cmds.columnLayout()
        row = cmds.rowLayout(numberOfColumns=2)
        cmds.text("Tiling Mode : ")
        cmds.button(label="Convert to UDIMS",command = self.convert)
        cmds.setParent(column1)
        cmds.showWindow()

    
    def convert(self,selection = False,*args):

        selection = cmds.ls(sl=True)
        if not selection:
            raise ValueError("Nothing is selected. Please select a textures")
        
        for node in selection:
            if cmds.objectType(node) != "file" and cmds.objectType(node) != "place2dTexture":
                raise ValueError("One of the selection is not a file Node. Aborting.")
            
        for texture in selection:
            if cmds.objectType(texture)=="place2dTexture":
                print("skipping Placer Node")
                continue
            else:
                cmds.setAttr(texture+".uvTilingMode",3)

if __name__=="__main__":
    t1 = UDIMS()
    t1.buildUI()


"""
MIT License

Copyright (c) 2024 Ram Yogeshwaran

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


