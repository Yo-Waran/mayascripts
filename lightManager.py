#importing PyMel

import sys
sys.path.append("/Users/ramyogeshwaran/Library/Preferences/Autodesk/maya/pymel-1.4.1b1")

from glob import glob
import pymel.core as pm

from PySide6 import QtWidgets, QtCore,QtGui
#from PySide2 import QtWidgets, QtCore,QtGui

from shiboken6 import wrapInstance
#from shiboken2 import wrapInstance

from functools import partial

import logging #log module

import maya._OpenMayaUI as omui

import pprint

import os

import json #reading and writing data

import time

logging.basicConfig() #sets up basic configuration for our logging
logger = logging.getLogger('LightingManager') #storing Lighting Manager logger 

logger.setLevel(logging.INFO) #log out every logger till DEBUG Logger


def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow() #returns the memory address of main window
    ptr = wrapInstance(int(win),QtWidgets.QMainWindow) #convert memory address to a long integer
    return ptr

def getDock(name = "LightingManagerDock"):
    deleteDock(name) #check if exists already and delete accordingly
    ctrl = pm.workspaceControl(name , dockToMainWindow = ('right',0),label = "Lighting Manager") #docks the window in the right at first
    qtctrl = omui.MQtUtil_findControl(ctrl) #returns the memory address of our new dock
    ptr = wrapInstance(int(qtctrl),QtWidgets.QWidget) #convert memory address to a long integer
    return ptr

def deleteDock(name = "LightingManagerDock"):
    if pm.workspaceControl(name,query = True, exists = True):
        pm.deleteUI(name)
    
def convert_sign(number):
    return -number



def createMeshLight():
    global selectedMesh 

    if pm.ls(sl=True):#if something selected
        #check if there is a mesh
        for i in pm.ls(sl=True,dag = True):
            if pm.objectType(i)== "mesh":
                selectedMesh = i.getTransform()
        if not selectedMesh:
            raise pm.displayError("No meshes inside the selected mesh")
    else:
        raise pm.displayError("Nothing is selected to convert as Mesh Light")
    light = pm.shadingNode('aiMeshLight',asLight= True)#create the light
    pm.parent(light,selectedMesh) #parent it
    return(light)


