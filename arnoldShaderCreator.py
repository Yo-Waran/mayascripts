import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide6 import QtCore, QtUiTools, QtWidgets
#from PySide2 import QtCore, QtUiTools, QtWidgets
from shiboken6 import wrapInstance
#from shiboken2 import wrapInstance

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
    panel = cmds.getPanel(up=True)
    ctrl = cmds.workspaceControl(name, dockToMainWindow = ('right',0), label="Arnold Shader Creator")  # Docks the window in the right at first
    #Ensure that the Hypershade panel is open before running this script, as docking will not work if the target panel is not available.

    qtctrl = omui.MQtUtil.findControl(ctrl)  # Returns the memory address of our new dock
    ptr = wrapInstance(int(qtctrl), QtWidgets.QWidget)  # Convert memory address to a long integer
    return ptr

def deleteDock(name="ShaderCreatorDock"):
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
SUFFIXES = {
    '_DIF': 'base_color_path',
    '_RGH': 'roughness_path',
    '_NRM': 'normal_path',
    '_DSP': 'displacement_path',
    '_MTL': 'metalness_path'
}
class ArnoldShaderCreatorWindow(QtWidgets.QWidget):
        
        def __init__(self, parent=None):
            """
            This is the Constructor function to initialize all the necessary variables ,dict and also connections
            Args:
                None
            Return:
                None
            """
            super(ArnoldShaderCreatorWindow, self).__init__(parent)
            ui_path = "/Users/ramyogeshwaran/Documents/Yogi/GitHub Repo/QtUi/Shader_CreatorWindow.ui"  # Replace with the path to your .ui file
            self.mainWindow = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
            layout = QtWidgets.QVBoxLayout(self)
            layout.addWidget(self.mainWindow)
            self.setWindowTitle("Arnold Shader Creator")
            self.setLayout(layout)

            #properties
            #self.mainWindow.scroll_widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum) #doesnt stretch the scroll area
            #self.mainWindow.scroll_area.setWidgetResizable(True) #make it resizable
            #self.mainWindow.scroll_area.setWidget(self.mainWindow.scroll_widget) #add the scrollwidget inside the scroll area
            #connections
            self.mainWindow.btn_browse.clicked.connect(self.browseFolder) 
            self.mainWindow.input_folderPath.textChanged.connect(self.findPrefixes)

            self.buildUI()
        
        def buildUI(self):
            #scroll widget to scroll through lights created
            scrollWidget = QtWidgets.QWidget() #new empty widget
            scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum) #doesnt stretch the scroll area
            self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget) #add vertical layout to it
            self.scrollLayout.setStretch(0,1)

            scrollArea = QtWidgets.QScrollArea() #add a scroll area
            scrollArea.setWidgetResizable(True) #make it resizable
            scrollArea.setWidget(scrollWidget) #add the scrollwidget inside the scroll area
            self.mainWindow.main_layout.addWidget(scrollArea) #1 = second row, 0 = 1st column, 1=  size of row , 2 = size of columns
        
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

            #folder_path = self.mainWindow.input_folderPath.text() #get the text from folder

            test1 = []
            self.populate("hello",test1)
            # Iterate through files in the folder
            #for filename in os.listdir(folder_path):
                #pass
                #find the unique prefixes

                #populate the scroll area

        def populate(self,prefix,filesList):
            widget = ArnoldShaderCreator(prefix,filesList)
            self.scrollLayout.addWidget(widget)
            




