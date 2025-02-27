"""
Script Name: shaderCreatorMaya.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script is used to create Arnold/VP2 shaders in Maya
"""
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui

from PySide2 import QtCore, QtUiTools, QtWidgets,QtGui

from shiboken2 import wrapInstance

def getDock(name="ShaderCreatorDock"):
    """
    This function gets the dock from Maya's interface

    Args:
        name: Name of the Dock for the tool
    Returns:
        ptr: the memory address of the dock that is created in Maya's interface
    """
    deleteDock(name)  # Check if exists already and delete accordingly
    cmds.HypershadeWindow() #create a window
    #panel = cmds.getPanel(up=True)
    ctrl = cmds.workspaceControl(name, dockToMainWindow = ('right',0), label="Maya Shader Creator")  # Docks the window in the right at first
    #Ensure that the Hypershade panel is open before running this script, as docking will not work if the target panel is not available.

    qtctrl = omui.MQtUtil.findControl(ctrl)  # Returns the memory address of our new dock
    ptr = wrapInstance(int(qtctrl), QtWidgets.QWidget)  # Convert memory address to a long integer
    return ptr

def deleteDock(name="ShaderCreatorDock"):
    """
    This function deletes already existing dock

    Args:
        name: Name of the dock to delete
    Returns:
        None
    """
    if cmds.workspaceControl(name, query=True, exists=True):
        cmds.deleteUI(name)

#Define Global Suffixes for various texture types
SUFFIXES = {
    '_DIF': 'base_color_path',
    '_RGH': 'roughness_path',
    '_NRM': 'normal_path',
    '_DSP': 'displacement_path',
    '_MTL': 'metalness_path'
}

VP2SUFFIX = {
    'VP2' : 'vp2_path'
}

