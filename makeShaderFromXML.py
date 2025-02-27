"""
Script Name: makeShaderFromXML.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script is used to create materials and assign the materials to respective geometries using a XML file.
"""

from xml.dom import minidom
import maya.cmds as cmds
from PySide2 import QtWidgets,QtCore,QtGui
import os


#default locations 
XML_LOCATION = ''

TEXTURE_LOCATION = ''

#texture mapping Dictionary
TEXTURE_MAPPING = {
    'texmap_diffuse': 'baseColor',
    'texmap_reflection': 'specularColor',
    'texmap_reflectionGlossiness': 'specularRoughness',
    'texmap_reflectionIOR':'specularIOR',
    'texmap_refraction': 'transmissionColor',
    None :'metalness',
    None :'normalCamera', 
}

class ArnoldShader():
    """
    This class creates an Arnold shader with the Passed material name and textures

    Methods:
        __init__: This is the Constructor function to initialize variables for the Arnold Shader Class
        create_shader : This function creates a shader and calls the connect_file_texture_to_shader() to assign textures to it
        connect_file_texture_to_shader: This functions creates a texture and connects it to the given shader based on the type of texture
    """

    def __init__(self,name,textures):
        """
        This is the Constructor function to initialize variables for the Arnold Shader Class

        Args:
            name: name of the arnold shader
            textures: textures to be created for the shader
        Return:
            None
        """

        self.name = name
        self.textures = textures

        self.create_shader()

    def create_shader(self):
        """
        This function creates a shader and calls the connect_file_texture_to_shader() to assign textures to it

        Args:
            None
        Return:
            None
        """
        shaderName = self.name

        self.shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=shaderName)#create shader
        self.shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName + 'SG') #create Shading Group

        #set the spec to 0.25 by default 
        cmds.setAttr(self.shader+".specular",0.25) #set the transmission value

        #connect SG and shader
        cmds.connectAttr(self.shader + '.outColor', self.shading_group + '.surfaceShader', force=True)

        #connect Textures to the shader
        self.connect_file_texture_to_shader(shaderName)
         
    def connect_file_texture_to_shader(self,shader_name):
        """
        This functions creates a texture and connects it to the given shader based on the type of texture

        Args:
            shader_name: name of the shader to be connected with
        Returns:
            None
        """
        self.non_existing_textures = [] #empty list to collect all the unavailable textures

        #iterate through all the textures
        for texture in self.textures:
            for attr_name, attr_value in texture.attributes.items():
                #check if texture path provided
                if attr_name == 'path':
                    texture_path = TEXTURE_LOCATION+"/"+attr_value
                    #check if file exists and add it to the list
                    if not os.path.exists(texture_path):
                        self.non_existing_textures.append(texture_path)
                    #display
                    print(attr_name, TEXTURE_LOCATION+attr_value)
                else: #if not texture path its a texture type
                    for parameter_type,arnold_parameter in TEXTURE_MAPPING.items():
                        if parameter_type == attr_value:
                            texture_type = arnold_parameter
                    print(attr_name, attr_value)
            

            # Create a file texture node
            texture_name = texture_path.split("/")[-1].split(".")[0]#get the name of the texture
            file_texture = cmds.shadingNode('file', asTexture=True, name=texture_name+"_FTN")
            
            # Set the file path to the texture node and set it to UDIMS
            cmds.setAttr(file_texture + '.fileTextureName', texture_path, type='string')
            #cmds.setAttr(file_texture+".uvTilingMode",3)
            
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
            
            if texture_type == "baseColor":  
                #connecting DIF nodes        
                # Create a color correct node
                color_correct = cmds.shadingNode('aiColorCorrect', asUtility=True, name=texture_name+"_AIC")
                # Connect the file texture to the color correct node
                cmds.connectAttr(file_texture + '.outColor', color_correct + '.input')
                # Connect the color correct node to the shader
                cmds.connectAttr(color_correct + '.outColor', shader_name + '.'+texture_type, force=True)

            elif texture_type == "specularColor":
                #connecting DIF nodes        
                # Create a color correct node
                color_correct = cmds.shadingNode('aiColorCorrect', asUtility=True, name=texture_name+"_AIC")
                # Connect the file texture to the color correct node
                cmds.connectAttr(file_texture + '.outColor', color_correct + '.input')
                # Connect the color correct node to the shader
                cmds.connectAttr(color_correct + '.outColor', shader_name + '.'+texture_type, force=True)

            elif texture_type == "specularRoughness":
                #connecting RGH nodes   
                # Create an aiRange node
                ai_range = cmds.shadingNode('aiRange', asUtility=True, name=texture_name+"_AIR")
                # Connect the file texture to the aiRange node
                cmds.connectAttr(file_texture + '.outColor', ai_range + '.input')
                #Connec the aiRange to shader
                cmds.connectAttr(ai_range + '.outColor.outColorR', shader_name + '.'+texture_type, force=True)
                cmds.setAttr(file_texture+".alphaIsLuminance",1) #set the alpha is luminance
            
            elif texture_type == "specularIOR":
                #connecting RGH nodes   
                # Create an aiRange node
                ai_range = cmds.shadingNode('aiRange', asUtility=True, name=texture_name+"_AIR")
                # Connect the file texture to the aiRange node
                cmds.connectAttr(file_texture + '.outColor', ai_range + '.input')
                #Connec the aiRange to shader
                cmds.connectAttr(ai_range + '.outColor.outColorR', shader_name + '.'+texture_type, force=True)
                cmds.setAttr(file_texture+".alphaIsLuminance",1) #set the alpha is luminance
            
            elif texture_type == "transmissionColor":
                #connecting RGH nodes   
                # Create an aiRange node
                ai_range = cmds.shadingNode('aiRange', asUtility=True, name=texture_name+"_AIR")
                # Connect the file texture to the aiRange node
                cmds.connectAttr(file_texture + '.outColor', ai_range + '.input')
                #Connec the aiRange to shader
                cmds.connectAttr(ai_range + '.outColor', shader_name + '.'+texture_type, force=True)
                cmds.setAttr(self.shader+".transmission",1) #set the transmission value
                cmds.setAttr(file_texture+".alphaIsLuminance",1) #set the alpha is luminance
            
            elif texture_type == "metalness":  
                #connecting MTL nodes      
                # Create an aiRange node
                ai_range = cmds.shadingNode('aiRange', asUtility=True, name=texture_name+"_AIR")
                # Connect the file texture to the aiRange node
                cmds.connectAttr(file_texture + '.outColor', ai_range + '.input')
                #Connec the aiRange to shader  
                cmds.connectAttr(ai_range + '.outColor.outColorR', shader_name + '.'+texture_type, force=True)
                cmds.setAttr(file_texture+".alphaIsLuminance",1)#set the alpha is luminance

            elif texture_type == "normalCamera":  
                #connecting NRM nodes        
                # Create an aiNormal node
                ai_normal = cmds.shadingNode('aiNormalMap', asUtility=True,name = texture_name+"_AIN")
                # Connect the file texture to the aiRange node
                cmds.connectAttr(file_texture + '.outColor', ai_normal + '.input')
                #Connec the aiRange to shader  
                cmds.connectAttr(ai_normal + '.outValue', shader_name + '.'+texture_type, force=True)