class LightManager(QtWidgets.QWidget):

    lightTypes = {
        "Ambient Light":pm.ambientLight,#function to be called
        "Point Light" : pm.pointLight, 
        "Spot Light" : pm.spotLight ,
        "Directional Light" : pm.directionalLight,
        "Area Light" : partial(pm.shadingNode, 'areaLight', asLight = True), #store the function name and arguments together using partial
        "Volume Light" : partial(pm.shadingNode, 'volumeLight',asLight = True) ,
        "aiArea Light" : partial(pm.shadingNode,'aiAreaLight', asLight=True),
        "aiSkyDome Light": partial(pm.shadingNode,'aiSkyDomeLight', asLight=True),
        "aiMesh Light" : createMeshLight,
        "aiPhotometric Light": partial(pm.shadingNode,'aiPhotometricLight', asLight=True),
    }
    

    def __init__(self,dockable = True):

        if dockable:
            parent = getDock() #parent is set to the empty dock
        else:

            deleteDock() #delete the empty dock
            try:
                pm.deleteUI('LightingManager') #if it exists delete it
            except:
                logger.debug("No Previous UI Exists")
                
            parent = QtWidgets.QDialog(parent=getMayaMainWindow()) #creates a new QDialog on the main window
            parent.setObjectName('LightingManager') #set the name for the dialog
            parent.setWindowTitle('Lighting Manager') #set the title 
            layout = QtWidgets.QVBoxLayout(parent) #add a layout to it


        super(LightManager,self).__init__(parent=parent) #call parent init of QDialog

        self.lightCount = 0 #to keep track of number of widgets
        logger.debug("Initialzing Light Manager Class") #log statements for debugging purpose
        self.buildUI()
        logger.debug("Running Light Manager build UI")
        self.populate()#populate using existing lights
        logger.debug("Populating Light Manager with lights on scene")

        self.parent().layout().addWidget(self)  #adds our manager to the parent layout
        if not dockable:
            parent.show() #show our parent 
        self.directory = None
        self.globalIntWidget = QtWidgets.QWidget()


    def populate(self):
        
        logger.debug("Populating Light Manager with lights on scene again")

        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget
        
        #clearing the scroll layout first!
        for widget in lightWidgets:
                widget.setVisible(False) #hide them
                widget.deleteLightWidget() #delete the light
        try:
            self.globalIntScale.destroy()
        except AttributeError:
            pass
        

        for light in pm.ls(type=['ambientLight','areaLight','spotLight','pointLight','directionalLight','volumeLight','aiAreaLight','aiSkyDomeLight','aiPhotometricLight','aiMeshLight']): #iterate through all lights
            self.addLight(light) #then we call the add light function for each lights present from scratch
        
    
    def buildUI(self):
        main_layout = QtWidgets.QGridLayout(self) #Grid layout for the main
        #first Label
        label1 = QtWidgets.QLabel("Create Light :")
        main_layout.addWidget(label1,0,0)

        #combobox
        self.lightTypeCB = ComboBoxWithSeparator() #custom combobox for storing the light types
        #populating combobox
        for lightType in self.lightTypes: #iterate through dict
            self.lightTypeCB.addItem(lightType) #add items for each key
        self.lightTypeCB.model().sort(0) #sort it
        self.lightTypeCB.addMayaSeparator(0) #add a maya Seperator
        self.lightTypeCB.addArnoldSeparator(7) #add an arnold seperator at 5
        main_layout.addWidget(self.lightTypeCB,0,1)  #add it to main layout at 0,0 = (x,y) position
        
        #createBtn
        createBtn = QtWidgets.QPushButton("Create") #button for creating light
        main_layout.addWidget(createBtn,0,2) #add the button at 0,1 position in the grid
        #connect the button
        createBtn.clicked.connect(self.createLight) 


        #scroll widget to scroll through lights created
        scrollWidget = QtWidgets.QWidget() #new empty widget
        scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum) #doesnt stretch the scroll area
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget) #add vertical layout to it

        scrollArea = QtWidgets.QScrollArea() #add a scroll area
        scrollArea.setWidgetResizable(True) #make it resizable
        scrollArea.setWidget(scrollWidget) #add the scrollwidget inside the scroll area
        main_layout.addWidget(scrollArea,1,0,1,3) #1 = second row, 0 = 1st column, 1=  size of row , 2 = size of columns

        #save btn
        saveBtn = QtWidgets.QPushButton("Save")
        saveBtn.clicked.connect(self.saveLight) #connect
        main_layout.addWidget(saveBtn,2,0)  #add it to main layout

        #import btn
        importBtn = QtWidgets.QPushButton("Import")
        importBtn.clicked.connect(self.importLight) #connect
        main_layout.addWidget(importBtn,2,1) #add it to main layout

        #refresh Btn
        refreshBtn = QtWidgets.QPushButton('Refresh')
        refreshBtn.clicked.connect(self.populate) #call populate again
        main_layout.addWidget(refreshBtn,2,2) #add the button at 3rd row , 2nd column
    


    def createLight(self,selLightType = None,add = True):
        if not selLightType:
            selLightType = self.lightTypeCB.currentText() #get the selected text in combo box

        func= self.lightTypes[selLightType] #get the function value from key

        light = func() #call the function to create the light

        if add:
            self.addLight(light) #add the light to the scroll area
        
        return light

    def addLight(self,light): #function to add the light widget
        self.lightCount+=1       

        if self.lightCount == 1:
            #add a new widget
            self.globalIntWidget = QtWidgets.QWidget()
            globalLayout = QtWidgets.QGridLayout(self.globalIntWidget)

            label2 = QtWidgets.QLabel("Global Modifier")
            label2.setStyleSheet("font-weight: bold")
            self.globalIntScale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.valueOfIntScale = QtWidgets.QLabel("0")

            self.intLabel = QtWidgets.QLabel("Global Intensity")

            #arnold sliders
            self.expLabel = QtWidgets.QLabel("Global Exposure")
            self.globalExpScale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.valueOfExpScale = QtWidgets.QLabel("0")
            self.sampLabel = QtWidgets.QLabel("Global Samples")
            self.globalSampScale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.valueOfSampScale = QtWidgets.QLabel("0")
            self.volSampLabel = QtWidgets.QLabel("Global Volume Samples")
            self.globalVolSampScale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.valueOfVolSampScale = QtWidgets.QLabel("0")

            #setminimum width for labels
            self.valueOfIntScale.setMinimumWidth(20)
            self.valueOfExpScale.setMinimumWidth(20)
            self.valueOfSampScale.setMinimumWidth(20)
            self.valueOfVolSampScale.setMinimumWidth(20)

            #properties for int slider
            self.globalIntScale.setMinimum(0)
            self.globalIntScale.setMaximum(100)
            self.globalIntScale.setValue(50)
            self.globalIntScale.valueChanged.connect(self.glob_val_int_change)
            self.globalIntScale.sliderReleased.connect(self.glob_val_int_reset)

            #properties for exp slider
            self.globalExpScale.setMinimum(0)
            self.globalExpScale.setMaximum(100)
            self.globalExpScale.setValue(50)
            self.globalExpScale.valueChanged.connect(self.glob_val_exp_change)
            self.globalExpScale.sliderReleased.connect(self.glob_val_exp_reset)

            #properties for samp slider
            self.globalSampScale.setMinimum(0)
            self.globalSampScale.setMaximum(10)
            self.globalSampScale.setValue(5)
            self.globalSampScale.valueChanged.connect(self.glob_val_samp_change)
            self.globalSampScale.sliderReleased.connect(self.glob_val_samp_reset)

            #properties for vol samp slider
            self.globalVolSampScale.setMinimum(0)
            self.globalVolSampScale.setMaximum(10)
            self.globalVolSampScale.setValue(5)
            self.globalVolSampScale.valueChanged.connect(self.glob_val_vol_change)
            self.globalVolSampScale.sliderReleased.connect(self.glob_val_vol_reset)

            #add to layout
            globalLayout.addWidget(label2,0,0)
            globalLayout.addWidget(self.intLabel,1,0)
            globalLayout.addWidget(self.globalIntScale,1,1)
            globalLayout.addWidget(self.valueOfIntScale,1,2)

            #disable and add the rest 
            self.expLabel.setDisabled(1)
            self.sampLabel.setDisabled(1)
            self.volSampLabel.setDisabled(1)
            self.globalExpScale.setDisabled(1)
            self.globalSampScale.setDisabled(1)
            self.globalVolSampScale.setDisabled(1)

            globalLayout.addWidget(self.expLabel,2,0)
            globalLayout.addWidget(self.globalExpScale,2,1)
            globalLayout.addWidget(self.valueOfExpScale,2,2)
            globalLayout.addWidget(self.sampLabel,3,0)
            globalLayout.addWidget(self.globalSampScale,3,1)
            globalLayout.addWidget(self.valueOfSampScale,3,2)
            globalLayout.addWidget(self.volSampLabel,4,0)
            globalLayout.addWidget(self.globalVolSampScale,4,1)
            globalLayout.addWidget(self.valueOfVolSampScale,4,2)

            self.scrollLayout.addWidget(self.globalIntWidget)


        #add the light to scroll area
        widget = LightWidget(light) #make a new Instance of lightWidget .
        self.scrollLayout.insertWidget(1,widget)  #add that check box to scroll layout 
        widget.onSolo.connect(self.isolate) #call a function when that signal is emitted
        widget.onDelete.connect(self.deleted) #call a function when widget is deleted
        widget.onAltClick.connect(self.isolateVis) #call a function for alt click
        widget.onShiftClick.connect(self.allVis) #call a function for shift click

        if widget.isArnoldLight() == 1: #if widget is an arnold
            self.arnoldParams()

    def glob_val_exp_change(self):
        val = self.globalExpScale.value() #get the value
        newVal = convert_sign(50-val) #inverse it
        self.valueOfExpScale.setText(str(newVal)) #set the label 



    def glob_val_exp_reset(self):
        #store the last point
        val = self.globalExpScale.value() #get the value
        self.addVal = convert_sign(50-val) #inverse it

        #reset it
        self.globalExpScale.setValue(50) #reset slider
        self.valueOfExpScale.setText("0") #reset the label

        #do the math
        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget

        #change the sliders
        for widget in lightWidgets:
            widget.globExpChange(self.addVal)


    def glob_val_samp_change(self):
        val = self.globalSampScale.value() #get the value
        newVal = convert_sign(5-val) #inverse it
        self.valueOfSampScale.setText(str(newVal)) #set the label 

    def glob_val_samp_reset(self):
        #store the last point
        val = self.globalSampScale.value() #get the value
        self.addVal = convert_sign(5-val) #inverse it

        #reset it
        self.globalSampScale.setValue(5) #reset slider
        self.valueOfSampScale.setText("0") #reset the label

        #do the math
        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget

        #change the sliders
        for widget in lightWidgets:
            widget.globSampChange(self.addVal)

    def glob_val_vol_change(self):
        val = self.globalVolSampScale.value() #get the value
        newVal = convert_sign(5-val) #inverse it
        self.valueOfVolSampScale.setText(str(newVal)) #set the label 

    def glob_val_vol_reset(self):
        #store the last point
        val = self.globalVolSampScale.value() #get the value
        self.addVal = convert_sign(5-val) #inverse it

        #reset it
        self.globalVolSampScale.setValue(5) #reset slider
        self.valueOfVolSampScale.setText("0") #reset the label

        #do the math
        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget

        #change the sliders
        for widget in lightWidgets:
            widget.globVolSampChange(self.addVal)

    
    def arnoldParams(self):
        self.expLabel.setEnabled(1)
        self.sampLabel.setEnabled(1)
        self.volSampLabel.setEnabled(1)
        self.globalExpScale.setEnabled(1)
        self.globalSampScale.setEnabled(1)
        self.globalVolSampScale.setEnabled(1)


    def allVis(self,value):
        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget
        for widget in lightWidgets: #iterate through all lightWidgets
            widget.disableLight(not value) #turn on the light

    def isolateVis(self,value):
        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget
        for widget in lightWidgets: #iterate through all lightWidgets
            if widget == self.sender(): #find the one that is emitting signal
                widget.disableLight(not value) #enable the light
            else:
                widget.disableLight(value)#disable
    
    def isolate(self,value):
        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget
        for widget in lightWidgets: #iterate through all lightWidgets
            if widget != self.sender(): #find the ones not emitting signal
                widget.setEnabled(not value)  #greys out other lights               
                widget.disableLight(value) #new function that disables the light
    
    
    def deleted(self):
        self.lightCount-=1
        if self.lightCount == 0:
            #delete the new widget
            self.globalIntWidget.setParent(None) #remove from the layout
            self.globalIntWidget.setVisible(False) #make it hidden
            self.globalIntWidget.deleteLater()
    
    def glob_val_int_reset(self):
        #store the last point
        val = self.globalIntScale.value() #get the value
        self.addVal = convert_sign(50-val) #inverse it

        #reset it
        self.globalIntScale.setValue(50) #reset slider
        self.valueOfIntScale.setText("0") #reset the label

        #do the math
        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget

        #change the sliders
        for widget in lightWidgets:
            widget.globIntChange(self.addVal)

        
    def glob_val_int_change(self):
        val = self.globalIntScale.value() #get the value
        newVal = convert_sign(50-val) #inverse it
        self.valueOfIntScale.setText(str(newVal)) #set the label 


    def saveLight(self):
        properties = {} #empty dict to collect data
        for lightWidget in self.findChildren(LightWidget): #iterate through all light widgets
            light = lightWidget.light #get the actual light
            if light.nodeType()=='aiMeshLight':
                print("skipping Mesh Light")
                continue
            transform = light.getTransform() #get transform node of that light

            #writing data to dict
            properties[str(transform)] = {
                'translate' : list(transform.translate.get()),
                'rotation' : list(transform.rotate.get()),
                'lightType': pm.objectType(light),
                'intensity' : light.intensity.get(),
                'color': light.color.get()
            }
        
        def_directory = os.path.join(pm.internalVar(userAppDir = True),'lightManager') #add lightManager folder to the user directory
        if not os.path.exists(def_directory): #if doesnt exist
            os.mkdir(def_directory) #make it

        self.directory = QtWidgets.QFileDialog.getExistingDirectory(self,"Where do you wanna save?", )
        lightFile = os.path.join(self.directory,'lightFile_{0}.json'.format(time.strftime('%d%m%H%M%S'))) #make a json file path based on the current day %d month %m and year %y

        with open(lightFile,'w') as f: #open the file
            json.dump(properties,f,indent = 4) #write properties dict on the file and indent by 4 spaces
        
        print('Saving File to {0}'.format(lightFile))
        logger.info('Saving File to {0}'.format(lightFile))

    def importLight(self):
        def_directory = os.path.join(pm.internalVar(userAppDir = True),'lightManager') #add lightManager folder to the user directory
        if not self.directory:
            self.directory = def_directory
        fileName = QtWidgets.QFileDialog.getOpenFileName(self,"Select your json",self.directory) #file dialog for user to choose a file
        with open (fileName[0],'r') as f:
            properties = json.load(f) #save the json dict from the file into a variable

        #recreating lights
        for light,info in properties.items():#iterating through the data
            lt = info.get('lightType')
            for lightType in self.lightTypes: #iterate through our lightTypes dict
                #check if the lightType in our dict and the data's type match
                if lt == ('{0}Light'.format(lightType.split()[0].lower())): #if they match
                    break
                elif lt == ('{0}Light'.format(lightType.split()[0])): #if ai lights match
                    break

            else: #if not thing found from our LightTypes dict
                logger.info("cannot find a corresponding light type for {0}:{1}".format(light,lt))
                continue

            light = self.createLight(selLightType = lightType) #create the light with our function
            light.intensity.set(info.get('intensity'))#set the intensity
            light.color.set(info.get('color'))#set color

            transform = light.getTransform() #store the transform node

            #set transforms
            transform.translate.set(info.get('translate'))
            transform.rotate.set(info.get('rotation')) 
            print('created {0}'.format(light))
        #refresh ui
        self.populate()

            