class ShaderCreatorMayaWindow(QtWidgets.QWidget):
        """
        This is a ShaderCreatorMayaWindow class that lets us create the UI for this tool 
        
        Methods:
            __init__: Initializes the ShaderCreatorMayaWindow class and connections to certain widget
            buildUI: builds additional UI for the Shader Creator Window
            clickAllButtons: This function creates all the shader for the shader widgets
            browseFolder: This function creates a dialog for the user to choose their texture folder
            findPrefixes: This function finds the releavant prefixes and populates the shader widgets accordingly.
            populate: This function populates the Arnold shaderWidget instances on the scroll area
            populateVP2: This function populates the VP2 shaderWidget instances on the scroll area
            clearWidgets: This Function clears all the shader widgets in the scroll area

        """
        
        def __init__(self, parent=None):
            """
            This is the Constructor function to initialize all the necessary variables ,dict and also connections
            
            Args:
                None
            Returns:
                None
            """
            super(ShaderCreatorMayaWindow, self).__init__(parent)
            ui_path = "/jobs/tvcResources/bangComms/waranr/Scripts/Git_Repository/QtUI/masterUIShaderCreator.ui"  # Replace with the path to your .ui file
            self.mainWindow = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.addWidget(self.mainWindow)
            self.setWindowTitle("Maya Shader Creator")
            self.setLayout(self.layout)

            #properties
            self.mainWindow.VP2Widget.setVisible(False)
            self.mainWindow.VP2Widget.destroy(True)
            self.mainWindow.standardSurfaceWidget.setVisible(False)
            self.mainWindow.standardSurfaceWidget.destroy(True)

            #connections
            self.mainWindow.btn_browse.clicked.connect(self.browseFolder)
            self.mainWindow.input_folderPath.textChanged.connect(self.findPrefixes)

            
            # Set size policies for main window
            self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
            self.adjustSize()

            #run initial functions
            self.buildUI()
            self.findPrefixes() #default run it
            
        
        def buildUI(self):
            """
            This function builds additional UI for the Shader Creator Window
            
            Args:
                None
            Returns:
                None
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
            # Set the width of the scroll area to match the content's width
            btn_createAllShaders = QtWidgets.QPushButton("Create  All Shaders")
            btn_createAllShaders.setToolTip("Create all the shaders listed above ") 
            btn_createAllShaders.setMinimumHeight(70)
            custom_font = QtGui.QFont()
            custom_font.setBold(True)
            custom_font.setPointSize(15)  # Set to your desired size
            btn_createAllShaders.setFont(custom_font)

            #bold font
            bold_font = QtGui.QFont()
            bold_font.setBold(True)

            #checkboxes
            cbox_layout = QtWidgets.QHBoxLayout()
            cbox_autoConvertTextures = QtWidgets.QCheckBox("Auto Convert Textures to TX")
            cbox_useExistingTextures = QtWidgets.QCheckBox("Use Existing TX Textures")
            cbox_layout.addWidget(cbox_autoConvertTextures)
            cbox_layout.addWidget(cbox_useExistingTextures)

            #progress bar
            self.progressBar = QtWidgets.QProgressBar()
            self.progressBar.setFont(bold_font)
            self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
            self.progressBar.setStyleSheet("QProgressBar {border: 0px;} QProgressBar::chunk {background-color: rgb(0, 150, 200);};")
            
            #add to layouts
            self.mainWindow.main_layout.addLayout(cbox_layout,1,0)
            self.mainWindow.main_layout.addWidget(self.scrollArea,2,0) #1 = second row, 0 = 1st column, 1=  size of row , 2 = size of columns
            self.layout.addWidget(btn_createAllShaders)
            self.layout.addWidget(self.progressBar)

            #connections
            btn_createAllShaders.clicked.connect(self.clickAllButtons)
            cbox_autoConvertTextures.toggled.connect(lambda val : cmds.setAttr("defaultArnoldRenderOptions.autotx",val)) 
            cbox_useExistingTextures.toggled.connect(lambda val : cmds.setAttr("defaultArnoldRenderOptions.use_existing_tiled_textures",val))
            
            #progressbar value
            self.progressBar.setValue(0)
    
        def clickAllButtons(self):
            """
            This function creates all the shader for the shader widgets
            
            Args:
                None
            Returns:
                None
            """
            arnoldshaderWidgets = self.findChildren(ArnoldShaderCreator)
            vp2shaderWidgets = self.findChildren(VP2ShaderCreator)


            i = 0 #counter variable for keeping track of iterations
            if vp2shaderWidgets:
                total_steps = len(arnoldshaderWidgets + vp2shaderWidgets)
                for widget in arnoldshaderWidgets:
                    widget.createShader()
                    
                    #update progress bar
                    i=i+1 #add the step counter
                    progress_value = int((float(i) / total_steps) * 50)
                    self.progressBar.setValue(progress_value)#set the value

                for widget in vp2shaderWidgets:
                    widget.createShader()

                    #update progress bar
                    i=i+1 #add the step counter
                    progress_value = int((float(i) / total_steps) * 100)
                    self.progressBar.setValue(progress_value)#set the value
            else:
                total_steps = len(arnoldshaderWidgets)
                i = 0
                for widget in arnoldshaderWidgets:
                    widget.createShader()
                    
                    #update progress bar
                    i=i+1 #add the step counter
                    progress_value = int((float(i) / total_steps) * 100)
                    self.progressBar.setValue(progress_value)#set the value

        def browseFolder(self):
            """
            This function creates a dialog for the user to choose their texture folder
            
            Args:
                None
            Returns:
                None
            """
            #get path from 
            self.path = QtWidgets.QFileDialog.getExistingDirectory(self,"Choose Texture Folder" )
            #paste it in input field
            self.mainWindow.input_folderPath.setText(self.path)
        
        
        def findPrefixes(self):
            """
            This function finds the releavant prefixes and populates the shader widgets accordingly.
            Args:
                None
            Returns:
                None
            """
            self.clearWidgets() #clear all the widgets
            folder_path = self.mainWindow.input_folderPath.text() #get the text from folder
            if not folder_path:
                prefix = "aiStandardSurface"
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
                for filename in files:
                    # Check each suffix
                    for suffix, var_name in SUFFIXES.items():
                        if suffix in filename:
                            isArnold = True
                    for suffix,var_name in VP2SUFFIX.items():
                        if suffix in filename:
                            isArnold = False
                            
                if isArnold == True:
                    self.populate(prefix, files,folder_path)
                if not isArnold:
                    self.populateVP2(prefix, files,folder_path)

            #reset the progress val
            self.progressBar.setValue(0)     

        def populate(self,prefix,filesList,folder_path):
            """
            This function populates the Arnold shaderWidget instances on the scroll area
            
            Args:
                prefix: prefix to be set for the shaderNames and nodes
                filesList: list of files containing the same prefix
                folder_path: folderPath where the function iterates upon
            Returns:
                None
            """
            widget = ArnoldShaderCreator(prefix,filesList,folder_path)
            self.scrollLayout.addWidget(widget)
            self.scrollArea.setFixedWidth(widget.width()) #set the scroll area according to contents


        def populateVP2(self,prefix,filesList,folder_path):
            """
            This function populates the VP2 shaderWidget instances on the scroll area
            
            Args:
                prefix: prefix to be set for the shaderNames and nodes
                filesList: list of files containing the same prefix
                folder_path: folderPath where the function iterates upon
            Returns:
                None
            """
            widget = VP2ShaderCreator(prefix,filesList,folder_path)
            self.scrollLayout.addWidget(widget)
            self.scrollArea.setFixedWidth(widget.width()) #set the scroll area according to contents
        
        def clearWidgets(self):
            """
            This Function clears all the shader widgets in the scroll area
            
            Args:
                None
            Returns:
                None
            """
            vp2shaderWidgets = self.findChildren(VP2ShaderCreator)
            if vp2shaderWidgets:
                for widget in vp2shaderWidgets:
                    widget.setVisible(False) #hide them
                    widget.deleteShaderWidget() #delete the light
            else:
                pass
          
            arnoldshaderWidgets = self.findChildren(ArnoldShaderCreator)
            if arnoldshaderWidgets:
                for widget in arnoldshaderWidgets:
                    widget.setVisible(False) #hide them
                    widget.deleteShaderWidget() #delete the light
            else:
                pass
            
class ArnoldShaderCreator(QtWidgets.QWidget):  # Change to QWidget instead of QMainWindow
    """
    This is a ArnoldShaderCreator class that lets us create the Arnold shaderWidget in the scroll area
    
    Methods:
        __init__: This is the Constructor function to initialize layout variables ,dict and also connections for each prefix found.
        createShader: This function creates a shader and calls the connectTextures() to assign textures to it. If assign and mesh is passed , then it will asign the shader to selected mesh
        createShaderAndAssign: This Function checks for any selected mesh. If there are any selected mesh, then a shader will be created and assigned
        connectTextures: This function checks the texturePaths dictionary and connects it to the passed shader if there are any paths
        connect_file_texture_to_shader: This functions creates a texture and connects it to the given shader based on the type of texture
        findTexturesPath: This function finds the relevant textures path from the given folder path
        deleteShaderWidget: This function deletes the widget from the parent UI
        updateShaderName: This function updates the shader name label based on the given input in the LineEdit Widget
        setBaseColorPath: This function makes a dialog for the User to pick the Base Color Texture path 
        setRoughPath: This function makes a dialog for the User to pick the Roughness Texture path 
        setMetalPath: This function makes a dialog for the User to pick the Metalness Texture path 
        setNormalPath: This function makes a dialog for the User to pick the Normal Texture path 
        setDispPath: This function makes a dialog for the User to pick the Displacement Texture path 

    """

    def __init__(self,prefix,filesList,folder_path,parent =None):
        """
        This is the Constructor function to initialize layout variables ,dict and also connections for each prefix found.
        
        Args:
            prefix: prefix to be set for the shaderNames and nodes
            filesList: list of files containing the same prefix
            folder_path: folderPath where the function iterates upon
        Returns:
            None
        """
        super(ArnoldShaderCreator, self).__init__(parent=parent)
        ui_path = "/jobs/tvcResources/bangComms/waranr/Scripts/Git_Repository/QtUI/masterUIShaderCreator.ui"  # Replace with the path to your .ui file
        self.myUI = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)

        self.myUI.standardSurfaceWidget.setVisible(True)
        
        #hide mainlayouts
        self.myUI.VP2Widget.setVisible(False)
        self.myUI.VP2Widget.deleteLater()
        self.myUI.btn_browse.setVisible(False)
        self.myUI.btn_browse.deleteLater()
        self.myUI.input_folderPath.setVisible(False)
        self.myUI.input_folderPath.deleteLater()
        self.myUI.label.setVisible(False)
        self.myUI.label.deleteLater()
        
        
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
        self.setMinimumSize(self.myUI.standardSurfaceWidget.sizeHint())


        #initalize dict for toolbuttons
        self.texturePaths = {
            "baseColor" : None,
            "specularRoughness" :None,
            "metalness" : None,
            "normalCamera" : None,
            "displacementShader" : None,
        }
        self.findTexturesPath(folder_path) #find textures and assign them
        self.myUI.lb_shaderName.setText(self.prefix.split("_primary")[0]+"_MAT") #set the name
        self.myUI.lb_shaderName.setToolTip(self.prefix.split("_primary")[0]+"_MAT") #set the tooltip
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
        Returns:
            None
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
        Returns:
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
        if textureType == "displacementShader":
            #connecting DSP nodes 
            # Create a displacement node
            disp_shader = cmds.shadingNode('displacementShader', asUtility=True,name = texture_name+"_DSN")
            # Connect the file texture to the disp_shader node
            cmds.connectAttr(file_texture + '.outAlpha', disp_shader + '.displacement')
            #Connec the disp_shader to shader
            cmds.connectAttr(disp_shader + '.displacement', self.shading_group + '.displacementShader', force=True)

        elif textureType == "baseColor":  
            #connecting DIF nodes        
            # Create a color correct node
            color_correct = cmds.shadingNode('aiColorCorrect', asUtility=True, name=texture_name+"_AIC")
            # Connect the file texture to the color correct node
            cmds.connectAttr(file_texture + '.outColor', color_correct + '.input')
            # Connect the color correct node to the shader
            cmds.connectAttr(color_correct + '.outColor', shader_name + '.baseColor', force=True)

        elif textureType == "specularRoughness":
            #connecting RGH nodes   
            # Create an aiRange node
            ai_range = cmds.shadingNode('aiRange', asUtility=True, name=texture_name+"_AIR")
            # Connect the file texture to the aiRange node
            cmds.connectAttr(file_texture + '.outColor', ai_range + '.input')
            #Connec the aiRange to shader
            cmds.connectAttr(ai_range + '.outColor.outColorR', shader_name + '.'+textureType, force=True)
            cmds.setAttr(file_texture+".alphaIsLuminance",1) #set the alpha is luminance
        
        elif textureType == "metalness":  
            #connecting MTL nodes      
            # Create an aiRange node
            ai_range = cmds.shadingNode('aiRange', asUtility=True, name=texture_name+"_AIR")
            # Connect the file texture to the aiRange node
            cmds.connectAttr(file_texture + '.outColor', ai_range + '.input')
            #Connec the aiRange to shader  
            cmds.connectAttr(ai_range + '.outColor.outColorR', shader_name + '.'+textureType, force=True)
            cmds.setAttr(file_texture+".alphaIsLuminance",1)#set the alpha is luminance

        elif textureType == "normalCamera":  
            #connecting NRM nodes        
            # Create an aiNormal node
            ai_normal = cmds.shadingNode('aiNormalMap', asUtility=True,name = texture_name+"_AIN")
            # Connect the file texture to the aiRange node
            cmds.connectAttr(file_texture + '.outColor', ai_normal + '.input')
            #Connec the aiRange to shader  
            cmds.connectAttr(ai_normal + '.outValue', shader_name + '.'+textureType, force=True)


        
    def findTexturesPath(self,folder_path):
        """
        This function finds the relevant textures path from the given folder path

        Args:
            folder_path: path of the folder to iterate upon.
        Returns:
            None
        """
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


    def deleteShaderWidget(self):
        """
        This function deletes the widget from the parent UI

        Args:
            None
        Returns:
            None
        """
        self.setParent(None) #remove from the layout
        self.setVisible(False) #make it hidden
        self.deleteLater() #delete the UI as soon as it can
        
    def updateShaderName(self):
        """
        This function updates the shader name label based on the given input in the LineEdit Widget
        
        Args:
            None
        Returns:
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
        """
        This function makes a dialog for the User to pick the Base Color Texture path 
        
        Args:
            None
        Returns:
            None
        """
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
        """
        This function makes a dialog for the User to pick the Roughness Texture path 
        
        Args:
            None
        Returns:
            None
        """
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
        """
        This function makes a dialog for the User to pick the Metalness Texture path 
        
        Args:
            None
        Returns:
            None
        """
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
        """
        This function makes a dialog for the User to pick the Normal Texture path 
        
        Args:
            None
        Returns:
            None
        """
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
        """
        This function makes a dialog for the User to pick the Displacement Texture path 
        
        Args:
            None
        Returns:
            None
        """
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

