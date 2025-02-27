"""
Script Name: materialQC.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script is used to QC the materials in a maya scene before publishing it
"""

sys.path.append("/jobs/tvcResources/bangComms/waranr/Scripts/Git_Repository/QtUI") #for accessing the resource file (newIcons_rc)

from PySide2 import QtWidgets,QtUiTools,QtGui,QtCore
import maya.cmds as cmds
import pprint
import pymel.core as pm
import os
import sys
import newIcons_rc #you need this complied version of the resource file to access icons used in your UI

cmds.flushUndo() #flush the undo queue to free up memory

class MaterialQC(QtWidgets.QWidget):

    """
    This class is used for creating the Material QC Window and Start QCing the materials in the scene

    Methods:
        init: Initializes the material QC class 
        buildUI : This function builds the UI for Material QC and makes the necessary connections
        setStatusGreen : This function changes the icon of the status button to green and also sets enable state for select button
        setStatusRed : This function changes the icon of the status button to red and also sets enable state for select button
        setStatusYellow : This function changes the icon of the passed button to yellow 
        updateDictionaries : This function updates the dictionaries required for the methods
        allQC: Calls all the QCs 
        find_custom_shaders_and_shading_groups: gets the custom shaders and shading groups
        namingConvention_QC : QC for naming convention check of each shaders and shading Groups
        find_meshes_to_shaders : This function finds all the meshes connected to each shader in the scene
        unusedNodes_QC: QC for checking the unused nodes in the scene
        deleteUnusedNodes : This function deletes the unused nodes from the scene
        fixNamingConventions: This function adds the required suffixes on the incorrect shaders and shading groups
        lambertMeshes_QC : This Function checks the scene for meshes that are in lambert1
        faceSelection_QC : This function checks if any shaders are assigned in face selection mode
        find_allTextureNodePaths : This function gets all the texture paths of all the texture file nodes.
        texturesInCurrentJob_QC: This function checks if all the texture are in current Job
        publishedTextures_QC : This function checks if all the textures that are connected to the shaders are published
        duplicateTextures_QC : This function checks if there are any texture duplicates in the scene
        selectNodes : This function selects all the nodes that passed as list arguments
        populateErrorWidget : This function populates the Error widget based on the passed argument
        selectItem : This function selects the specific item that is clicked on the list widget
        clearErrorWidget : This function clears the Error widget completely

    """

    def __init__(self,selection = None):
        """
        This is the constructor class for Material QC 

        Args:
            None
        Returns:
            None
        """

        #INITIALIZE CLASS ELEMENTS and its parent
        super(MaterialQC,self).__init__()

        #initialize variables
        self.currentJob = os.environ['JOB']

        self.selectedGrp = selection

        #BUILD UI and CONNECTIONS
        self.buildUI()
    
    def buildUI(self):
        """    
        This function builds the UI for Material QC and makes the necessary connections

        Args:
            None
        Returns:
            None
        """

        ####### LOAD UI #######
        ui_path = "/jobs/tvcResources/bangComms/waranr/Scripts/Git_Repository/QtUI/masterUIMaterialQC.ui"  # Replace with the path to your .ui file
        self.ui = QtUiTools.QUiLoader().load(ui_path, parentWidget=self)
        self.setWindowTitle("Material QC")
        
        #externally set a layout
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.ui)
        self.setLayout(self.layout)
        self.setMaximumSize(127695,127695)


        #setTitle for headerLayout
        self.ui.lb_title.setText("Material QC Tool - Beta 0.1 | {0}".format(self.currentJob))

        #set selected Group text
        if self.selectedGrp:
            self.ui.lb_selectedGrp.setText(self.selectedGrp )
        else:
            self.ui.lb_selectedGrp.setText("All")

        #set overall Style Sheet
        self.setStyleSheet('''
            * { color: white;
                font-size: 13px;
                font-family: "Arial";
                }
            
        ''')
        self.layout.setMargin(5)

        #set alignment for gridboxes

        self.ui.vlo_mandatoryQC.setAlignment(QtCore.Qt.AlignTop )
        self.ui.vlo_generalQC.setAlignment(QtCore.Qt.AlignTop )

        ####### UI CONNECTIONS #######

        #run button
        self.ui.btn_run.clicked.connect(self.allQC) 

        #refresh buttons
        self.ui.btn_refreshNamingConvention.clicked.connect(lambda : self.namingConvention_QC(refresh=True))
        self.ui.btn_refreshUnusedNodes.clicked.connect(lambda : self.unusedNodes_QC(refresh= True))
        self.ui.btn_refreshCurrentJob.clicked.connect(lambda : self.texturesInCurrentJob_QC(refresh= True))
        self.ui.btn_refreshPublishedTextures.clicked.connect(lambda : self.publishedTextures_QC(refresh= True))
        self.ui.btn_refreshDuplicateTextures.clicked.connect(lambda : self.duplicateTextures_QC(refresh= True))
        self.ui.btn_refreshDefaultShaders.clicked.connect(lambda : self.lambertMeshes_QC(refresh= True))
        self.ui.btn_refreshFaceSelection.clicked.connect(lambda : self.faceSelection_QC(refresh= True))

        #select buttons
        self.ui.btn_selectNamingConvention.clicked.connect(lambda : self.selectNodes(self.incorrectShaders,self.incorrectShadingGroups))
        self.ui.btn_selectUnusedNodes.clicked.connect(lambda : self.selectNodes(self.unused_textures,self.unused_shaders))
        self.ui.btn_selectCurrentJob.clicked.connect(lambda : self.selectNodes(self.incorrectJobTextures))
        self.ui.btn_selectPublishedTextures.clicked.connect(lambda : self.selectNodes(self.unpublishedTextures))
        self.ui.btn_selectDuplicateTextures.clicked.connect(lambda : self.selectNodes(self.duplicateTextures))
        self.ui.btn_selectDefaultShaders.clicked.connect(lambda: self.selectNodes(self.lambertMeshes))
        self.ui.btn_selectFaceSelection.clicked.connect(lambda: self.selectNodes(self.faceAssignedShaders))
    
    def setStatusGreen(self,statusLabel,selButton):
        """
        This function changes the icon of the status label to green and also sets enable state for select button

        Args:
            statusLabel : label to switch icon for
            selButton : button to be enabled
        Returns:
            None
        """

        #store new color and icon
        statusLabel.setStyleSheet("background-color: rgb(100, 100, 100)")
        greenIconPath = ":/newIcons/UI_Icons/xgGreenDot.png"
        greenIcon = QtGui.QPixmap(greenIconPath)

        #status label properties
        statusLabel.setPixmap(greenIcon)
        statusLabel.setToolTip("No Errors Found") #set the tooltip

        #select button properties
        selButton.setEnabled(False)
 
    def setStatusRed(self,statusLabel,selButton):
        """
        This function changes the icon of the status label to red and also sets enable state for select button
        
        Args:
            statusLabel : button to switch icon for
            selButton : button to be enabled
        Returns:
            None
        """

        #store new color and icon
        statusLabel.setStyleSheet("background-color: rgb(100, 100, 100)")
        redIconPath = ":/newIcons/UI_Icons/xgRedDot.png"
        redIcon = QtGui.QPixmap(redIconPath)

        #status label properties
        statusLabel.setPixmap(redIcon)
        statusLabel.setToolTip("Errors Found") #set the tooltip

        #select button properties
        selButton.setEnabled(True)

    def setStatusYellow(self,statusLabel):
        """
        This function changes the icon of the passed label to Yellow
        
        Args:
            statusLabel : label to switch icon for
        Returns:
            None
        """

        #store new color and icon
        statusLabel.setStyleSheet("background-color: rgb(100, 100, 100)")
        yellowIconPath = ":/newIcons/UI_Icons/xgYellowDot.png"
        yellowIcon = QtGui.QPixmap(yellowIconPath)

        #status label properties
        statusLabel.setPixmap(yellowIcon)

    def updateDictionaries(self):
        """ 
        This function updates the dictionaries required for the methods

        Args:
            None
        Returns:
            None
        """
        #update all the necessary dictionaries
        self.shadingDict = self.find_custom_shaders_and_shading_groups() #this dict contains all the shading engine and their shaders info
        self.shaderToMeshes = self.find_meshes_to_shaders() #this dict contains all the shader and their assignment info
        self.texturePaths = self.find_allTextureNodePaths() #this dict contains all the textures and their paths info

    def allQC(self):
        """
        This function calls all the QCs for the selected meshes and its shaders , while also updating the progress bar and selected Group label

        Args:
            None
        Returns:
            None
        """

        print("-"*80)
        print("...Materials QC started ...")

        self.updateDictionaries() #get latest data from scene

        #clear the error widget first
        self.clearErrorWidget()

        #update progress bar
        self.ui.pbar_globalRun.setValue(0) #update progress

        print("\nMANDATORY CHECKS\n")

            #### MANDATORY CHECKS ####
        
        #run namingcheck_QC
        self.namingConvention_QC()
        self.fixNamingConventions #call it after confirmation
        self.ui.pbar_globalRun.setValue(15) #update progress
        print("\n")

        #run UnusedNodes_QC
        self.unusedNodes_QC()
        self.deleteUnusedNodes #call it after confirmation
        self.ui.pbar_globalRun.setValue(30)
        print("\n")
        
        #run texturesInCurrentJob_QC_
        self.texturesInCurrentJob_QC()
        self.ui.pbar_globalRun.setValue(45) #update progress
        print("\n")

        #run publishedTextures_QC
        self.publishedTextures_QC()
        self.ui.pbar_globalRun.setValue(60) #update progress
        print("\n")

        #run duplicateTextures_QC
        self.duplicateTextures_QC()
        self.ui.pbar_globalRun.setValue(75) #update progress
        print("\n")

        #run lambertMeshes_QC
        self.lambertMeshes_QC()
        self.ui.pbar_globalRun.setValue(90) #update progress

        print("\nGENERAL CHECKS\n")

            #### OPTIONAL CHECKS ####       
        
        #run the faceSelection_QC
        self.faceSelection_QC()
        self.ui.pbar_globalRun.setValue(100) #update progress

        count = 0 #counts the number of errors in the selected group

        #check if there are error lists in the errorLists
        for i in range(self.ui.vlo_errorLists.count()):
            count+=1
        
        if count == 0:
            #update label in error message if there are no errors
            self.ui.lb_errorMessage.setText("All QC Finished Succesfully (0 Errors)")

            #update the color
            self.ui.pbar_globalRun.setStyleSheet("QProgressBar {border: 0px;} QProgressBar::chunk {background-color: #00BFFF;}")
        else:
            #update label in error message if there are any errors
            self.ui.lb_errorMessage.setText("There are "+str(count)+" QC Failures")

            #update the pbar color to red
            self.ui.pbar_globalRun.setStyleSheet("QProgressBar {border: 0px;} QProgressBar::chunk {background-color: rgb(255, 20, 20);}")

    def find_custom_shaders_and_shading_groups(self):
        """
        This function lists all the shaders and shading groups and stores it in a dict (except default materials and shading groups)

        Args:
            None
        Returns:
            custom_shaders_and_group : a dict containing all the shaders and shading groups in format {SG:Shader}
        """

        # Default shaders and shading groups
        default_shaders = {"lambert1", "particleCloud1"}
        default_shading_groups = {"initialShadingGroup", "initialParticleSE"}
        
        # List all shading groups in the selected group
        if cmds.ls(sl=True):
            var = cmds.ls(sl=True)
            if cmds.nodeType(var)== "transform" and not cmds.listRelatives(var,shapes=True): #check if selection is a group
                selected_group = cmds.ls(sl=True)
                self.selectedGrp = selected_group[0] #store the first group
                descendants = cmds.listRelatives(selected_group[0], allDescendents=True, fullPath=True) or []
                shading_groups = set() #empty list for storing shading groups
                for descendant in descendants: 
                    shapes = cmds.listRelatives(descendant, shapes=True, fullPath=True) or []
                    for shape in shapes:
                        sg_nodes = cmds.listConnections(shape, type='shadingEngine') or [] #store the shading groups of selected shape node
                        shading_groups.update(sg_nodes) #update the list
            else : 
                #if selected is not a group
                self.selectedGrp = None 
                shading_groups = cmds.ls(type='shadingEngine') #list all shading Engine

        # List all shading groups in the scene
        if not cmds.ls(sl=True):
            self.selectedGrp = None
            shading_groups = cmds.ls(type='shadingEngine')
        
        #set selected Group label 
        if self.selectedGrp:
            self.ui.lb_selectedGrp.setText(self.selectedGrp ) 
        else:
            self.ui.lb_selectedGrp.setText("All" )
            
        # Dictionary to store custom shaders and their shading groups
        custom_shaders_and_groups = {}

        try:
            #iterate through the shading groups
            for shading_group in shading_groups:
                if shading_group not in default_shading_groups: #filter out the default shading group
                    # Get shaders connected to the shading group
                    connected_shader = cmds.ls(cmds.listConnections(shading_group + ".surfaceShader"), materials=True)
                    # Filter out default shaders
                    if connected_shader[0] not in default_shaders:
                        shader = connected_shader[0] 

                    if shader:
                        custom_shaders_and_groups[shading_group] = shader #update the dictionary
            
        except:
            #make an error window displaying the error 
            print("Select a Group to QC . For Global QC of materials in the scene, try Removing existing Turntables and Optimizing the scene before running Material QC")
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setInformativeText(" For Global QC of materials in the scene, try Removing existing Turntables and Optimizing the scene before running Material QC")
            msg.setText("Select a Group to QC!")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.show()
            print("Aborting...")
            #raise an error
            raise RuntimeError("Select a Group to QC . For Global QC of materials in the scene, try Removing existing Turntables and Optimizing the scene before running Material QC")
        
        return custom_shaders_and_groups

    def namingConvention_QC(self,refresh = False ):
        """
        QC for checking the naming convention of all the Shaders and Shading groups  and returns the wrong ones

        Args:
            refresh : boolean value to refresh the dictionaries 
        Returns:
            incorrectShadingGroups: list of all the shading groups with incorrect names
            incorrectShaders : list of all the shaders with incorrect names
        """
        print("...Naming Convention QC started ...")
        
        #update dictionaries if refresh is True
        if refresh:
            self.updateDictionaries() 
            self.ui.lb_errorMessage.setText("Updated Naming Convention QC ") #update label
        else:
            pass
        
        #for collecting results
        self.incorrectShadingGroups = []
        self.incorrectShaders = []

        #iterate and check for naming conventions
        if self.shadingDict: 
            total_steps = len(self.shadingDict.keys()) #total steps for calculating percentage
            i = 0 #counter variable for keeping track of iterations
            #check for suffixes and append accordingly
            for sg,shd in self.shadingDict.items():
                if not sg.endswith("_MATSG") and not sg.endswith("_SHDSG"): #sg check condition
                    self.incorrectShadingGroups.append(sg)
                if not shd.endswith("_MAT") and not shd.endswith("_SHD"): #shd check condition
                    self.incorrectShaders.append(shd)

                #update progress bar
                i=i+1 #add the counter
                progress_value = int((float(i) / total_steps) * 100)
                self.ui.pBar_namingConvention.setValue(progress_value) #set the value
        else:
            print("No Shaders to check for Naming Convention")
            self.ui.pBar_namingConvention.setValue(100) #set the value of progress bar

        #display results
        if self.incorrectShaders:
            print("Incorrect Shader names found:")
            print(self.incorrectShaders)
        else:
            print("No Incorrect Shader names found")
        if self.incorrectShadingGroups:      
            print("Incorrect Shading Groups names found:")
            print(self.incorrectShadingGroups)

        else:
            print("No incorrect Shading Groups names found")

        #setting the icon in UI
        if self.incorrectShaders or self.incorrectShadingGroups:
            self.setStatusRed(self.ui.lb_statusNamingConvention,self.ui.btn_selectNamingConvention) #set the icon to red and enable select
        else:
            self.setStatusGreen(self.ui.lb_statusNamingConvention,self.ui.btn_selectNamingConvention) #set the icon to green and disable select

        #populate the error widget with the text on ui and return values
        if refresh:
            self.populateErrorWidget(self.ui.lb_labelNamingConvention.text(), returnVal1 = self.incorrectShadingGroups,returnVal2=self.incorrectShaders,update=True) 
        else:
            self.populateErrorWidget(self.ui.lb_labelNamingConvention.text(), returnVal1 = self.incorrectShadingGroups,returnVal2=self.incorrectShaders) 

        #enabling the refresh button
        self.ui.btn_refreshNamingConvention.setEnabled(True)

        return (self.incorrectShadingGroups,self.incorrectShaders)  

    def find_meshes_to_shaders(self):
        """
        This function finds all the meshes connected to each shader in the scene.

        Args:
            None
        Returns:
            shader_to_meshes: a dict containing the info of all the shader to meshes connections in format {SHD: [mesh]}
        """
        # Dictionary to store shaders and their assigned meshes
        shader_to_meshes = {}

        # Iterate through each shading engine
        for sg,shader in self.shadingDict.items():
            if shader:
                # Get all meshes connected to the shading engine
                meshes = cmds.sets(sg, query=True)
                # If there are meshes, add them to the dictionary
                if meshes:
                    if shader in shader_to_meshes:
                        shader_to_meshes[shader].extend(meshes)
                    else:
                        shader_to_meshes[shader] = meshes
                else:
                    # If there are no meshes, ensure the shader is in the dictionary with an empty list
                    if shader not in shader_to_meshes:
                            shader_to_meshes[shader] = []

        return shader_to_meshes

    def unusedNodes_QC(self,refresh = False):
        """
        QC for checking the unused nodes in the scene

        Args:
            refresh : boolean value to refresh the dictionaries 
        Returns:
            unused_shaders : a list containing all the unused shaders in the scene
            unused_textures : a list containing all the unused textures in the scene
        """
        print("...Unused Nodes QC started ...")
        
        #update dictionaries if refresh is True
        if refresh:
            self.updateDictionaries()
            self.ui.lb_errorMessage.setText("Updated Unused Nodes QC ") #update label
        else:
            pass
        
        #update the Dicts
        self.shaderToMeshes = self.find_meshes_to_shaders()
        self.texturePaths = self.find_allTextureNodePaths()

        # List to store unused shaders
        self.unused_shaders = [shader for shader, meshes in self.shaderToMeshes.items() if not meshes]
        #List to store unused Textures
        self.unused_textures = []

        #if textures in the scene
        if self.texturePaths:
            total_steps = len(self.texturePaths.keys()) #total steps for calculating percentage
            i = 0 #counter variable for keeping track of iterations
            for tex,paths in self.texturePaths.items():
                isConnected = False #default value
                #find if there are any connections for each textureNodes
                if cmds.connectionInfo(tex+".outColor",isSource=True):
                    isConnected = True
                elif cmds.connectionInfo(tex+".outColorR",isSource=True):
                    isConnected = True
                elif cmds.connectionInfo(tex+".outColorG",isSource=True):
                    isConnected = True
                elif cmds.connectionInfo(tex+".outColorB",isSource=True):
                    isConnected = True
                elif cmds.connectionInfo(tex+".outAlpha",isSource=True):
                    isConnected = True

                if not isConnected:
                    self.unused_textures.append(tex) 

                #update progress bar
                i=i+1 #add the step counter
                progress_value = int((float(i) / total_steps) * 100)
                self.ui.pBar_unusedNodes.setValue(progress_value)#set the value

            if self.unused_textures:
                print("Unused Textures in the scene found: ")
                pprint.pprint(self.unused_textures)
            else:
                print("No Unused Textures are present, All Textures are connected ")
        else:
            print("No Textures in the scene")
            self.ui.pBar_unusedNodes.setValue(100) #set value for progressbar

        #display results
        if self.unused_shaders:
            print("Unused Shaders in the scene found: ")
            pprint.pprint(self.unused_shaders)
        else:
            print("No Unused Shaders are present, All Shaders are assigned ")
        
        #setting the icon in UI
        if self.unused_shaders or self.unused_textures:
            self.setStatusRed(self.ui.lb_statusUnusedNodes,self.ui.btn_selectUnusedNodes) #set the icon to red and enable select
        else:
            self.setStatusGreen(self.ui.lb_statusUnusedNodes,self.ui.btn_selectUnusedNodes) #set the icon to green and disable select

        #populate the error widget with the text on ui and return values
        if refresh:
            self.populateErrorWidget(self.ui.lb_labelUnusedNodes.text(), returnVal1 = self.unused_shaders,returnVal2=self.unused_textures,update=True) 
        else:
            self.populateErrorWidget(self.ui.lb_labelUnusedNodes.text(), returnVal1 = self.unused_shaders,returnVal2=self.unused_textures) 

        #enabling the refresh button
        self.ui.btn_refreshUnusedNodes.setEnabled(True)

        return self.unused_shaders,self.unused_textures
    
    def deleteUnusedNodes(self):
        """
        This function deletes the unused nodes from the scene
faceSelectiom_QC : This function checks if any shaders are assigned in face selection mode
        Args:
            None
        Returns:
            None
        """
        print("..Deleting Unused Nodes..")
        pm.mel.MLdeleteUnused() #run the 'delete Unused nodes' command in Hypershade

    def fixNamingConventions(self):
        """
        This function adds the required suffixes on the incorrect shaders and shading groups

        Args:
            None
        Returns:
            None
        """
        print("..Fixing the Naming Conventions..")

        if self.incorrectShadingGroups: 
            print("Fixing incorrect Shading Groups..")
            for sg in self.incorrectShadingGroups:
                print("fixing "+sg)
                cmds.rename(sg,sg+"_MATSG")
                self.incorrectShadingGroups.remove(sg)
        else:
            print("No incorrect shading Group names to fix")
        if self.incorrectShaders:
            print("Fixing incorrect Shaders..")
            for shd in self.incorrectShaders:
                print("fixing "+shd)
                cmds.rename(shd,shd+"_MAT")
                self.incorrectShaders.remove(shd)
        else:
            print("No Incorrect Shader names to fix")
        

        #update the shading dict
        self.shadingDict = self.find_custom_shaders_and_shading_groups()
        
    def lambertMeshes_QC(self, refresh = False):
        """
        This Function checks the scene for meshes that are in lambert1

        Args:
            refresh : boolean value to refresh the dictionaries 
        Returns:
            lambertMeshes : a list of all the meshes that are in lambert1
        """
        print("...Default Shader QC started...")
        
        #update dictionaries if refresh is True
        if refresh:
            self.updateDictionaries()
            self.ui.lb_errorMessage.setText("Updated Default Shaders QC ") #update label
        else:
            pass

        #save all the meshes assigned in lambert
        self.lambertMeshes = cmds.sets("initialShadingGroup", query=True)

        splitList = [] #empty list to split the strings and store them
        if self.lambertMeshes:
            print("Meshes in lambert1 found:")

            total_steps = len(self.lambertMeshes) #total steps for calculating percentage
            i = 0 #counter variable for keeping track of iterations
            for mesh in self.lambertMeshes:
                print(mesh)
                splitList.append(mesh.split("|")[-1])

                #update progress bar
                i=i+1 #add the step counter
                progress_value = int((float(i) / total_steps) * 100)
                self.ui.pBar_defaultShaders.setValue(progress_value)#set the value
            #setting the icon in UI
            self.setStatusRed(self.ui.lb_statusDefaultShaders,self.ui.btn_selectDefaultShaders) #set the icon to red and enable select
        else:
            print("No default shader (lambert1) meshes present in the scene")
            self.ui.pBar_defaultShaders.setValue(100)#set the value for progress bar

            #setting the icon in UI
            self.setStatusGreen(self.ui.lb_statusDefaultShaders,self.ui.btn_selectDefaultShaders) #set the icon to green and disable select
        
        #reassign the return lists
        if splitList:
            self.lambertMeshes = splitList #update the list with the split version

        #populate the error widget with the text on ui and return values
        if refresh:
            self.populateErrorWidget(self.ui.lb_labelDefaultShaders.text(), returnVal1 = self.lambertMeshes,update=True) 
        else:
            self.populateErrorWidget(self.ui.lb_labelDefaultShaders.text(), returnVal1 = self.lambertMeshes) 

        #enabling the refresh button
        self.ui.btn_refreshDefaultShaders.setEnabled(True)

        return self.lambertMeshes

    def faceSelection_QC(self, refresh = False) : 
        """
        This function checks if any shaders are assigned in face selection mode

        Args:
            refresh : boolean value to refresh the dictionaries 
        Returns:
            faceAssignedShaders: a list of all shaders that has face selection assignments
        """
        print("...Face Selection QC started...")

        #update dictionaries if refresh is True
        if refresh:
            self.updateDictionaries()
            self.ui.lb_errorMessage.setText("Updated Face Selection QC ") #update label
        else:
            pass

        #empty list to collect the shader list
        self.faceAssignedShaders = []

        if self.shaderToMeshes:
            total_steps = len(self.shaderToMeshes.keys()) #total steps for calculating percentage
            i = 0 #counter variable for keeping track of iterations
            for shd,meshes in self.shaderToMeshes.items():
                if meshes:
                    for mesh in meshes:
                        if (".f") in mesh:
                            if shd in self.faceAssignedShaders:
                                pass
                            else:
                
                                self.faceAssignedShaders.append(shd)
                #update progress bar
                i=i+1 #add the step counter
                progress_value = int((float(i) / total_steps) * 100)
                self.ui.pBar_faceSelection.setValue(progress_value)#set the value
        else:
            print("No shaders to check for Face selection")
            self.ui.pBar_faceSelection.setValue(100)#set the value of progress bar

        if self.faceAssignedShaders:
            print("Shaders with Face Selection assignments found:")
            print(self.faceAssignedShaders)
        else :
            print("No Shaders has any Face Selection assignments")

        #setting the icon in UI
        if self.faceAssignedShaders:
            self.setStatusRed(self.ui.lb_statusFaceSelection,self.ui.btn_selectFaceSelection) #set the icon to red and enable select
        else:
            self.setStatusGreen(self.ui.lb_statusFaceSelection,self.ui.btn_selectFaceSelection) #set the icon to green and disable select

        #populate the error widget with the text on ui and return values
        if refresh:
            self.populateErrorWidget(self.ui.lb_labelFaceSelection.text(), returnVal1 = self.faceAssignedShaders,update=True) 
        else:
            self.populateErrorWidget(self.ui.lb_labelFaceSelection.text(), returnVal1 = self.faceAssignedShaders) 

        #enabling the refresh button
        self.ui.btn_refreshFaceSelection.setEnabled(True)

        return self.faceAssignedShaders

    def find_allTextureNodePaths(self) : 
        """
        This function gets all the texture paths of all the texture file nodes.

        Args:
            None
        Returns:
            texturePaths : a dict containg all the texture nodes and their respective file paths in format {texture : path of the texture }
        """
        texturePaths = {}

        #to skip below textures
        TT_textures = ['dome_overcast_ACEScg_file', 'dome_studioSmall_ACEScg_file', 'dome_studioContrast_file', 'sunny_HDRI_file_lkdv_Tmpl', 'lightRig_gray_bg_file', 'dome_custom2_missing_file', 'dome_custom1_file', 'sunny_ACEScg_HDRI_file_lkdv_Tmpl', 'dome_sunny_ACEScg_file', 'dome_sunny_noSun_ACEScg_file', 'macbeth_ACEScg_FILE_lkdv_Tmpl', 'custom_HDRI_file_lkdv_Tmpl', 'chart_ACEScg_file', 'lightRig_gray_bgLogo_file', 'dome_night_ACEScg_file', 'macbeth_AlexaGamut_FILE_lkdv_Tmpl', 'dome_custom1_missing_file', 'dome_custom2_file', 'dome_cloudy_ACEScg_file', 'dome_custom0_file', 'dome_custom0_missing_file', 'neutral_ACEScg_HDRI_file_lkdv_Tmpl', 'warm_HDRI_file_lkdv_Tmpl', 'custom_PLATE_lkdv_Tmpl', 'dome_studio_ACEScg_file', 'warm_ACEScg_HDRI_file_lkdv_Tmpl', 'neutral_HDRI_file_lkdv_Tmpl']

        all_textureNodes = cmds.ls(type='file')

        for file_texture in all_textureNodes:
            if file_texture not in TT_textures:#skip TT Texture files            
                texturePaths[file_texture] = cmds.getAttr(file_texture + '.fileTextureName')

        return texturePaths
    
    def texturesInCurrentJob_QC(self, refresh = False):
        """
        This function checks if all the textures that are connected to the shaders are published

        Args:
            refresh : boolean value to refresh the dictionaries
        Returns:
            incorrectJobTextures : a list containing all the textures that are not in the current job
        """    
        print("...Current Job Textures QC started...")

        #update dictionaries if refresh is True
        if refresh:
            self.updateDictionaries()
            self.ui.lb_errorMessage.setText("Updated Texture in Current Job QC ") #update label
        else:
            pass

        job = self.currentJob

        #empty list to collect incorrect Job textures
        self.incorrectJobTextures = []


        if self.texturePaths:
            total_steps = len(self.texturePaths.keys()) #total steps for calculating percentage
            i = 0 #counter variable for keeping track of iterations
            for tex,paths in self.texturePaths.items():
                if not job in paths: #if job in is not in the path's string
                    self.incorrectJobTextures.append(tex)
                
                #update progress bar
                i=i+1 #add the step counter
                progress_value = int((float(i) / total_steps) * 100)
                self.ui.pBar_currentJob.setValue(progress_value)#set the value

            if self.incorrectJobTextures:
                print("Textures that are not from the current job found :")
                print(self.incorrectJobTextures)
            else:
                print("All Textures in the scene are from Current job("+job+")")
        else:
            self.ui.pBar_currentJob.setValue(100)#set the value for progressbar
            print("No Textures to check for Current job")
        
        #setting the icon in UI
        if self.incorrectJobTextures:
            self.setStatusRed(self.ui.lb_statusCurrentJob,self.ui.btn_selectCurrentJob) #set the icon to red and enable select
        else:
            self.setStatusGreen(self.ui.lb_statusCurrentJob,self.ui.btn_selectCurrentJob) #set the icon to green and disable select

        #populate the error widget with the text on ui and return values
        if refresh:
            self.populateErrorWidget(self.ui.lb_labelCurrentJob.text(), returnVal1 = self.incorrectJobTextures,update=True) 
        else:
            self.populateErrorWidget(self.ui.lb_labelCurrentJob.text(), returnVal1 = self.incorrectJobTextures) 

        #enabling the refresh button
        self.ui.btn_refreshCurrentJob.setEnabled(True)

        return self.incorrectJobTextures

    def publishedTextures_QC(self, refresh = False) : 
        """
        This function checks if all the textures that are connected to the shaders are published
        
        Args:
            refresh : boolean value to refresh the dictionaries 
        Returns:
            unpublishedTextures : a list of all the textures that are not published 
        """

        print("...Published Textures QC started...")

        #update dictionaries if refresh is True
        if refresh:
            self.updateDictionaries()
            self.ui.lb_errorMessage.setText("Updated Published Textures QC ")#update label
        else:
            pass

        #empty list to collect the unpublished Textures
        self.unpublishedTextures = []
        if self.texturePaths:
            total_steps = len(self.texturePaths.keys()) #total steps for calculating percentage
            i = 0 #counter variable for keeping track of iterations
            for tex,path in self.texturePaths.items():
                if not ("release") in path:
                    self.unpublishedTextures.append(tex)
                
                #update progress bar
                i=i+1 #add the step counter
                progress_value = int((float(i) / total_steps) * 100)
                self.ui.pBar_publishedTextures.setValue(progress_value)#set the value
                
            if self.unpublishedTextures:
                print("Unpublished textures found :")
                print(self.unpublishedTextures)
            else:
                print("All Textures in the scene are Published textures")
        else:
            print("No Textures to check for publish state")
            self.ui.pBar_publishedTextures.setValue(100)#set the value for progressbar

        #setting the icon in UI
        if self.unpublishedTextures:
            self.setStatusRed(self.ui.lb_statusPublishedTextures,self.ui.btn_selectPublishedTextures) #set the icon to red and enable select
        else:
            self.setStatusGreen(self.ui.lb_statusPublishedTextures,self.ui.btn_selectPublishedTextures) #set the icon to green and disable select    
        
        #populate the error widget with the text on ui and return values
        if refresh:
            self.populateErrorWidget(self.ui.lb_labelPublishedTextures.text(), returnVal1 = self.unpublishedTextures,update=True) 
        else:
            self.populateErrorWidget(self.ui.lb_labelPublishedTextures.text(), returnVal1 = self.unpublishedTextures) 

        #enabling the refresh button
        self.ui.btn_refreshPublishedTextures.setEnabled(True)

        return self.unpublishedTextures
    
    def duplicateTextures_QC(self, refresh = False):
        """
        This function checks if there are any texture duplicates in the scene
        
        Args:
            refresh : boolean value to refresh the dictionaries
        Returns:
            duplicateTextures : a list of all the textures that are duplicated 
        """
        print("...Duplicate Textures QC started...")
        #update dictionaries if refresh is True
        if refresh:
            self.updateDictionaries()
            self.ui.lb_errorMessage.setText("Updated Duplicated Textures QC ") #update label
        else:
            pass

        #empty list to collect the unpublished Textures
        duplicateTexturePaths = []
        self.duplicateTextures = []

        if self.texturePaths:
            allPaths = list(self.texturePaths.values())

            occurences = {}

            for path in allPaths:
                if path in occurences:
                    occurences[path] +=1
                else:
                    occurences[path] = 1
            
            for path,count in occurences.items():
                if count>1:
                    duplicateTexturePaths.append(path)
            
            total_steps = len(self.texturePaths.keys()) #total steps for calculating percentage
            i = 0 #counter variable for keeping track of iterations
            for tex,path in self.texturePaths.items():
                if path in duplicateTexturePaths:
                    self.duplicateTextures.append(tex)

                #update progress bar
                i=i+1 #add the step counter
                progress_value = int((float(i) / total_steps) * 100)
                self.ui.pBar_duplicateTextures.setValue(progress_value)#set the value

            if self.duplicateTextures:
                print("Duplicate textures found :")
                print(self.duplicateTextures)
            else:
                print("No multiple instances of Textures present in the scene")

        else:
            print("No Textures in the scene to check Duplicates")
            self.ui.pBar_duplicateTextures.setValue(100)#set the value for progress bar
        
        #setting the icon in UI
        if self.duplicateTextures:
            self.setStatusRed(self.ui.lb_statusDuplicateTextures,self.ui.btn_selectDuplicateTextures) #set the icon to red and enable select
        else:
            self.setStatusGreen(self.ui.lb_statusDuplicateTextures,self.ui.btn_selectDuplicateTextures) #set the icon to green and disable select    
        
        #populate the error widget with the text on ui and return values
        if refresh:
            self.populateErrorWidget(self.ui.lb_labelDuplicateTextures.text(), returnVal1 = self.duplicateTextures,update=True) 
        else:
            self.populateErrorWidget(self.ui.lb_labelDuplicateTextures.text(), returnVal1 = self.duplicateTextures) 

        #enabling the refresh button
        self.ui.btn_refreshDuplicateTextures.setEnabled(True)

        return self.duplicateTextures

    def selectNodes(self,list1 = [],list2 = []):
        """
        This function selects all the nodes that passed as list arguments

        Args:
            None
        Returns:
            None
        """

        if list2: #if there is a second arg
            nodes_to_select = list1 + list2
        else: #else takes only arg1
            nodes_to_select = list1 

        if not nodes_to_select: #if nothing present
            print("No Incorrect Nodes found! Try refreshing the function")
            return 
        cmds.select(cl=True) #clear selection

        #iterate through the selections and select each nodes 
        for node in nodes_to_select:
            cmds.select(node,add=True,hi=True,ne=True) 

    def populateErrorWidget(self,funcName,returnVal1 = [],returnVal2 = [],update = False):
        """ 
        This function populates the Error widget based on the passed argument

        Args:
            funcName: name of the function to populate
            returnVal1: passed list #1
            returnVal2: passed list #2
            update : a boolean to determine if an existing widget has to be updated or not
        Returns:
            None
        """

        if update: #if the function is called with update
            for x in range(self.ui.vlo_errorLists.count()): #iterate through the list
                layout = self.ui.vlo_errorLists.itemAt(x) #save the layout at that specific position
                
                for i in range(layout.count()):
                    item = layout.itemAt(i) #save the item
                    widget = item.widget() #save the widget
                    #find the widget with our funcname label and the list below it
                    if isinstance(widget,QtWidgets.QLabel) and funcName in widget.text():
                        current_index = x #save the position index
                        layout.removeWidget(widget)
                        widget.setParent(None)
                        widget.deleteLater() #remove the label

                        #find if next item is a list widget
                        next_item = layout.itemAt(i)
                        if next_item: 
                            next_widget = next_item.widget() #store the next widget
                            if isinstance(next_widget,QtWidgets.QListWidget): #if its a list
                                layout.removeWidget(next_widget) #remove the widget
                                next_widget.setParent(None)
                                next_widget.deleteLater() #remove the list as well
                        break

            #update new label and list widget in the same position
            if returnVal1 or returnVal2: #if there are any passed values that can be displayed
                allItems = returnVal1+returnVal2

                #add a label on top
                numberOfErrors = len(allItems)
                if numberOfErrors <=1 :
                    errorTxt = " Error:"
                else:
                    errorTxt = " Errors:"
                
                #make a parent error layout
                errorLayout = QtWidgets.QVBoxLayout()
                errorLayout.setSpacing(0)

                #function label properties
                funcLabel = QtWidgets.QLabel(funcName+" QC Found " + str(numberOfErrors) + errorTxt)
                funcLabel.setStyleSheet("background-color: rgb(75, 75, 75)")
                funcLabel.adjustSize()
                funcLabel.setFixedHeight(18)

                #add itemsList ListWidget below it
                itemsList = QtWidgets.QListWidget()
                itemsList.setStyleSheet("background-color: rgb(90, 90, 90)")
                itemsList.itemDoubleClicked.connect(lambda val: self.selectItem(val,itemsList)) #set its connections

                #add the layouts
                errorLayout.addWidget(funcLabel)
                errorLayout.addWidget(itemsList)
                self.ui.vlo_errorLists.insertLayout(current_index,errorLayout) #insert the new layout in the same position

                #populate the listWidget
                for item in allItems:
                    itemsList.addItem(item)
                
                #itemsList properties to set fixed height based on number of items
                item_height = itemsList.sizeHintForRow(0)
                item_count = itemsList.count()
                total_height = item_height * item_count + 5
                itemsList.setFixedHeight(total_height)
                
            if not returnVal1 and not returnVal2: #if there are no passed values to display
                return


        else: #if not called with update

            if returnVal1 or returnVal2: #if there are any passed values that can be displayed
                self.ui.vlo_errorLists.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
                allItems = returnVal1+returnVal2

                #add a label on top
                numberOfErrors = len(allItems)
                if numberOfErrors <=1 :
                    errorTxt = " Error:"
                else:
                    errorTxt = " Errors:"

                #make a parent error layout
                errorLayout = QtWidgets.QVBoxLayout()
                errorLayout.setSpacing(0)

                #function label properties
                funcLabel = QtWidgets.QLabel(funcName+" QC Found " + str(numberOfErrors) + errorTxt)
                funcLabel.setStyleSheet("background-color: rgb(75, 75, 75)")
                funcLabel.adjustSize()
                funcLabel.setFixedHeight(18)

                #add itemsList ListWidget below it
                itemsList = QtWidgets.QListWidget()
                itemsList.setStyleSheet("background-color: rgb(90, 90, 90)")
                itemsList.itemDoubleClicked.connect(lambda val: self.selectItem(val,itemsList))

                #add to layout
                errorLayout.addWidget(funcLabel)
                errorLayout.addWidget(itemsList)
                self.ui.vlo_errorLists.addLayout(errorLayout)

                #populate the listWidget
                for item in allItems:
                    itemsList.addItem(item)
                
                #itemsList properties to set fixed height based on number of items
                item_height = itemsList.sizeHintForRow(0)
                item_count = itemsList.count()
                total_height = item_height * item_count + 5
                itemsList.setFixedHeight(total_height)

            if not returnVal1 and not returnVal2: #if there are no passed values to display
                return
    
    def selectItem(self,item,itemsList):
        """ 
        This function selects the specific item that is clicked on the list widget

        Args:
            None
        Returns:
            None
        """
        cmds.select(cl=True) #clear selection

        #select the specific item
        cmds.select(item.text(),hi=True,ne=True)

    def clearErrorWidget(self):
        """
        This function clears the Error widget completely

        Args:
            None
        Returns:
            None
        """   
        #check if there are any error widget inside
        if self.ui.vlo_errorLists.count():   
            while self.ui.vlo_errorLists.count():#when the layout is not empty
                layout = self.ui.vlo_errorLists.takeAt(0) #take the item at 0
                while layout.count(): #while the inner layout is not empty
                    childLayout=layout.takeAt(0) #take the child item at 0
                    if childLayout.widget(): #if there is a widget
                        #remove the widget
                        widget = childLayout.widget() 
                        layout.removeWidget(widget)
                        widget.setParent(None)
                        widget.deleteLater()
        else:
            pass

if __name__ == "__main__":

    if cmds.ls(sl=True): #check for selection before starting the tool
        var = cmds.ls(sl=True) #store the selection
        if cmds.nodeType(var)== "transform" and not cmds.listRelatives(var,shapes=True): #check if selection is a group
            selectedGrp = var[0] #store the first item in list

            #make an instance with the selected selection
            obj = MaterialQC(selection = selectedGrp)
            obj.show()
        else: 
            #if selected is not a group
            cmds.select(cl=True) #clear selection

            #make an instance with the selected selection
            obj = MaterialQC() 
            obj.show()
    else: 
        #if nothing is before starting the tool

        #make an instance with the selected selection
        obj = MaterialQC() 
        obj.show()