class LightWidget(QtWidgets.QWidget):

    onSolo = QtCore.Signal(bool) #makes a new signal 
    onDelete = QtCore.Signal(bool) #make a signal for deletion
    onAltClick = QtCore.Signal(bool) #make a signal for alt click
    onShiftClick = QtCore.Signal(bool)  #make a signal for shift click

    def __init__(self,light):
        super(LightWidget,self).__init__() #call init of QWidget
        if isinstance(light , str): #if light is a string
            light = pm.PyNode(light) #convert it to pyNode so that we can work with PyMel
        
        #check if its a transform
        if isinstance(light,pm.nodetypes.Transform):
            light = light.getShape()

        self.light = light #save the light
        self.buildUI() #call function to build UI

    def buildUI(self):

        layout = QtWidgets.QGridLayout(self) #add a layout

        #node button
        self.name = QtWidgets.QPushButton(str(self.light.getTransform()))
        self.name.clicked.connect(partial(pm.select,str(self.light.getTransform())))
        layout.addWidget(self.name,0,0)

        #node type
        self.type = QtWidgets.QLabel("("+pm.objectType(self.light)+")")
        self.type.setStyleSheet("color:rgba(255,255,255,0.3)")
        layout.addWidget(self.type,0,1)


        #CHECKBOX
        self.visBox = CustomClickCheckBox("Visible") #get the transform name and save it as a checkbox
        self.visBox.setChecked(self.light.visibility.get()) #get visibility attr . same as cmds.getAttr(self.light.visibilty)
        #connect the checkbox
        self.visBox.clicked.connect(lambda val : self.light.getTransform().visibility.set(val)) #store the toggle value in val and set it as the visibility for the light
        self.visBox.altClicked.connect(lambda val : self.onAltClick.emit(val))
        layout.addWidget(self.visBox,0,2)
        self.visBox.shifClicked.connect(lambda val: self.onShiftClick.emit(val))

        #SOLOBTN
        soloBtn = QtWidgets.QPushButton('Solo') #create a btn
        soloBtn.setCheckable(True) #makes it work like a switch  
        soloBtn.toggled.connect(lambda val: self.onSolo.emit(val)) #sets a signal of True or false based on the toggle
        soloBtn.setStyleSheet('background-color:rgba({0},{1},{2},0.5)'.format(0,100,200)) #set color
        soloBtn.setMaximumSize(30,30)
        layout.addWidget(soloBtn,0,3) #add it to the layout

        #DELETEBTN
        deleteBtn = QtWidgets.QPushButton("X")
        deleteBtn.clicked.connect(lambda val : self.onDelete.emit(val))
        deleteBtn.clicked.connect(self.deleteLight) #function to delete the widget
        deleteBtn.setMaximumWidth(100)#set maximum
        deleteBtn.setStyleSheet('background-color:rgba({0},{1},{2},0.5)'.format(150,0,0)) #set color
        layout.addWidget(deleteBtn,0,4) #add it at 3rd column


        #INTENSITY_SLIDER
        intensityLabel = QtWidgets.QLabel("Intensity")
        self.intensity = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.intensity.setMinimum(1) #set min
        self.intensity.setMaximum(1000) #set max

        self.intensity.setValue(self.light.intensity.get()) #get val from intensity of light
        self.intensity.valueChanged.connect(lambda val : self.light.intensity.set(val)) #connect the slider and intensity
        layout.addWidget(intensityLabel,1,0)
        layout.addWidget(self.intensity,1,1,1,3) #1 - 2nd row , 0 - 1st column , 1- 1 row of size, 2-  column of size

        #COLORBRN
        self.colorBtn = QtWidgets.QPushButton()
        self.colorBtn.setMaximumWidth(20) #set max w
        self.colorBtn.setMaximumHeight(20) #set max h
        self.setButtonColor() #new func to set the button color
        self.colorBtn.clicked.connect(self.setColor) #fnew unction to set the color of light
        layout.addWidget(self.colorBtn,1,4) #add to layout

        if self.isArnoldLight()==1:

            #mesh light conditions    
            if self.light.nodeType()=='aiMeshLight': #check if its a mesh light
                connections = self.light.inMesh.listConnections(plugs=True) #if mesh light has connections
                if connections:
                    pass 
                else: #if no connections for mesh light
                    pm.connectAttr(selectedMesh.outMesh, self.light.inMesh) #connect the attributes with selected mesh
                    selectedMesh.getShape().visibility.set(0) #set its visibilty
                expVariable = self.light.aiExposure
            else: #if not mesh light pass
                expVariable = self.light.exposure
            
            #EXPOSURE SLIDER
            exposureLabel = QtWidgets.QLabel("Exposure")
            self.exposure = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.exposure.setMinimum(1)
            self.exposure.setMaximum(1000)

            #connect
            self.exposure.setValue(expVariable.get()) #get val from exposure
            self.exposure.valueChanged.connect(lambda val : expVariable.set(val))

            #add it
            layout.addWidget(exposureLabel,2,0)
            layout.addWidget(self.exposure,2,1,1,4)

            #SAMPLES SLIDER
            samplesLabel = QtWidgets.QLabel("Samples")
            self.samples = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.samples.setMinimum(1)
            self.samples.setMaximum(10)
            
            #connect
            self.samples.setValue(self.light.aiSamples.get())
            self.samples.valueChanged.connect(lambda val: self.light.aiSamples.set(val))

            #add it
            layout.addWidget(samplesLabel,3,0)
            layout.addWidget(self.samples,3,1,1,4)

            #VOLUMESAMPLES SLIDER
            volumesLabel = QtWidgets.QLabel("Volume Samples")
            self.volumes = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.volumes.setMinimum(1)
            self.volumes.setMaximum(10)

            #connect
            self.volumes.setValue(self.light.aiVolumeSamples.get())
            self.volumes.valueChanged.connect(lambda val: self.light.aiVolumeSamples.set(val))

            #add it
            layout.addWidget(volumesLabel,4,0)
            layout.addWidget(self.volumes,4,1,1,4)

        else:

            pass
        

    
    def setButtonColor(self,color = None):

        if not color:
            color = self.light.color.get() #get the color from the light

        assert len(color) == 3, "You must provide a list of 3 Colors"

        #convert float value of rgb to 0-255 integer
        r,g,b = [c*255 for c in color]#get correct rgb from float values
        self.colorBtn.setStyleSheet('background-color:rgba({0},{1},{2},1.0)'.format(r,g,b)) #set the color using QSS (similar to CSS)

    def isArnoldLight(self):
        if self.light.nodeType().startswith("ai"):
            return True
        else :
            return False

    def setColor(self):
        lightColor = self.light.color.get() #get color from light

        #open maya color editor
        color = pm.colorEditor(rgbValue = lightColor) #open the color chart
        
        #convert string
        r,g,b,a = [float(c) for c in color.split()] #split the string at spaces and convert it into float

        color = (r,g,b)
        self.light.color.set(color) #set color of light
        self.setButtonColor() #call previous function to set button color again

    def deleteLight(self):
        self.setParent(None) #remove from the layout
        self.setVisible(False) #make it hidden
        self.deleteLater() #delete the UI as soon as it can

        #delete the actual light from scene
        pm.delete(self.light.getTransform()) #delete the transfrom 

    def deleteLightWidget(self):
        self.setParent(None) #remove from the layout
        self.setVisible(False) #make it hidden
        self.deleteLater() #delete the UI as soon as it can
        self.onDelete.emit(True)


    def disableLight(self,val):   
        self.visBox.setChecked(not val) #pass opposite of what value is!


    def globIntChange(self,value):
        #get the value of the current slider
        oldVal = self.intensity.value()

        #add it to the value
        addedValue = oldVal + value

        #set the slider value again
        self.intensity.setValue(addedValue)

    def globExpChange(self,value):
        if self.isArnoldLight()==1:
            #get the value of current slider
            oldVal = self.exposure.value()

            #add it to the value
            addedValue = oldVal+value

            #set the slider
            self.exposure.setValue(addedValue)
        else:
            pass

    def globSampChange(self,value):
        if self.isArnoldLight()==1:
            #get the value of current slider
            oldVal = self.samples.value()

            #add it to the value
            addedValue = oldVal+value

            #set the slider
            self.samples.setValue(addedValue)
        else:
            pass

    def globVolSampChange(self,value):
        if self.isArnoldLight()==1:    
            #get the value of current slider
            oldVal = self.volumes.value()

            #add it to the value
            addedValue = oldVal+value

            #set the slider
            self.volumes.setValue(addedValue)
        else:
            pass

    

