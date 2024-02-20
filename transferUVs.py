import maya.cmds as cmds

class TransferWindow(object):
    def __init__(self):
        self.windowName = "TransferUVs"

    def buildUI(self):
        if cmds.window(self.windowName, query = True , exists = True):
            cmds.deleteUI(self.windowName)
        self.transferWindow = cmds.window(self.windowName, widthHeight = (320,85) , s = False)
        cmds.showWindow()

        column = cmds.columnLayout()

        cmds.text("**************************************************************************")
        cmds.text("Step 1: Select the Mesh that you wanna transfer from.")
        cmds.text("Step 2: Select the rest of the meshes with the same poly count")
        cmds.text("Step 3: Hit the Button!")
        cmds.button(label = "Transfer UVs!",command = self.transferAttributes)

        cmds.text("**************************************************************************")


    #First select the mesh that has proper UVs and then add the rest of the meshes to the selection!
    def transferAttributes(self,*args):
        """
        This Script will transfer Attributes for multiple meshes. 
        Select the Mesh that has proper UVs firt. Then select rest of the meshes and Run this function. 
        """ 
        # Get the selected objects.
        self.selectedObjects = cmds.ls(sl=True) 

        # Get the first object in the selection.
        self.driver = self.selectedObjects.pop(0)

        # For each object in the selection, transfer the attributes from the driver object.
        for object in self.selectedObjects:
            cmds.select([self.driver, object])
            cmds.transferAttributes(sampleSpace=4, transferUVs=2, transferColors=2)

# Run the transferAttributes() function.
if __name__ == "__main__":
    window = TransferWindow()
    window.buildUI()