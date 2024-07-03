import os 
import maya.cmds as cmds  
import json #to write a data file

USRAPPDIR= cmds.internalVar(userAppDir=True) #store the Maya Pref folder  
DEFAULT_DIRECTORY = os.path.join(USRAPPDIR,'controllerLib') #join the string with the path (using OS SPECIFIC Operator)  

def createDir(directory=DEFAULT_DIRECTORY):
    """
        Creates the given directory if it doesnt exist

        Args:
            directory : Directory to create the directory

    """

    #check if directory exists
    if not os.path.exists(DEFAULT_DIRECTORY): #check existence of path is false  
        os.mkdir(DEFAULT_DIRECTORY) #make directory
        print("Directory Created!")  
    
class ControllerLibrary(dict): #making it a child of Dictionary class  

    def __init__(self):
        self.directory = DEFAULT_DIRECTORY

    def save(self,filname,dir = DEFAULT_DIRECTORY,screenshot = True , **info): 
        """
            A function to save out .ma files   

            Args:
                name : Name of file to be saved  
                dir : Directory to save the file in (Default is User Directory)  
        """
        createDir(dir) #run the global function to make the folder  
        path = os.path.join(dir,"{0}.ma".format(filname)) #make the file path  
        infoFile = os.path.join(dir,"{0}.json".format(filname))#file path for storing the data in json format

        #update json dict
        info['name'] = filname
        info['path'] = path
        
        #make the .ma file
        cmds.file(rename = path) #rename file name 
        if cmds.ls(selection = True): #check for selection  
            cmds.file(force = True, type = 'mayaAscii',exportSelected = True) #save the selected obj  
        else:
            cmds.file(force = True , type = 'mayaAscii' , save = True) #save all obj   

        if screenshot :
            info['screenshot'] = self.saveScreenshot(filname,dir)
        #write the json data with info arguments
        with open(infoFile,'w') as file: #open the file with info file path and store it in a temporary var called file
            json.dump(info,file,indent = 4) #then write the **info arguments on the file with some indentation

        print("saved file!")
        self[filname] = infoFile #update our dict with the file name and its path   
    
    def find(self,dir = DEFAULT_DIRECTORY) :  
        self.clear() #clear the dict before finding it
        if not os.path.exists(dir): #if no directory exists  
            return #go out   
        
        files = os.listdir(dir) #store all the files in dir   
        mayaFiles = [item for item in files if item.endswith(".ma")] #filter out only maya files  

        for ma in mayaFiles: #iterate  
            name,ext = os.path.splitext(ma) #split the extension only  
            path = os.path.join(dir,ma) #make the full path 
            
            #check info json
            infoFile = '{0}.json'.format(name)
            if infoFile in files:
                infoFile = os.path.join(dir,infoFile)

                #read the json data 
                with open(infoFile,'r') as file: #open the file with info file path and store it in a temporary var called file
                    info = json.load(file) #then read the file and store it a var
            else: 
                info = {} #no dict

            info['name'] = name
            info['path'] = path

            screenshot  = "{0}.jpeg".format(name)

            if screenshot in files:
                info['screenshot'] = os.path.join(dir,screenshot)
            self[name] = info #update our dictionary
        

        
    def load(self,name):
        path = self[name]['path'] #get the path from our stored dictionary!
        cmds.file(path,i = True ) #load the file  / import the file
    
    def saveScreenshot(self,name,dir):
        path = os.path.join(dir,"{0}.jpeg".format(name)) #path for creating image file

        cmds.viewFit(fitFactor = 100,c = True) #fit the view on selected

        # Set the current renderer to Maya Software
        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mayaSoftware', type='string')
        cmds.setAttr('defaultRenderGlobals.imageFormat',8) #render setting for saving a jpeg
        
        sel = cmds.ls(selection = True)
        if sel:
            cmds.select(cl=True) #clearSelection
        #render the image out
        cmds.playblast(completeFilename = path, forceOverwrite = True, format = 'image',width = 600, height = 600 , showOrnaments = False , startTime = 1, endTime = 1 , viewer = False,qlt = 80)

        #select it back again
        cmds.select(sel)

        print("Screenshot Captured!")
        return path
    