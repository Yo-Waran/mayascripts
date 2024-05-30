"""
Script Name: gearCreator.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script generates a procedural Gear in Maya.
"""
from maya import cmds

class Gear(object):
    """
    This is a Gear class that lets us create a gear and modify it , if required.
     
    Methods:
        __init__: Initializes the Gear class.
        buildGearUI: builds the base window for the createGear() and modifyGear() and displays it
        createGear: creates a gear with the set arguments.  
        modifyGear:modifies the created gear's Height,length or teeths according to the passed arguments.
        dragHeight : changes the height variable and calls the modifyGear() method
        dragTeeth : changes the number of teeths and calls the modifyGear() method
        dragLength : changes the length variable and calls the modifyGear() method
        dragSlider1 : gets the int value from the field , changes the slider value and runs the modifyGear() method 
        dragSlider2 : gets the float value from the field , changes the slider value and runs the modifyGear() method
        dragSlider3 : gets the float value from the field , changes the slider value and runs the modifyGear() method
        reset1 : resets slider1, text displayed beside it and runs the modifyGear() method
        reset2 : resets slider2, text displayed beside it and runs the modifyGear() method
        reset3 : resets slider3, text displayed beside it and runs the modifyGear() method
        deleteWindow : disconnects the Gear from the creator and deletes the History.
        makeGear: calls the CreateGear() method
    """

    def __init__(self):
        """ Initializing some attributes """
        self.transformNode = None
        self.shapeNode = None
        self.extrudeNode = None
        self.windowName = "GearWindow"
        self.teethValue = 10
        self.lengthValue = 0.25
        self.heightValue = 2
    
    
    def buildGearUI(self):
        """
        This Function will create the UI for the createGear() and modifyGear() methods.
        """
        #check if it exists already
        if cmds.window(self.windowName,query = True , exists = True):
            cmds.deleteUI(self.windowName)
        self.gearWindow = cmds.window(self.windowName, widthHeight = (210,200), s = False) #create a window and store it
        cmds.showWindow()
        
        #parentColumn
        column = cmds.columnLayout()
        cmds.text("Lets make some Gears!")
        cmds.text("*"*28)
        row0= cmds.rowLayout(numberOfColumns=2)
        cmds.text("Step 1: Make the gear")
        cmds.button(label="Make Gear", command = self.makeGear)
        cmds.setParent(column)
        cmds.text("*"*50)
        cmds.text("Step 2: Modify it to your liking")

        #Slider1
        row1 = cmds.rowLayout(numberOfColumns= 4)
        self.slider1 = cmds.intSlider(min = 5 , max = 100, value = 10, step = 1 , dragCommand = self.dragTeeth)
        self.teethsText = cmds.intField("Teeths",min = 5, max = 100, value =10 , step = 1, w = 30, changeCommand = self.dragSlider1)
        cmds.text(" : Teeths")
        cmds.button(label = "Reset", command = self.reset1)        
        
        cmds.setParent(column)       
        #Slider2
        row2 = cmds.rowLayout(numberOfColumns= 4)
        self.slider2 = cmds.floatSlider(min = 0 , max = 5, value = 0.25, step = 1 , dragCommand = self.dragLength)
        self.lengthText = cmds.floatField("length",min = 0, max = 5, value =0.25 ,showTrailingZeros = False, step = 1, w = 30, changeCommand = self.dragSlider2)
        cmds.text(" : Length")
        cmds.button(label = "Reset", command = self.reset2)   

        cmds.setParent(column)

        #Slider3
        row3 = cmds.rowLayout(numberOfColumns= 4)
        self.slider3 = cmds.floatSlider(min = 0.1 , max = 15, value = 2, step = 0.1 , dragCommand = self.dragHeight)
        self.heightText = cmds.floatField("height",min = 0.1, max = 15, value = 2 ,showTrailingZeros = False, step = 0.1, w = 30, changeCommand = self.dragSlider3)
        cmds.text(" : Height")
        cmds.button(label = "Reset", command = self.reset3)   

        cmds.setParent(column)

        cmds.text("*"*46)
        row4= cmds.rowLayout(numberOfColumns=2)
        cmds.text("Step 3: End Creation")  
        cmds.button(label="Disconnect", command = self.deleteWindow)
        cmds.setParent(column)
        cmds.text("*"*50)
        
    def dragSlider1(self,dragInt,*args):
        self.teethValue = dragInt
        cmds.intSlider(self.slider1,edit=True,value = self.teethValue)
        self.modifyGear(teeth= self.teethValue, l = self.lengthValue, h =self.heightValue)
        
    def dragSlider2(self,dragFlt,*args):
        self.lengthValue = dragFlt
        cmds.floatSlider(self.slider2,edit=True,value = round(self.lengthValue,2))
        self.modifyGear(teeth= self.teethValue , new_length = self.lengthValue , h =self.heightValue)  
    
    def dragSlider3(self,dragFlt,*args):
        self.heightValue= dragFlt
        cmds.floatSlider(self.slider3,edit=True,value = round(self.heightValue,2))
        self.modifyGear(teeth = self.teethValue , l= self.lengthValue , h = self.heightValue)

    def dragHeight(self,dragHgt,*args):
        self.heightValue = dragHgt
        cmds.floatField(self.heightText, edit = True, value = round(self.heightValue,2))
        self.modifyGear(teeth = self.teethValue , l= self.lengthValue , h = self.heightValue)

    
    def deleteWindow(self,*args):
        cmds.select(self.transformNode)
        cmds.DeleteAllHistory()
        cmds.select(cl=True)
        cmds.deleteUI(self.windowName)


    def dragTeeth(self,teethsInt, *args):
        self.teethValue = teethsInt #store the teethsValue
        cmds.intField(self.teethsText, edit = True , value = self.teethValue) #changing the number of teeths 
        self.modifyGear(teeth= self.teethValue, l = self.lengthValue, h =self.heightValue) #modifying the gear according to the stored value
    
    def dragLength(self,lengthInt, *args):
        self.lengthValue = lengthInt #store the lengthValue
        cmds.floatField(self.lengthText, edit = True , value = round(self.lengthValue,2)) #changing the length value displayed 
        self.modifyGear(teeth= self.teethValue , new_length = self.lengthValue , h =self.heightValue) #modifying the gear according to the stored value
    
    def reset1(self, *args):
        cmds.intSlider(self.slider1, edit = True , value = 10 ) #reset slider
        cmds.intField(self.teethsText, edit = True , value = 10) #reset the text displayed
        self.modifyGear(l = self.lengthValue , h = self.heightValue) #modfiy the gear according to the stored value
        self.teethValue = 10
    
    def reset2(self, *args): #same as the other reset button
        cmds.floatSlider(self.slider2, edit = True, value = 0.25)
        cmds.floatField(self.lengthText, edit = True , value = 0.25)
        self.modifyGear(t= self.teethValue, h = self.heightValue)
        self.lengthValue = 0.25
    
    def reset3(self, *args):
        cmds.floatSlider(self.slider3,edit = True , value = 2)
        cmds.floatField(self.heightText,edit = True,value=2)
        self.modifyGear(teeth = self.teethValue , l = self.lengthValue )
        self.heightValue = 2


    def makeGear(self, *args): #this function calls the createGear() when the button is pressed
        self.createGear()
        cmds.select(self.transformNode)


    def createGear(self, teeth=10, length= 0.25):
        """
        This function will create a gear based on the required number of teeths for the gear.

        Args:
        Teeth : Number of teeths to be created (default: 10)
        Length : Length of the teeths to be created (default : 0.3)
        
        Returns:
        A tuple with the transform,shape and extrude Node
        """
        #subdivisions in the pipe is double the number of teeths required, so subdiv = teeth x 2
        subdiv = teeth * 2
        self.transformNode, self.shapeNode = cmds.polyPipe(n="customGear",sa=subdiv) #certain subdiv Pipe is created and transform,shape nodes are stored

        #selecting the alternate faces for the teeth
        teethFaces = range(subdiv*2,subdiv*3,2) #Every faces in the pipe ranges from one number to another. The center alternate faces ranges from subdiv*2 to subdiv*3 with every 2nd step
        
        cmds.select(clear=True) #clear selection

        for face in teethFaces:
            cmds.select("{0}.f[{1}]".format(self.transformNode,face),add = True) #adds every teethfaces together in a format 'polyPipe1.f[40]'
        
        #now that its selected we extrude the faces with the given length
        self.extrudeNode = cmds.polyExtrudeFacet(ltz=length)[0] #we select the [0] the first element to be stored so that we dont store a list , instead we need an item.

        cmds.select(clear=True) #clear selection

        #lets return the transform,shape and extrude node 
        return self.transformNode,self.shapeNode,self.extrudeNode

    def modifyGear(self, **kwargs):
        """
        This function will modify any existing gear based on the required number of teeths for the gear.

        Args:
        shapeNode: shapeNode of the existing gear
        extrudeNode: extrudeNode of the existing gear
        Teeth : Number of teeths to be created (default: 10)
        Length : Length of the teeths to be created (default : 0.3)
        
        Returns:
        A tuple with the shape and extrude Node
        """
        #define aliases for parameters
        teeth = kwargs.get('t',kwargs.get("teeth",10))
        new_length = kwargs.get('l',kwargs.get("new_length",0.25))
        height = kwargs.get('h',kwargs.get("height",2))

        #lets calculate the subdiv for the new number of teeth again
        subdiv2 = teeth * 2

        #editting the existing pipenode using its SHAPE NODE!
        if not self.shapeNode:
            raise ValueError("No Gear is created/Connected with the plugin. Click on Make Gear")

        cmds.polyPipe(self.shapeNode,edit=True,sa=subdiv2)

        #select the correct faces to be extruded
        teethFaces2 = range (subdiv2*2,subdiv2*3,2) #The center alternate faces ranges from subdiv*2 to subdiv*3 with every 2nd step

        newTeethFaces = []

        #assign proper face names to the newTeethFaces List
        for face in teethFaces2:
            newTeethFace = "f[{0}]".format(face)
            newTeethFaces.append(newTeethFace)
        
        #now we know which faces to Extrude properly. Lets set the extrusion faces again by modifying the extrude node's input components attribute
        cmds.setAttr(self.extrudeNode +'.inputComponents',len(newTeethFaces),*newTeethFaces, type = "componentList") # modifying input components using setAttr can work in specific scenarios where the Maya command supports it. In this case, the extrudeNode provides an attribute for controlling input components, allowing you to dynamically specify which faces to extrude.
        cmds.setAttr(self.extrudeNode+'.localTranslateZ',new_length)

        #added an extra functionality to edit the Height according to the given value
        cmds.polyPipe(self.shapeNode,edit=True,h=height)

        return self.shapeNode, self.extrudeNode 

if __name__=="__main__":
    g1 = Gear()
    g1.buildGearUI()



"""
MIT License

Copyright (c) 2024 Ram Yogeshwaran

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


