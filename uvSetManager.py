import maya.cmds as cmds

from PySide2 import QtCore

from PySide2.QtWidgets import QPushButton,QLineEdit,QWidget,QMainWindow,QGridLayout

class UVSetCreator(QMainWindow):
    def __init__(self):
        super(UVSetCreator,self).__init__()
        self.setWindowTitle("Quick UVSets Manager")
        self.buildUI()

    def buildUI(self):
        centralwidget = QWidget()
        central_layout = QGridLayout(centralwidget)

        #lineEdit
        self.input = QLineEdit()
        central_layout.addWidget(self.input,0,0)

        self.input.setPlaceholderText("Type the name for your UV Sets")

        #create button
        createBtn = QPushButton("Create New Set and Copy UVs from map1")
        central_layout.addWidget(createBtn,0,1)

        #delete button
        deleteBtn = QPushButton("Delete UVSets except map1")
        central_layout.addWidget(deleteBtn,1,0,1,2)

        #transfer button
        transferBtn = QPushButton("Transfer UVs and Delete History")
        central_layout.addWidget(transferBtn,2,0,1,2)

        #connections

        deleteBtn.clicked.connect(self.delete_other_uv_set)
        createBtn.clicked.connect(self.create_new_uv_set)
        transferBtn.clicked.connect(self.transferAttributes)
        #setcentral
        self.setCentralWidget(centralwidget)

    def create_new_uv_set(self):
        """
        This method will create a new UV Set with the given name in input field
        """

        mysel = cmds.ls(sl=True) #selected node
        uv_set_name = self.input.text()
        if not uv_set_name:
            raise ValueError("No Text given to Create an UV Set")
        for mesh in mysel:
            # Create a new UV set
            cmds.polyUVSet(mesh, create=True, uvSet=uv_set_name)
            cmds.polyCopyUV(mesh,uvSetNameInput = 'map1',uvSetName = uv_set_name,ch = 1)
        self.input.clear() #clear the text
    

    def delete_other_uv_set(self):
        """
        This method will Delete all UVSets except 'map1' in the selected meshes
        """

        mysel = cmds.ls(sl=True) #list of selected nodes

        for mesh in mysel:
            uvsets = cmds.polyUVSet(mesh,query=True,auv = True) #get all the UV Sets
            for setItem in uvsets:
                #iterate the uvsets
                cmds.polyUVSet(mesh,cuv = True, uvSet = setItem) #change the current UV Set
                currentUVS = cmds.polyUVSet(mesh,query=True,cuv=True)[0] #store current UV Set name
                if currentUVS!='map1': #if not map1
                    cmds.polyUVSet(mesh,delete=True,cuv = True) #delete the UV Set
                    print('deleted {0}'.format(currentUVS))
                else:
                    print('skipping {0}'.format(currentUVS))
    def transferAttributes(self):
        """
        This method will transfer Attributes for multiple meshes. 
        Select the Mesh that has proper UVs firt. Then select rest of the meshes and Run this function. 
        """ 
        # Get the selected objects.
        selectedObjects = cmds.ls(sl=True) 

        # Get the first object in the selection.
        self.driver = selectedObjects.pop(0)

        # For each object in the selection, transfer the attributes from the driver object.
        for object in selectedObjects:
            cmds.select([self.driver, object])
            cmds.transferAttributes(sampleSpace=4, transferUVs=2, transferColors=2)
            cmds.delete(object, ch=True) #delete history



# Example usage

if __name__=="__main__":
    obj =UVSetCreator()
    obj.show()