class CustomClickCheckBox(QtWidgets.QCheckBox):

    altClicked = QtCore.Signal(bool)  # Custom signal
    shifClicked  = QtCore.Signal(bool) #custom signal for shift click

    def __init__(self,name):
        super(CustomClickCheckBox,self).__init__() #initalize the Checkbox attribs
        self.setText(name)

    def mousePressEvent(self, event):
        # Check if the Alt key is pressed and the left mouse button is clicked
        if event.modifiers() == QtCore.Qt.AltModifier and event.button() == QtCore.Qt.LeftButton:
            self.altClicked.emit(True)  # Emit the custom signal

        elif event.modifiers() == QtCore.Qt.ShiftModifier and event.button() == QtCore.Qt.LeftButton:
            self.shifClicked.emit(True)
            
        else:
            super(CustomClickCheckBox,self).mousePressEvent(event)  # Call the base class method for normal behavior

class ComboBoxWithSeparator(QtWidgets.QComboBox):

    def __init__(self):
        super(ComboBoxWithSeparator,self).__init__()

    def addArnoldSeparator(self, index):
            #function to add a seperator at the given index
            separator = "***Arnold Lights***"
            self.insertItem(index, separator) #inser the item at that index
            item = self.model().item(index, 0)#store the model
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable) #make it no selectable
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled) #make it not enabled

    def addMayaSeparator(self, index):
            #function to add a seperator at the given index
            separator = "***Maya Lights***"
            self.insertItem(index, separator) #inser the item at that index
            item = self.model().item(index, 0)#store the model
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable) #make it no selectable
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled) #make it not enabled



LightManager() #setting it false
