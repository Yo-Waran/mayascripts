import sys
import maya.cmds as cmds
from importlib import reload #for reloading
import pprint

sys.path.append("/Users/ramyogeshwaran/Documents/Yogi/GitHub Repo/mayascripts/")

import controllerLibrary  
reload(controllerLibrary) #to update instances of items

from PySide6 import QtWidgets,QtCore,QtGui

class ControllerLibraryUI(QtWidgets.QDialog):
    """
        The Controller Library UI is a dialog that lets us save ,browse and import the Saved Controllers!
    """
    def __init__(self): #constructor 
        super(ControllerLibraryUI,self).__init__() #construct all the parameters from the parent class
        self.setWindowTitle("My Asset Library")
        self.library = controllerLibrary.ControllerLibrary() #instance of previous class

        self.buildUI() #function to build rest of the UI
        self.populate() #to populate the UI with our items

    def buildUI(self):
        """ 
            This method builds the UI using QT Modules
        """
        main_layout = QtWidgets.QVBoxLayout(self) # Main Vertical Layout

        #directory layout
        dirLayout = QtWidgets.QHBoxLayout()
        self.dirLabel = QtWidgets.QLabel("Files Directory : " + self.library.directory)
        browseBtn = QtWidgets.QPushButton("change (WIP)")
        browseBtn.clicked.connect(self.changeFolder)
        dirLayout.addWidget(self.dirLabel)
        dirLayout.addWidget(browseBtn)
        main_layout.addLayout(dirLayout)
        
        #main widget and the first layout
        saveWidget = QtWidgets.QWidget() #main container widget

        #layout for input and button
        saveLayout = QtWidgets.QHBoxLayout(saveWidget) #horizontal layout
        main_layout.addWidget(saveWidget) #add the main widget to the main layout

        #textfield and button on top
        self.saveNameField= QtWidgets.QLineEdit() #inputBox
        saveLayout.addWidget(self.saveNameField)

        saveBtn = QtWidgets.QPushButton("Save") 
        saveBtn.clicked.connect(self.save) #call func when clicked
        saveLayout.addWidget(saveBtn)

        #thumbnail view for the list
        size = 64 #size for icons
        buffer = 12 #padding number
        self.listWidget = QtWidgets.QListWidget()  
        self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode) #sets the viewmode for list
        self.listWidget.setIconSize(QtCore.QSize(size,size)) #resize the icons
        self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust) #make the list responsive
        self.listWidget.setGridSize(QtCore.QSize(size+buffer,size+buffer)) #to add padding between items
        main_layout.addWidget(self.listWidget) #add it to main layout

        #buttons on bottom

        bottomWidget = QtWidgets.QWidget() #empty container for placing all the buttons
        btmLayout = QtWidgets.QHBoxLayout(bottomWidget) #add a layout to the container
        main_layout.addWidget(bottomWidget)

        importBtn = QtWidgets.QPushButton("Import!")#first button
        importBtn.clicked.connect(self.load)
        btmLayout.addWidget(importBtn)
        
        refreshBtn = QtWidgets.QPushButton("Refresh")#second button
        refreshBtn.clicked.connect(self.populate) #call the populate func
        btmLayout.addWidget(refreshBtn)
        
        closeBtn = QtWidgets.QPushButton("Close")#third button
        closeBtn.clicked.connect(self.close) #call a func called close() when clicked
        btmLayout.addWidget(closeBtn)        
        

    def populate(self):
        """
            This method populates the list Widget with items that are present
        """
        self.listWidget.clear() #clear the function before populating
        #call the find() function from the ControllerLibrary class
        self.library.find()

        for name,info in self.library.items(): # .items() since the library is a dict
            item = QtWidgets.QListWidgetItem(name) #add an item in the list widget
            self.listWidget.addItem(item)

            screenshot = info.get('screenshot')
            if screenshot: #if there is a screenshot
                icon = QtGui.QIcon(screenshot) #creates an icon
                item.setIcon(icon) #sets the icon to each item

            #add tooltips
            item.setToolTip(pprint.pformat(info)) #set tooltip  for each item
    
    def load(self):
        """
            This method imports the selected item from the list into the maya scene
        """
        currentItem = self.listWidget.currentItem() #store the selected item
        if not currentItem: #if nothing selected
            return
        
        name = currentItem.text() #store the text
        self.library.load(name) #call the load function from the other module
        print(name + ": has been Imported")


    def save(self):
        """
            This method saves the selected/All objects based on the name in the field
        """
        name = self.saveNameField.text() #save the field's input
        
        if not name.strip(): #if the string has whitespaces
            cmds.warning("You must give a Valid Name") #warning
            return
        
        self.library.save(name) #call the save func
        self.populate() #refresh again
        self.saveNameField.clear() #clear the field

    def changeFolder(self):
        # Use Maya's fileDialog2 to select a directory
        directory = cmds.fileDialog2(dialogStyle=2, fileMode=3, okCaption='Select')
        if directory:
            selected_directory = directory[0]
            self.dirLabel.setText(selected_directory)
            #make the functions to update the UI based on the given path
            self.library.directory = selected_directory
        else:
            pass
        self.buildUI()


def showUI():
    # create instance of the UI class
    ui = ControllerLibraryUI()
    ui.show()
    return ui

dialog = showUI()