class ArnoldShaderCreator(QtWidgets.QWidget):  # Change to QWidget instead of QMainWindow


    def __init__(self,prefix,filesList,parent =None):
        """
        This is the Constructor function to initialize layout variables ,dict and also connections for each prefix found.
        Args:
            None
        Return:
            None
        """
        super(ArnoldShaderCreator, self).__init__(parent=parent)
        ui_path = "/Users/ramyogeshwaran/Documents/Yogi/GitHub Repo/QtUi/shaderCreator_v2.ui"  # Replace with the path to your .ui file
        self.myUI = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
        
        #initialize prefix
        self.prefix = prefix
        self.listOfFiles = filesList

        #CONNECTIONS
        self.myUI.btn_createAndAssign.clicked.connect(self.createShaderAndAssign)
        self.myUI.btn_create.clicked.connect(self.createShader)
        
        
        self.myUI.input_shaderName.returnPressed.connect(self.updateShaderName)

        self.myUI.tb_baseColor.clicked.connect(self.setBaseColorPath)
        self.myUI.tb_roughness.clicked.connect(self.setRoughPath)
        self.myUI.tb_metalness.clicked.connect(self.setMetalPath)
        self.myUI.tb_normal.clicked.connect(self.setNormalPath)
        self.myUI.tb_displacement.clicked.connect(self.setDispPath)


        # Set minimum size based on adjusted size
        self.adjustSize()
        self.setMinimumSize(self.size())
        #initalize dict for toolbuttons
        self.texturePaths = {
            "baseColor" : None,
            "specularRoughness" :None,
            "metalness" : None,
            "normalCamera" : None,
            "displacementShader" : None,
        }

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
            self.shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=shaderName)#create shader
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
        file_texture = cmds.shadingNode('file', asTexture=True, name='fileTextureNode')
        
        # Set the file path to the texture node and set it to UDIMS
        cmds.setAttr(file_texture + '.fileTextureName', texture_path, type='string')
        cmds.setAttr(file_texture+".uvTilingMode",3)
        
        # Create a place2dTexture node for UV coordinates
        place2d = cmds.shadingNode('place2dTexture', asUtility=True, name='place2dTextureNode')
        
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
        if textureType == "displacementShader":
            #connecting DSP nodes 
            # Create a displacement node
            disp_shader = cmds.shadingNode('displacementShader', asUtility=True)
            # Connect the file texture to the disp_shader node
            cmds.connectAttr(file_texture + '.outAlpha', disp_shader + '.displacement')
            #Connec the disp_shader to shader
            cmds.connectAttr(disp_shader + '.displacement', self.shading_group + '.displacementShader', force=True)

        elif textureType == "baseColor":  
            #connecting DIF nodes        
            # Create a color correct node
            color_correct = cmds.shadingNode('aiColorCorrect', asUtility=True, name='correctDIF')
            # Connect the file texture to the color correct node
            cmds.connectAttr(file_texture + '.outColor', color_correct + '.input')
            # Connect the color correct node to the shader
            cmds.connectAttr(color_correct + '.outColor', shader_name + '.baseColor', force=True)

        elif textureType == "specularRoughness":
            #connecting RGH nodes   
            # Create an aiRange node
            ai_range = cmds.shadingNode('aiRange', asUtility=True, name='rangeRGH')
            # Connect the file texture to the aiRange node
            cmds.connectAttr(file_texture + '.outColor', ai_range + '.input')
            #Connec the aiRange to shader
            cmds.connectAttr(ai_range + '.outColor.outColorR', shader_name + '.'+textureType, force=True)
            cmds.setAttr(file_texture+".alphaIsLuminance",1) #set the alpha is luminance
        
        elif textureType == "metalness":  
            #connecting MTL nodes      
            # Create an aiRange node
            ai_range = cmds.shadingNode('aiRange', asUtility=True, name='rangeMTL')
            # Connect the file texture to the aiRange node
            cmds.connectAttr(file_texture + '.outColor', ai_range + '.input')
            #Connec the aiRange to shader  
            cmds.connectAttr(ai_range + '.outColor.outColorR', shader_name + '.'+textureType, force=True)
            cmds.setAttr(file_texture+".alphaIsLuminance",1)#set the alpha is luminance

        elif textureType == "normalCamera":  
            #connecting NRM nodes        
            # Create an aiNormal node
            ai_normal = cmds.shadingNode('aiNormalMap', asUtility=True)
            # Connect the file texture to the aiRange node
            cmds.connectAttr(file_texture + '.outColor', ai_normal + '.input')
            #Connec the aiRange to shader  
            cmds.connectAttr(ai_normal + '.outValue', shader_name + '.'+textureType, force=True)


        
    def findTexturesPath(self):
        # Initialize variables for each texture type
        base_color_path = None
        roughness_path = None
        normal_path = None
        displacement_path = None
        metalness_path = None

        
        # Iterate through files in the folder
        for filename in self.listOfFiles:
            # Check each suffix
            for suffix, var_name in SUFFIXES.items():
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
                        if var_name == 'base_color_path':
                            if base_color_path is None or frame_number < int(base_color_path.split('.')[-2]):
                                base_color_path = full_path
                        elif var_name == 'roughness_path':
                            if roughness_path is None or frame_number < int(roughness_path.split('.')[-2]):
                                roughness_path = full_path
                        elif var_name == 'normal_path':
                            if normal_path is None or frame_number < int(normal_path.split('.')[-2]):
                                normal_path = full_path
                        elif var_name == 'displacement_path':
                            if displacement_path is None or frame_number < int(displacement_path.split('.')[-2]):
                                displacement_path = full_path
                        elif var_name == 'metalness_path':
                            if metalness_path is None or frame_number < int(metalness_path.split('.')[-2]):
                                metalness_path = full_path  

        #assign the values for our dictionary
        self.texturePaths["baseColor"]=base_color_path
        self.texturePaths["specularRoughness"]=roughness_path
        self.texturePaths["metalness"]=metalness_path
        self.texturePaths["normalCamera"]=normal_path
        self.texturePaths["displacementShader"]=displacement_path

        #set the icons and label
        if base_color_path:
            self.myUI.tb_baseColor.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_baseColor.setText(base_color_path.split("/")[-1])
            #take out strike
            font = self.myUI.lb_baseColor.font()
            font.setStrikeOut(False)
            self.myUI.lb_baseColor.setFont(font)
        if not base_color_path:
            self.myUI.tb_baseColor.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_baseColor.setText("No Texture Found")
            #strike it
            font = self.myUI.lb_baseColor.font()  
            font.setStrikeOut(True)
            self.myUI.lb_baseColor.setFont(font)

        if roughness_path:
            self.myUI.tb_roughness.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_roughness.setText(roughness_path.split("/")[-1])
            #take out strike
            font = self.myUI.lb_roughness.font()
            font.setStrikeOut(False)
            self.myUI.lb_roughness.setFont(font)
        if not roughness_path:
            self.myUI.tb_roughness.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_roughness.setText("No Texture Found")
            #strike it
            font = self.myUI.lb_roughness.font()
            font.setStrikeOut(True)
            self.myUI.lb_roughness.setFont(font)

        if metalness_path:
            self.myUI.tb_metalness.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_metalness.setText(metalness_path.split("/")[-1])
            #take out strike
            font = self.myUI.lb_metalness.font()
            font.setStrikeOut(False)
            self.myUI.lb_metalness.setFont(font)
        if not metalness_path:
            self.myUI.tb_metalness.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_metalness.setText("No Texture Found")
            #strike it
            font = self.myUI.lb_metalness.font()
            font.setStrikeOut(True)
            self.myUI.lb_metalness.setFont(font)


        if normal_path:
            self.myUI.tb_normal.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_normal.setText(normal_path.split("/")[-1])
            #take out strike
            font = self.myUI.lb_normal.font()
            font.setStrikeOut(False)
            self.myUI.lb_normal.setFont(font)
        if not normal_path:
            self.myUI.tb_normal.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_normal.setText("No Texture Found")
            #strike it
            font = self.myUI.lb_normal.font()
            font.setStrikeOut(True)
            self.myUI.lb_normal.setFont(font)
            
        if displacement_path:
            self.myUI.tb_displacement.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_displacement.setText(displacement_path.split("/")[-1])
            #take out strike
            font = self.myUI.lb_displacement.font()
            font.setStrikeOut(False)
            self.myUI.lb_displacement.setFont(font)
        if not displacement_path:
            self.myUI.tb_displacement.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_displacement.setText("No Texture Found")
            #strike it
            font = self.myUI.lb_displacement.font()
            font.setStrikeOut(True)
            self.myUI.lb_displacement.setFont(font)
    



        
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
        self.myUI.input_shaderName.clear()
    
    def setBaseColorPath(self):
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Base Color Texture" ,dir = self.path)[0]
        except:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Base Color  Texture")[0]
        self.texturePaths["baseColor"]=file
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


    def setRoughPath(self):
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Roughness Texture" ,dir = self.path)[0]
        except:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Roughness Texture")[0]
        self.texturePaths["specularRoughness"]=file
        if file:
            self.myUI.tb_roughness.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_roughness.setText(file.split("/")[-1])
            #take out strike
            font = self.myUI.lb_roughness.font()
            font.setStrikeOut(False)
            self.myUI.lb_roughness.setFont(font)
        if not file:
            self.myUI.tb_roughness.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_roughness.setText("No Texture Selected")
            #strike it
            font = self.myUI.lb_roughness.font()
            font.setStrikeOut(True)
            self.myUI.lb_roughness.setFont(font)

        
    def setMetalPath(self):
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Metalness Texture" ,dir = self.path)[0]
        except:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Metalness Texture")[0]
        self.texturePaths["metalness"]=file
        if file:
            self.myUI.tb_metalness.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_metalness.setText(file.split("/")[-1])
            #take out strike
            font = self.myUI.lb_metalness.font()
            font.setStrikeOut(False)
            self.myUI.lb_metalness.setFont(font)
        if not file:
            self.myUI.tb_metalness.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_metalness.setText("No Texture Selected")
            #strike it
            font = self.myUI.lb_metalness.font()
            font.setStrikeOut(True)
            self.myUI.lb_metalness.setFont(font)


    def setNormalPath(self):
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Normal Texture" ,dir = self.path)[0]
        except:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Normal Texture")[0]
        self.texturePaths["normalCamera"]=file
        if file:
            self.myUI.tb_normal.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_normal.setText(file.split("/")[-1])
            #take out strike
            font = self.myUI.lb_normal.font()
            font.setStrikeOut(False)
            self.myUI.lb_normal.setFont(font)
        if not file:
            self.myUI.tb_normal.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_normal.setText("No Texture Selected")
            #strike it
            font = self.myUI.lb_normal.font()
            font.setStrikeOut(True)
            self.myUI.lb_normal.setFont(font)
   

    def setDispPath(self):
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Displacement Texture" ,dir = self.path)[0]
        except:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Displacement Texture")[0]
        self.texturePaths["displacementShader"]=file
        if file:
            self.myUI.tb_displacement.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.lb_path_displacement.setText(file.split("/")[-1])
            #take out strike
            font = self.myUI.lb_displacement.font()
            font.setStrikeOut(False)
            self.myUI.lb_displacement.setFont(font)
        if not file:
            self.myUI.tb_displacement.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.lb_path_displacement.setText("No Texture Selected")
            #strike it
            font = self.myUI.lb_displacement.font()
            font.setStrikeOut(True)
            self.myUI.lb_displacement.setFont(font)

def createArnoldShaderCreatorWindow():
    dock = getDock()
    arnold_shader_creatorWin = ArnoldShaderCreatorWindow(parent=dock)
    dock.layout().addWidget(arnold_shader_creatorWin)

createArnoldShaderCreatorWindow()
