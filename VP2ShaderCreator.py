
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
#from PySide6 import QtCore, QtUiTools, QtWidgets
from PySide2 import QtCore, QtUiTools, QtWidgets,QtGui
#from shiboken6 import wrapInstance
from shiboken2 import wrapInstance
import pprint

def getDock(name="ShaderCreatorDock"):
    """
    This function gets the dock from Maya's interface

    Args:
        name: Name of the Dock for the tool
    Return:
        ptr: the memory address of the dock that is created in Maya's interface
    """
    deleteDock(name)  # Check if exists already and delete accordingly
    cmds.HypershadeWindow() #create a window
    #panel = cmds.getPanel(up=True)
    ctrl = cmds.workspaceControl(name, dockToMainWindow = ('right',0), label="Viewport Shader Creator")  # Docks the window in the right at first
    #Ensure that the Hypershade panel is open before running this script, as docking will not work if the target panel is not available.

    qtctrl = omui.MQtUtil.findControl(ctrl)  # Returns the memory address of our new dock
    ptr = wrapInstance(int(qtctrl), QtWidgets.QWidget)  # Convert memory address to a long integer
    return ptr

def deleteDock(name="ViewportShaderCreatorDock"):
    """
    This function deletes already existing dock

    Args:
        name: Name of the dock to delete
    Return:
        None
    """
    if cmds.workspaceControl(name, query=True, exists=True):
        cmds.deleteUI(name)

# Define suffixes for different texture types

VP2SUFFIX = {
    'VP2' : 'vp2_path'
}

class VP2ShaderCreatorWindow(QtWidgets.QWidget):
        
        def __init__(self, parent=None):
            """
            This is the Constructor function to initialize all the necessary variables ,dict and also connections
            Args:
                None
            Return:
                None
            """
            super(VP2ShaderCreatorWindow, self).__init__(parent)
            ui_path = "/jobs/tvcResources/bangComms/waranr/Scripts/Git_Repository/QtUI/Shader_CreatorWindow.ui"  # Replace with the path to your .ui file
            self.mainWindow = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.addWidget(self.mainWindow)
            self.setWindowTitle("Viewport Shader Creator")
            self.setLayout(self.layout)

            #properties

            #connections
            self.mainWindow.btn_browse.clicked.connect(self.browseFolder) 
            self.mainWindow.input_folderPath.textChanged.connect(self.findPrefixes)

            self.buildUI()
            self.findPrefixes() #default run it
        
        def buildUI(self):
            """
            This function builds additional UI for the Shader Creator Window
            """
            #scroll widget to scroll through lights created
            scrollWidget = QtWidgets.QWidget() #new empty widget
            scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum) #doesnt stretch the scroll area
            self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget) #add vertical layout to it
            self.scrollLayout.setStretch(0,1)

            self.scrollArea = QtWidgets.QScrollArea() #add a scroll area
            self.scrollArea.setWidgetResizable(True) #make it resizable
            self.scrollArea.setWidget(scrollWidget) #add the scrollwidget inside the scroll area
            self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.mainWindow.main_layout.addWidget(self.scrollArea,1,0) #1 = second row, 0 = 1st column, 1=  size of row , 2 = size of columns
            # Set the width of the scroll area to match the content's width
            btn_createAllShaders = QtWidgets.QPushButton("Create All Shaders")
            btn_createAllShaders.setToolTip("Create all the shaders listed above ") 
            btn_createAllShaders.setMinimumHeight(100)
            custom_font = QtGui.QFont()
            custom_font.setBold(True)
            custom_font.setPointSize(15)  # Set to your desired size
            btn_createAllShaders.setFont(custom_font)
            #cbox_autoConvertTextures = QtWidgets.QCheckBox("Auto Convert Textures to TX")
            #cbox_useExistingTextures = QtWidgets.QCheckBox("Use Existing TX Textures")

            self.layout.addWidget(btn_createAllShaders)


            #connections
            btn_createAllShaders.clicked.connect(self.clickAllButtons)
            
        
        def clickAllButtons(self):
            """
            This function creates all the shader for the shader widgets
            """
            shaderWidgets = self.findChildren(VP2ShaderCreator)
            for widget in shaderWidgets:
                widget.createShader()

        def browseFolder(self):
            """
            This function creates a dialog for the user to choose their texture folder
            Args:
                None
            Return:
                None
            """
            #get path from 
            self.path = QtWidgets.QFileDialog.getExistingDirectory(self,"Choose Texture Folder" )
            #paste it in input field
            self.mainWindow.input_folderPath.setText(self.path)
        
        
        def findPrefixes(self):
            """
            This function finds the releavant prefixes and populates the shader widgets accordingly.
            """
            self.clearWidgets() #clear all the widgets
            folder_path = self.mainWindow.input_folderPath.text() #get the text from folder
            if not folder_path:
                prefix = "lambert"
                list = []
                folder_path = ""
                self.populate(prefix,list,folder_path="")
                return

            # Iterate through files in the folder
            prefix_files = {}
            for filename in os.listdir(folder_path):
                parts = filename.split('.')#split the ext
                ext = parts[-1]
                if ext == "exr": #get only exrs
                    # Build full path
                    full_path = os.path.join(folder_path, filename)

                    #find the unique prefixes
                    prefix = filename.split("_base")[0]
                    # Add the file to the corresponding prefix list
                    if prefix not in prefix_files:
                        prefix_files[prefix] = []
                    prefix_files[prefix].append(full_path)
        
            # Populate the scroll area with each prefix and its list
            for prefix, files in prefix_files.items():
                self.populate(prefix, files,folder_path)

            

        def populate(self,prefix,filesList,folder_path):
            """
            This function populates the shaderWidget instances on the scroll area
            """
            widget = VP2ShaderCreator(prefix,filesList,folder_path)
            self.scrollLayout.addWidget(widget)
            self.scrollArea.setFixedWidth(widget.width()) #set the scroll area according to contents
        
        def clearWidgets(self):
            shaderWidgets = self.findChildren(VP2ShaderCreator)
            if shaderWidgets:
                for widget in shaderWidgets:
                    widget.setVisible(False) #hide them
                    widget.deleteShaderWidget() #delete the light
            else:
                pass
            

