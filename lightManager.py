#importing PyMel

import sys
sys.path.append("/Users/ramyogeshwaran/Library/Preferences/Autodesk/maya/pymel-1.4.1b1")

import pymel.core as pm

from PySide6 import QtWidgets, QtCore,QtGui

from functools import partial

class LightManager(QtWidgets.QDialog):

    lightTypes = {
        "Point Light" : pm.pointLight, #function to be called
        "Spot Light" : pm.spotLight ,
        "Directional Light" : pm.directionalLight,
        "Area Light" : partial(pm.shadingNode, 'areaLight', asLight = True), #store the function name and arguments together using partial
        "Volume Light" : partial(pm.shadingNode, 'volumeLight',asLight = True) 
    }
    

    def __init__(self):
        super(LightManager,self).__init__() #call parent init of QDialog
        self.setWindowTitle("Lights Manager")

        self.buildUI()

    def buildUI(self):
        main_layout = QtWidgets.QGridLayout(self) #Grid layout for the main
        self.lightTypeCB = QtWidgets.QComboBox() #combobox for storing the light types

        #populating combobox
        for lightType in self.lightTypes: #iterate through dict
            self.lightTypeCB.addItem(lightType) #add items for each key


        main_layout.addWidget(self.lightTypeCB,0,0)  #add it to main layout at 0,0 = (x,y) position

        createBtn = QtWidgets.QPushButton("Create") #button for creating light
        main_layout.addWidget(createBtn,0,1) #add the button at 0,1 position in the grid


        #scroll widget to scroll through lights created
        scrollWidget = QtWidgets.QWidget() #new empty widget
        scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum) #doesnt stretch the scroll area
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget) #add vertical layout to it

        scrollArea = QtWidgets.QScrollArea() #add a scroll area
        scrollArea.setWidgetResizable(True) #make it resizable
        scrollArea.setWidget(scrollWidget) #add the scrollwidget inside the scroll area
        main_layout.addWidget(scrollArea,1,0,1,2) #1 = second row, 0 = 1st column, 1=  size of row , 2 = size of columns


        #connect the button
        createBtn.clicked.connect(self.createLight) 
    
    def createLight(self):
        selLightType = self.lightTypeCB.currentText() #get the selected text in combo box
        func= self.lightTypes[selLightType] #get the function value from key

        light = func() #call the function to create the light
        self.addLight(light) #add the light to the area
        

    def addLight(self,light): #function to add the light widget
        #add the light to scroll area
        widget = LightWidget(light) #make a new Instance of lightWidget . Makes a check box
        self.scrollLayout.addWidget(widget)  #add that check box to scroll layout 
        widget.onSolo.connect(self.isolate) #call a function when that signal is emitted

    def isolate(self,value):
        print(value)
        lightWidgets = self.findChildren(LightWidget) #finds all the instances of that widget
        for widget in lightWidgets: #iterate through all lightWidgets
            if widget != self.sender(): #find the ones not emitting signal
                widget.disableLight(value) #new function that disables the light


class LightWidget(QtWidgets.QWidget):
    onSolo = QtCore.Signal(bool) #makes a new signal 
    def __init__(self,light):
        super(LightWidget,self).__init__() #call init of QWidget
        if isinstance(light , str): #if light is a string
            light = pm.PyNode(light) #convert it to pyNode so that we can work with PyMel

        self.light = light #save the light
        self.buildUI() #call function to build UI

    def buildUI(self):
        layout = QtWidgets.QGridLayout(self) #add a layout
        self.name = QtWidgets.QCheckBox(str(self.light.getTransform())) #get the transform name and save it as a checkbox
        self.name.setChecked(self.light.visibility.get()) #get visibility attr . same as cmds.getAttr(self.light.visibilty)
        #connect the checkbox
        self.name.toggled.connect(lambda val : self.light.getTransform().visibility.set(val)) #store the toggle value in val and set it as the visibility for the light
        layout.addWidget(self.name,0,0)

        #solo button
        soloBtn = QtWidgets.QPushButton('Solo') #create a btn
        soloBtn.setCheckable(True) #makes it work like a switch  
        soloBtn.toggled.connect(lambda val: self.onSolo.emit(val)) #sets a signal of True or false based on the toggle
        layout.addWidget(soloBtn,0,1) #add it to the layout

    
        

def showUI(): #function to create instance of the class
    ui = LightManager()
    ui.show()
    return ui

UI = showUI() #store the UI in a variable