class VP2ShaderCreator(QtWidgets.QWidget):  # Change to QWidget instead of QMainWindow
    """
    This is a VP2haderCreator class that lets us create the VP2 shaderWidget in the scroll area
    
    Methods:
        __init__: This is the Constructor function to initialize layout variables ,dict and also connections for each prefix found.
        createShader: This function creates a shader and calls the connectTextures() to assign textures to it. If assign and mesh is passed , then it will asign the shader to selected mesh
        createShaderAndAssign: This Function checks for any selected mesh. If there are any selected mesh, then a shader will be created and assigned
        connectTextures: This function checks the texturePaths dictionary and connects it to the passed shader if there are any paths
        connect_file_texture_to_shader: This functions creates a texture and connects it to the given shader based on the type of texture
        findTexturesPath: This function finds the relevant textures path from the given folder path
        deleteShaderWidget: This function deletes the widget from the parent UI
        updateShaderName: This function updates the shader name label based on the given input in the LineEdit Widget
        setBaseColorPath: This function makes a dialog for the User to pick the Base Color Texture path 

    """

    def __init__(self,prefix,filesList,folder_path,parent =None):
        """
        This is the Constructor function to initialize layout variables ,dict and also connections for each prefix found.
        
        Args:
            prefix: prefix to be set for the shaderNames and nodes
            filesList: list of files containing the same prefix
            folder_path: folderPath where the function iterates upon
        Returns:
            None
        """
        super(VP2ShaderCreator, self).__init__(parent=parent)
        ui_path = "/jobs/tvcResources/bangComms/waranr/Scripts/Git_Repository/QtUI/masterUIShaderCreator.ui"  # Replace with the path to your .ui file
        self.myUI = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)

        self.myUI.VP2Widget.setVisible(True)


        #hide mainlayouts
        self.myUI.standardSurfaceWidget.setVisible(False)
        self.myUI.standardSurfaceWidget.destroy(True)
        self.myUI.btn_browse.setVisible(False)
        self.myUI.btn_browse.destroy(True)
        self.myUI.input_folderPath.setVisible(False)
        self.myUI.input_folderPath.destroy(True)
        self.myUI.label.setVisible(False)
        self.myUI.label.destroy(True)

        #initialize prefix
        self.prefix = prefix
        self.listOfFiles = filesList

        #CONNECTIONS
        self.myUI.VP2_btn_createAndAssign.clicked.connect(self.createShaderAndAssign)
        self.myUI.VP2_btn_create.clicked.connect(self.createShader)
        
        
        self.myUI.VP2_input_shaderName.returnPressed.connect(self.updateShaderName)

        self.myUI.VP2_tb_baseColor.clicked.connect(self.setBaseColorPath)


        # Set minimum size based on adjusted size
        self.adjustSize()
        self.setMinimumSize(self.myUI.VP2Widget.sizeHint())

        #initalize dict for toolbuttons
        self.texturePaths = {
            "color" : None,
        }
        self.findTexturesPath(folder_path) #find textures and assign them
        self.myUI.VP2_lb_shaderName.setText(self.prefix.split("_primary")[0]+"_VP2") #set the name
        self.myUI.VP2_lb_shaderName.setToolTip(self.prefix.split("_primary")[0]+"_VP2") #set the tooltip
        #adjust the size of the label
        self.defaultFont = self.myUI.VP2_lb_shaderName.font()
        self.smallfont = QtGui.QFont()
        self.smallfont.setPointSize(10)
        self.smallfont.setBold(1)

        if (len(self.myUI.VP2_lb_shaderName.text()))>=27:
            self.myUI.VP2_lb_shaderName.setFont(self.smallfont)
        
    def createShader(self,assign = False, mesh = None):
        """
        This function creates a shader and calls the connectTextures() to assign textures to it. If assign and mesh is passed , then it will asign the shader to selected mesh

        Args:
            assign: bool to check if shader needs to be assigned
            mesh: mesh to assign the shader to.
        Returns:
            None
        """
        #get the name
        shaderName = self.myUI.VP2_lb_shaderName.text()
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
        Returns:
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
        
        Args:
            folder_path : path of the folder to iterate upon.
        Returns:
            None
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
            self.myUI.VP2_tb_baseColor.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.VP2_lb_path_baseColor.setText(vp2_path.split("/")[-1])
            #take out strike
            font = self.myUI.VP2_lb_baseColor.font()
            font.setStrikeOut(False)
            self.myUI.VP2_lb_baseColor.setFont(font)
        if not vp2_path:
            self.myUI.VP2_tb_baseColor.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.VP2_lb_path_baseColor.setText("No Texture Found")
            #strike it
            font = self.myUI.VP2_lb_baseColor.font()  
            font.setStrikeOut(True)
            self.myUI.VP2_lb_baseColor.setFont(font)

    def deleteShaderWidget(self):
        """
        This function deletes the widget from the parent UI
        
        Args:
            None
        Returns:
            None
        """
        self.setParent(None) #remove from the layout
        self.setVisible(False) #make it hidden
        self.deleteLater() #delete the UI as soon as it can
        
    def updateShaderName(self):
        """
        This function updates the shader name label based on the given input in the LineEdit Widget
        
        Args:
            None
        Returns:
            None
        """
        #get the name
        inputname = self.myUI.VP2_input_shaderName.text()
        name = inputname+"_VP2" #add suffix
        #update the text
        self.myUI.VP2_lb_shaderName.setText(name)
        self.myUI.VP2_lb_shaderName.setToolTip(name)#set the tooltip
        self.myUI.VP2_input_shaderName.clear()

        if (len(self.myUI.VP2_lb_shaderName.text()))>=27:
            self.myUI.VP2_lb_shaderName.setFont(self.smallfont)
        else:
            self.myUI.VP2_lb_shaderName.setFont(self.defaultFont)
    
    def setBaseColorPath(self):
        """
        This function makes a dialog for the User to pick the Base Color Texture path 
        
        Args:
            None
        Returns:
            None
        """
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Base Color Texture" ,dir = self.path)[0]
        except:
            file = QtWidgets.QFileDialog.getOpenFileName(self,"Choose Base Color  Texture")[0]
        self.texturePaths["color"]=file
        if file:
            self.myUI.VP2_tb_baseColor.setArrowType(QtCore.Qt.RightArrow)
            self.myUI.VP2_lb_path_baseColor.setText(file.split("/")[-1])
            #take out strike
            font = self.myUI.VP2_lb_baseColor.font()
            font.setStrikeOut(False)
            self.myUI.VP2_lb_baseColor.setFont(font)
        if not file:
            self.myUI.VP2_tb_baseColor.setArrowType(QtCore.Qt.NoArrow)
            self.myUI.VP2_lb_path_baseColor.setText("No Texture Selected")
            #strike it
            font = self.myUI.VP2_lb_baseColor.font()  
            font.setStrikeOut(True)
            self.myUI.VP2_lb_baseColor.setFont(font)

def createShaderCreatorMayaWindow():
    """
    This function makes an instance of the Shader Creator Window

    Args:
        None
    Returns:
        None
    """
    dock = getDock()
    arnold_shader_creatorWin = ShaderCreatorMayaWindow(parent=dock)
    dock.layout().addWidget(arnold_shader_creatorWin)

createShaderCreatorMayaWindow() #call the function to create the Window Class