class MainWindow(QtWidgets.QMainWindow):
    """
    This is a MainWindow class that lets us create the UI for this tool 
    
    Methods:
        __init__: This is the Constructor function to initialize variables for the MainWindow Class
        build_UI: This function builds the Main UI and makes relevant connections
        create_shader_from_xml: This function makes an instance os the Arnold Shader and assigns it to respective meshes
        check_for_mesh: This function checks for the geometries tag in xml and assigns it respective materials
        assign_mesh_to_material: This function assigns the passed material on the passed geometry based on the passed faces list 
        browse_xml_file: This function gets file path from the selected file and changes the text accordingly
        browse_texture_location: This function gets folder path from the selected folder and changes the text accordingly
        assign_xml_location: This function gets file path from the line edit and setst the value for XML_LOCATION
        assign_texture_location: This function gets file path from the line edit and sets the value for TEXTURE_LOCATION
        errored_texture: This function updates the log according to the passed shader and the textures
        errored_geometry: This function updates the log according to the passed material and shader
        errored_face_not_exist: This function updates the log according to the passed geometry and faces
    """
    def __init__(self):
        """
        This is the Constructor function to initialize variables for the MainWindow Class

        Args:
            None
        Return:
            None
        """
        super(MainWindow,self).__init__()
        self.setWindowTitle("XML Shader Creator")
        #self.setFixedSize(200,100)
        self.build_UI()
        
        #Set the window flags to keep the UI always on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
    
    def build_UI(self):
        """ 
        This function builds the Main UI and makes relevant connections

        Args:
            None
        Return:
            None
        """

        central_Widget = QtWidgets.QWidget()

        #declare some layouts
        self.central_layout = QtWidgets.QGridLayout()

        #set Layout to centralwidget
        central_Widget.setLayout(self.central_layout)
        self.setCentralWidget(central_Widget)

        #XML Location 
        self.xml_location = QtWidgets.QLineEdit()

        self.xml_location.setPlaceholderText("Set your XML File path here")
        xml_browse_btn = QtWidgets.QPushButton("Browse XML File")

        #Textures Location
        self.textures_location = QtWidgets.QLineEdit()
        self.textures_location.setPlaceholderText("Set your Textures Folder path here")
        textures_browse_btn = QtWidgets.QPushButton("Browse Textures Folder")

        #text edit for logs
        self.logs_window = QtWidgets.QPlainTextEdit()
        self.logs_window.setReadOnly(True)#set it not editable

        self.logs_window.setPlaceholderText("Set the XML File path and Textures Folder path")


        #add pbar and run button to layout
        self.pbar = QtWidgets.QProgressBar()
        run_button = QtWidgets.QPushButton("Create Shaders and Assign")

        self.pbar.setValue(0)#set initial value
        
        #connections
        run_button.clicked.connect(self.create_shader_from_xml)
        xml_browse_btn.clicked.connect(self.browse_xml_file)
        textures_browse_btn.clicked.connect(self.browse_texture_location)


        #set locations
        self.xml_location.textChanged.connect(self.assign_xml_location)
        self.textures_location.textChanged.connect(self.assign_texture_location)

        #add to layouts
        self.central_layout.addWidget(self.xml_location,0,0)
        self.central_layout.addWidget(xml_browse_btn,0,1)
        self.central_layout.addWidget(self.textures_location,1,0)
        self.central_layout.addWidget(textures_browse_btn,1,1)
        self.central_layout.addWidget(run_button,2,0,1,2)
        self.central_layout.addWidget(self.logs_window,3,0,1,2)
        #self.central_layout.addWidget(self.help_label,6,0,1,2)
        self.central_layout.addWidget(self.pbar,7,0,1,2)

    def create_shader_from_xml(self):
        """ 
        This function makes an instance os the Arnold Shader and assigns it to respective meshes 
        Args:
            None
        Return:
            None
        """

        #add a new help label
        self.help_label = QtWidgets.QLabel()
        self.help_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.logs_window.clear() #clear the logs

        existing_materials = cmds.ls(materials=True) #lists all the materials

        #empty dictionary store 
        createdMaterials = []

        #error out early if no paths in either
        if not XML_LOCATION or not TEXTURE_LOCATION:
            self.logs_window.insertPlainText("ERROR: Make sure to set the Locations for both XML and Textures!")
            return

        try:
            self.file = minidom.parse(XML_LOCATION) #open the xml file
            materials = self.file.getElementsByTagName("Materials")[0] #store all materials
        #error out materials
        except:
            self.logs_window.insertPlainText("ERROR: Check the XML File . No <Materials> Tag found in it")
            return

        total_steps = len(materials.childNodes) #total steps for calculating percentage

        #iterating through all materials
        i= 0 #counter variable for keeping track of iterations
        for material in materials.childNodes:
            i=i+1 #add the step counter
            #check if the node is an XML Element
            if material.nodeType == minidom.Node.ELEMENT_NODE: 
                #store the name of the material
                material_name = material.attributes['name'].value

                #display material details
                print('------------------------------------------------')
                print("Material: ", material_name)

                #store all the textures
                textures = material.getElementsByTagName('texture')

                #Check if it already exists in the scene
                for existing_mat in existing_materials:
                    if material_name == existing_mat:
                        new_name = existing_mat+"_old"
                        cmds.rename(existing_mat,new_name)

                #create the Arnold Shader instance for this material
                shader = ArnoldShader(material_name,textures)
                createdMaterials.append(material_name)

                #error updates
                if shader.non_existing_textures:
                    print("Non existing textures found!")
                    self.errored_texture(shader,material_name)

            #update progress bar
            progress_value = int((float(i) / total_steps) * 100)
            self.pbar.setValue(progress_value)#set the value

        log_text = self.logs_window.toPlainText()
        
        if 'TEXTURE ERROR' not in log_text:
            print('**'*25)
            print("Sucessfully created all Shaders from  the given XML")

            #update the help Message
            self.help_label.setText("Sucessfully created all Shaders from  the given XML")
        else:
            print('**'*25)
            print("Sucessfully created all Shaders from  the given XML (Some Textures doesnt exist. Repath Textures to fix this)")

            #update the help Message
            self.help_label.setText("Sucessfully created all Shaders from  the given XML (Some Textures doesnt exist. Repath Textures to fix this)")


        #add the help label to UI
        self.central_layout.addWidget(self.help_label,6,0,1,2)


        #run to check respective meshes
        self.check_for_mesh()

    def check_for_mesh(self):
        """ 
        This function checks for the geometries tag in xml and assigns it respective materials

        Args:
            None
        Return:
            None
        """

        self.errored_meshes = [] #empty list to collect errored geometries
        self.errored_faces = [] #empty list to collect errored geometries

        #list all the meshes
        all_geos = self.file.getElementsByTagName("Geometries")[0]

        #empty dict to store all the matches in {mat:mesh,mesh,mesh , mat:mesh,}
        material_to_mesh = {}

        #iterate through all materials
        for mat in all_geos.childNodes:
            #iterate through all geos and check if the node is an XML Element
            if mat.nodeType == minidom.Node.ELEMENT_NODE: 
                #store mat name
                mat_name = mat.attributes['name'].value 
                
                #append the key {mat:[]}
                if mat_name not in material_to_mesh:
                    material_to_mesh[mat_name] = []

                #iterate inside each material
                for geo in mat.childNodes:
                    #check if the node is an XML Element
                    if geo.nodeType == minidom.Node.ELEMENT_NODE: 
                        geo_name = geo.attributes['name'].value
                        #append the value {mat:[mesh,mesh]}
                        material_to_mesh[mat_name].append(geo_name)

                        #check for face selection parameter
                        face_assign_list = geo.attributes['face'].value
                        
                        if face_assign_list == "None":
                            self.assign_mesh_to_material(mat_name,geo_name,faces = None) #call the function with no face assignment
                        else:
                            self.assign_mesh_to_material(mat_name,geo_name,faces = face_assign_list) #call the function with face assignment

                if self.errored_meshes:
                    #call the function to update the log
                    self.errored_geometry(mat_name)
        
        log_text = self.logs_window.toPlainText()
        if 'GEOMETRY ERROR' not in log_text and 'FACES ERROR' not in log_text:
            #update the label
            info = self.help_label.text()
            updated_info = info + "\nSucessfully assigned all Shaders to the objects in the scene"
            self.help_label.setText(updated_info)
        
        if 'GEOMETRY ERROR' not in log_text and 'FACES ERROR' not in log_text and 'TEXTURE ERROR' not in log_text:
            self.logs_window.appendPlainText("No Errors Found")

    def assign_mesh_to_material(self,mat_name,geo_name,faces):
        """ 
        This function assigns the passed material on the passed geometry based on the passed faces list 

        Args:
            mat_name: material to apply
            geo_name: geometry to be applied on
            faces: list of strings for face selections
        Return:
            None
        """

        if not faces :
            #FOR OBJECT ASSIGNMENT
            print(geo_name + " has to be Object Assigned by "+ mat_name)

            #if it exists
            try:
                cmds.select(geo_name)
                cmds.hyperShade(assign=mat_name)
            except:
                #append to list
                self.errored_meshes.append(geo_name)
                print(geo_name+ " is not in scene")
        else:
            #FOR FACE ASSIGNMENT
            faces = faces.split(",") #split the list of ranges 

            print(geo_name + " has to be Face Assigned by "+ mat_name + " with faces: "+str(faces))
            
            #check if the geo exists first
            try:
                cmds.select(geo_name)
            except:
                #append to list
                self.errored_meshes.append(geo_name)
                print(geo_name+ " is not in scene")
                return
            
            #store all the faces in the geometry
            all_faces = cmds.polyListComponentConversion(geo_name, toFace=True)
            all_faces = cmds.ls(all_faces, flatten=True)

            print(all_faces)
            
            #if it exists
            for face_range in faces:
                #split the [1:2] to range(1,2)
                lower_range = int(face_range.split(":")[0])
                higher_range = int(face_range.split(":")[1])

                #iterate through all the faces and check
                for face in range(lower_range,higher_range+1):
                    print("Checking f["+str(face)+"]")
                    face_str = "{0}.f[{1}]".format(geo_name,str(face))
                    if face_str not in all_faces:
                        #update the faces list
                        self.errored_faces.append(face) 
                        print(str(face)+ " is not in the geo")
                        continue
                    else:
                        #assign the material
                        cmds.select("{0}.f[{1}]".format(geo_name,str(face)))
                        cmds.hyperShade(assign=mat_name)
            
            if self.errored_faces:
                self.errored_face_not_exist(geo_name)

    def browse_xml_file(self):
        """ 
        This function gets file path from the selected file and changes the text accordingly

        Args:
            None
        Returns:
            None
        """

        self.xml_path = QtWidgets.QFileDialog.getOpenFileName(self,"Choose XML File",filter= "XML files (*.xml)")[0] #open a dialog
        self.xml_location.setText(self.xml_path) #update path

    def browse_texture_location(self):
        """ 
        This function gets folder path from the selected folder and changes the text accordingly

        Args:
            None
        Returns:
            None
        """

        self.textures_path = QtWidgets.QFileDialog.getExistingDirectory(self,"Choose Textures Folder" ) #open a dialog
        self.textures_location.setText(self.textures_path) #update path

    def assign_xml_location(self):
        """ 
        This function gets file path from the line edit and setst the value for XML_LOCATION

        Args:
            None
        Returns:
            None
        """
        global XML_LOCATION
        XML_LOCATION = self.xml_location.text()

        #update pbar
        self.pbar.setValue(0)#set initial value

        #reset log and label
        self.logs_window.clear() #clear the logs
        self.central_layout.removeWidget(self.help_label) #remove the widget
        self.help_label.deleteLater() #delete the widget

    def assign_texture_location(self):
        """ 
        This function gets file path from the line edit and sets the value for TEXTURE_LOCATION

        Args:
            None
        Returns:
            None
        """

        global TEXTURE_LOCATION
        TEXTURE_LOCATION = self.textures_location.text()

        #update pbar
        self.pbar.setValue(0)#set initial value

        #reset log and label
        self.logs_window.clear() #clear the logs
        self.central_layout.removeWidget(self.help_label) #remove the widget
        self.help_label.deleteLater() #delete the widget

    def errored_texture(self,shader,material_name):
        """ 
        This function updates the log according to the passed shader and the textures

        Args:
            shader: name of the shader
            material_name: name of the material
        Returns:
            None
        """
        errored_textures = shader.non_existing_textures
        self.logs_window.appendPlainText("\nTEXTURE ERROR: Textures doesn't exist for ("+ material_name+")")
        for texture in errored_textures:
            self.logs_window.appendPlainText("     "+texture)

    def errored_geometry(self,material):
        """ 
        This function updates the log according to the passed material and shader

        Args:
            material: name of the material
        Returns:
            None
        """
        #update the log
        self.logs_window.appendPlainText("\nGEOMETRY ERROR: Geometries not found in scene for ("+ material+")")
        #iterate through the geos
        for geo in self.errored_meshes:
            self.logs_window.appendPlainText("     "+geo)
        
        #clear the list for next material
        self.errored_meshes = []
 
    def errored_face_not_exist(self,geo):
        """ 
        This function updates the log according to the passed geometry and faces

        Args:
            geo: name of the geo
        Returns:
            None
        """
        #update the log
        self.logs_window.appendPlainText("\nFACES ERROR: Faces not found in geometry for ("+ geo+")")
        #iterate through the geos
        for face in self.errored_faces:
            self.logs_window.appendPlainText("     "+str(face))
        
        #clear the list for next material
        self.errored_faces = []

#make an instance of the Window class
window = MainWindow()
window.show()