class VP2ShaderCreator(QtWidgets.QWidget):  # Change to QWidget instead of QMainWindow


    def __init__(self,prefix,filesList,folder_path,parent =None):
        """
        This is the Constructor function to initialize layout variables ,dict and also connections for each prefix found.
        Args:
            None
        Return:
            None
        """
        super(VP2ShaderCreator, self).__init__(parent=parent)
        ui_path = "/jobs/tvcResources/bangComms/waranr/Scripts/Git_Repository/QtUI/VP2_ShaderCreator_v1.ui"  # Replace with the path to your .ui file
        self.myUI = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
        
        #initialize prefix
        self.prefix = prefix
        self.listOfFiles = filesList

        #CONNECTIONS
        self.myUI.btn_createAndAssign.clicked.connect(self.createShaderAndAssign)
        self.myUI.btn_create.clicked.connect(self.createShader)
        
        
        self.myUI.input_shaderName.returnPressed.connect(self.updateShaderName)

        self.myUI.tb_baseColor.clicked.connect(self.setBaseColorPath)


        # Set minimum size based on adjusted size
        self.adjustSize()
        self.setMinimumSize(self.size())

        #initalize dict for toolbuttons
        self.texturePaths = {
            "color" : None,
        }
        self.findTexturesPath(folder_path) #find textures and assign them
        self.myUI.lb_shaderName.setText(self.prefix.split("_primary")[0]+"_VP2") #set the name
        self.myUI.lb_shaderName.setToolTip(self.prefix.split("_primary")[0]+"_VP2") #set the tooltip
        #adjust the size of the label
        self.defaultFont = self.myUI.lb_shaderName.font()
        self.smallfont = QtGui.QFont()
        self.smallfont.setPointSize(10)
        self.smallfont.setBold(1)

        if (len(self.myUI.lb_shaderName.text()))>=27:
            self.myUI.lb_shaderName.setFont(self.smallfont)
        
    def createShader(self,assign = False, mesh = None):
        """
        This function creates a shader and calls the connectTextures() to assign textures to it. If assign and mesh is passed , then it will asign the shader to selected mesh

        Args:
            assign: bool to check if shader needs to be assigned
            mesh: mesh to assign the shader to.
        Return:
            
        """
        #get the name
        shaderName = self.myUI.lb_shaderName.text()
        if shaderName.startswith(tuple("0123456789")):
            cmds.warning("Enter a Valid Name for shader")
            return
        #MAKING THE SHADER
        try:
            self.shader = cmds.shadingNode('lambert', asShader=True, name=shaderName)#create shader
            self.shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName + 'SG') #create Shading Group

            #connect SG and shader
            cmds.connectAttr(self.shader + '.outColor', self.shading_group + '.surfaceShader', force=True)

            #connect textures
            self.connectTextures(self.shader) 
            
            #assign to a mesh
            if assign:
                cmds.select(mesh)
                cmds.hyperShade(assign=self.shading_group)
            else:
                pass
            print("Successfully created "+ shaderName)

        except:
            raise RuntimeError("Couldnt create your shader")

    def createShaderAndAssign(self):
        """
        This Function checks for any selected mesh. If there are any selected mesh, then a shader will be created and assigned

        Args:
            None
        Return:
            None
        """
        selection = cmds.ls(selection=True,tr=True)
        if not selection:
            cmds.warning("No objects selected.")
            return
        else:
            self.createShader(assign=True,mesh=selection)

    def connectTextures(self,shader):
        """
        This function checks the texturePaths dictionary and connects it to the passed shader if there are any paths

        Args:
            shader: shader to be operated on
        Returns:
            None
        """
        for texType,path in self.texturePaths.items():
            if path:
                self.connect_file_texture_to_shader(texType,path,shader) #call the function to connect texture to shader

            if not path:
                print("Skipping "+texType)
                continue
    
    def connect_file_texture_to_shader(self,textureType,texture_path, shader_name):
        """
        This functions creates a texture and connects it to the given shader based on the type of texture

        Args:
            textureType: type of texture
            texture_path: path of texture
            shader_name: name of the shader to be connected with
        Returns:
            None
        """

        # Create a file texture node
        texture_name = texture_path.split("/")[-1].split(".")[0]#get the name of the texture
        file_texture = cmds.shadingNode('file', asTexture=True, name=texture_name+"_FTN")
        
        # Set the file path to the texture node and set it to UDIMS
        cmds.setAttr(file_texture + '.fileTextureName', texture_path, type='string')
        cmds.setAttr(file_texture+".uvTilingMode",3)
        
        # Create a place2dTexture node for UV coordinates
        place2d = cmds.shadingNode('place2dTexture', asUtility=True, name=texture_name+"_PTN")
        
        # Connect the place2dTexture attributes to the file texture node
        cmds.connectAttr(place2d + '.outUV', file_texture + '.uvCoord')
        cmds.connectAttr(place2d + '.outUvFilterSize', file_texture + '.uvFilterSize')
        
        # Connect other necessary attributes
        for attr in ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV',
                    'stagger', 'wrapU', 'wrapV', 'repeatUV', 'offset', 'rotateUV',
                    'noiseUV', 'vertexUvOne', 'vertexUvTwo', 'vertexUvThree',
                    'vertexCameraOne']:
            cmds.connectAttr(place2d + '.' + attr, file_texture + '.' + attr)
        
        # Connect the file texture to the shader's attributes based on type
        if textureType == "color":  
            #connecting DIF nodes        
            cmds.connectAttr(file_texture + '.outColor', shader_name + '.color', force=True)


        
    def findTexturesPath(self,folder_path):
        """
        This function finds the relevant textures path from the given folder path
        """
        # Initialize variables for each texture type
        vp2_path = None

        # Iterate through files in the folder
        for filename in self.listOfFiles:
            # Check each suffix
            for suffix, var_name in VP2SUFFIX.items():
                if suffix in filename:
                    # Extract the number and file extension
                    parts = filename.split('.')
                    try:
                        frame_number = int(parts[-2])
                        ext = parts[-1]
                    except ValueError:
                        continue
                    if ext == "exr": #get only exrs
                        # Build full path
                        full_path = os.path.join(folder_path, filename)
                        # Assign to appropriate variable
                        if var_name == 'vp2_path':
                            if vp2_path is None or frame_number < int(vp2_path.split('.')[-2]):
                                vp2_path = full_path
                        

        #assign the values for our dictionary
        self.texturePaths["color"]= vp2_path


        #set the icons and label
        if vp2_path:
            self.myUI.tb_baseColor.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_baseColor.setText(vp2_path.split("/")[-1])
            #take out strike
            font = self.myUI.lb_baseColor.font()
            font.setStrikeOut(False)
            self.myUI.lb_baseColor.setFont(font)
        if not vp2_path:
            self.myUI.tb_baseColor.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_baseColor.setText("No Texture Found")
            #strike it
            font = self.myUI.lb_baseColor.font()  
            font.setStrikeOut(True)
            self.myUI.lb_baseColor.setFont(font)

    def deleteShaderWidget(self):
        """
        This function deletes the widget
        """
        self.setParent(None) #remove from the layout
        self.setVisible(False) #make it hidden
        self.deleteLater() #delete the UI as soon as it can
        
    def updateShaderName(self):
        """
        This function updates the shader name label based on the given input in the LineEdit Widget
        Args:
            None
        Return:
            None
        """
        #get the name
        inputname = self.myUI.input_shaderName.text()
        name = inputname+"_MAT" #add suffix
        #update the text
        self.myUI.lb_shaderName.setText(name)
        self.myUI.lb_shaderName.setToolTip(name)#set the tooltip
        self.myUI.input_shaderName.clear()

        if (len(self.myUI.lb_shaderName.text()))>=27:
            self.myUI.lb_shaderName.setFont(self.smallfont)
        else:
            self.myUI.lb_shaderName.setFont(self.defaultFont)
    
    def setBaseColorPath(self):
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Base Color Texture" ,dir = self.path)[0]
        except:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Base Color  Texture")[0]
        self.texturePaths["color"]=file
        if file:
            self.myUI.tb_baseColor.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_baseColor.setText(file.split("/")[-1])
            #take out strike
            font = self.myUI.lb_baseColor.font()
            font.setStrikeOut(False)
            self.myUI.lb_baseColor.setFont(font)
        if not file:
            self.myUI.tb_baseColor.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_baseColor.setText("No Texture Selected")
            #strike it
            font = self.myUI.lb_baseColor.font()  
            font.setStrikeOut(True)
            self.myUI.lb_baseColor.setFont(font)

def createVP2ShaderCreatorWindow():
    """
    This function makes an instance of the VP2 Shader Creator Window
    """
    dock = getDock()
    vp2_shader_creatorWin = VP2ShaderCreatorWindow(parent=dock)
    dock.layout().addWidget(vp2_shader_creatorWin)

createVP2ShaderCreatorWindow()