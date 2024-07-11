#importing PyMel

import sys
sys.path.append("/Users/ramyogeshwaran/Library/Preferences/Autodesk/maya/pymel-1.4.1b1")

import pymel.core as pm

from PySide6 import QtWidgets, QtCore,QtGui

from shiboken6 import wrapInstance

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

#make our code work in other Modules
'''
import Qt
if Qt.__binding__ == 'PySide':
    from shiboken import wrapInstance
    from QtCore import Signal
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from QtCore import pyqtSignal as Signal
else:
    from shiboken2 import wrapInstance
    from QtCore import Signal

'''
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
    
class LightManager(QtWidgets.QWidget):

    lightTypes = {
        "Point Light" : pm.pointLight, #function to be called
        "Spot Light" : pm.spotLight ,
        "Directional Light" : pm.directionalLight,
        "Area Light" : partial(pm.shadingNode, 'areaLight', asLight = True), #store the function name and arguments together using partial
        "Volume Light" : partial(pm.shadingNode, 'volumeLight',asLight = True) 
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

        logger.debug("Initialzing Light Manager Class") #log statements for debugging purpose
        self.buildUI()
        logger.debug("Running Light Manager build UI")
        self.populate()#populate using existing lights
        logger.debug("Populating Light Manager with lights on scene")

        self.parent().layout().addWidget(self)  #adds our manager to the parent layout
        if not dockable:
            parent.show() #show our parent 
        self.directory = None

    def populate(self):

        logger.debug("Populating Light Manager with lights on scene again")
        #clearing the scroll layout first!
        while self.scrollLayout.count(): #while scroll layout can count its children
            widget  = self.scrollLayout.takeAt(0).widget() #get the child at position 0 to get its widget
            if widget:
                widget.setVisible(False) #hide them
                widget.deleteLater() #delete them 

        for light in pm.ls(type=['areaLight','spotLight','pointLight','directionalLight','volumeLight']): #iterate through all lights
            self.addLight(light) #then we call the add light function for each lights present from scratch
            

    def buildUI(self):
        main_layout = QtWidgets.QGridLayout(self) #Grid layout for the main
        #combobox
        self.lightTypeCB = QtWidgets.QComboBox() #combobox for storing the light types

        #populating combobox
        for lightType in self.lightTypes: #iterate through dict
            self.lightTypeCB.addItem(lightType) #add items for each key


        main_layout.addWidget(self.lightTypeCB,0,0,1,2)  #add it to main layout at 0,0 = (x,y) position
        
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
        #add the light to scroll area
        widget = LightWidget(light) #make a new Instance of lightWidget .
        self.scrollLayout.addWidget(widget)  #add that check box to scroll layout 
        widget.onSolo.connect(self.isolate) #call a function when that signal is emitted

    def isolate(self,value):
        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget
        for widget in lightWidgets: #iterate through all lightWidgets
            if widget != self.sender(): #find the ones not emitting signal
                widget.disableLight(value) #new function that disables the light
                widget.setEnabled(not value)  #greys out other lights

    def saveLight(self):
        properties = {} #empty dict to collect data
        for lightWidget in self.findChildren(LightWidget): #iterate through all light widgets
            light = lightWidget.light #get the actual light
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

        #CHECKBOX
        self.name = QtWidgets.QCheckBox(str(self.light.getTransform())) #get the transform name and save it as a checkbox
        self.name.setChecked(self.light.visibility.get()) #get visibility attr . same as cmds.getAttr(self.light.visibilty)
        #connect the checkbox
        self.name.toggled.connect(lambda val : self.light.getTransform().visibility.set(val)) #store the toggle value in val and set it as the visibility for the light
        layout.addWidget(self.name,0,0)

        #SOLOBTN
        soloBtn = QtWidgets.QPushButton('Solo') #create a btn
        soloBtn.setCheckable(True) #makes it work like a switch  
        soloBtn.toggled.connect(lambda val: self.onSolo.emit(val)) #sets a signal of True or false based on the toggle
        soloBtn.setStyleSheet('background-color:rgba({0},{1},{2},1.0)'.format(0,0,255)) #set color
        layout.addWidget(soloBtn,0,1) #add it to the layout

        #DELETEBTN
        deleteBtn = QtWidgets.QPushButton("X")
        deleteBtn.clicked.connect(self.deleteLight) #function to delete the widget
        deleteBtn.setMaximumWidth(100)#set maximum
        deleteBtn.setStyleSheet('background-color:rgba({0},{1},{2},1.0)'.format(255,0,0)) #set color
        layout.addWidget(deleteBtn,0,2) #add it at 3rd column


        #INTENSITY_SLIDER
        intensity = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        intensity.setMinimum(1) #set min
        intensity.setMaximum(1000) #set max

        intensity.setValue(self.light.intensity.get()) #get val from intensity of light
        intensity.valueChanged.connect(lambda val : self.light.intensity.set(val)) #connect the slider and intensity
        layout.addWidget(intensity,1,0,1,2) #1 - 2nd row , 0 - 1st column , 1- 1 row of size, 2-  column of size

        #COLORBRN
        self.colorBtn = QtWidgets.QPushButton()
        self.colorBtn.setMaximumWidth(20) #set max w
        self.colorBtn.setMaximumHeight(20) #set max h
        self.setButtonColor() #new func to set the button color
        self.colorBtn.clicked.connect(self.setColor) #fnew unction to set the color of light
        layout.addWidget(self.colorBtn,1,2) #add to layout
    
    def setButtonColor(self,color = None):
        if not color:
            color = self.light.color.get() #get the color from the light

        assert len(color) == 3, "You must provide a list of 3 Colors"

        #convert float value of rgb to 0-255 integer
        r,g,b = [c*255 for c in color]#get correct rgb from float values
        self.colorBtn.setStyleSheet('background-color:rgba({0},{1},{2},1.0)'.format(r,g,b)) #set the color using QSS (similar to CSS)

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

    def disableLight(self,val):
        self.name.setChecked(not val) #pass opposite of what value is!

LightManager() #setting it false
