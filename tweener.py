"""
Script Name: TweenWindow.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script provides functionality for tweening keyframes in Maya.
"""
from maya import cmds

ATTRIBUTES = {
    "translateX":"tx",
    "translateY":"ty",
    "translateZ":"tz",
    "rotateX":"rx",
    "rotateY":"ry",
    "rotateZ":"rz",
    "scaleX":"sx",
    "scaleY":"sy",
    "scaleZ":"sz",
    "visibility":"v"
}

class TweenWindow(object):
    """
    Methods:
        __init__: Initializes the TweenWindow class.
        tween: Creates an in-between keyframe based on the percentage, attribute selected, and surrounding keyframes.
        show: Displays the window UI.
        buildUI: Builds the UI elements for the window.
        resetSlider: Resets the slider to its default value.
        buildOptions: Builds the attribute selection menu.
        changeAttribute: Handles attribute selection changes.
        halfValue : sets a key with exactly half value at the current time
        deleteFrame :Deletes the keyframes of selected attributes in the current time
    """

    def __init__(self):  #we initialzie the variables that we'll be using
        self.windowName = "TweenerWindow" #make sure there is no space when creating the window Names!
        self.attr= None
    
    def tween(self,percentage,obj=None, selection=True):
        """
        This function will create an inbetween keyframe based on the percentage , attribute selected and the previous+next keyframes from the current frame.

        Args:
        percentage : percentage to Tween the keyframe
        obj : which object to create the keyframe on
        Attr : which attribute on the specified object to keyframe on
        selection : get the selected objects
        
        Returns:
        None
        """
        #lets raise an error early if obj is not given and selection is set to false
        if not obj and selection:
            selected_objects = cmds.ls(selection=True)
            if not selected_objects:
                raise ValueError("Nothing is selected to tween!")
            obj = selected_objects[0]
        
        # If attr is provided, use it directly; otherwise, list all keyable attributes
        if not self.attr:
            attrs = cmds.listAttr(obj, keyable=True)
            if not attrs:
                raise ValueError("No keyable attributes found on the specified object")
        else:
            attrs = [self.attr]
        
        #get the current keyframe and store it
        currentTime= cmds.currentTime(query=True)

        #go through the attribute with the keyframes
        for attr in attrs:
            self.attrName = "{0}.{1}".format(obj,attr)#store the attribute name in format (objName.attribute)

            #lets check if the given attribute has any keyframes. we use cmds.keyframe for that. It will return a list of keyframes if there are any present.
            keyframes = cmds.keyframe(self.attrName,query=True) #checks if the given attribute has a keyframe and returns a list of keyframes accordingly

            if not keyframes: #continue on to the next attribute if there's no keyframe
                continue
    
            #collecting previous and later keyframes
            previous_keyframes = [pframe for pframe in keyframes if pframe < currentTime ] #list comprehension to collect all the previous keyframes . This line is the same as creating a 'for loop with an if statement' inside it. 
            later_keyframes = [lframe for lframe in keyframes if lframe > currentTime ]

            if not previous_keyframes and not later_keyframes:
                continue

            #maximum value of previous and min value of later
            prev_frame = max(previous_keyframes) if previous_keyframes else None
            next_frame = min(later_keyframes) if later_keyframes else None

            #continue to next attribute if the keyframe is an extreme keyframe
            if not prev_frame or not next_frame:
                continue

            #store the values from prev and next frame
            prev_value = cmds.getAttr(self.attrName,time=prev_frame)
            next_value = cmds.getAttr(self.attrName,time=next_frame)

            #find the current value according to the difference and the percentage
            difference = next_value - prev_value
            weighted_difference = (difference * percentage) / 100.0
            currentValue = prev_value + weighted_difference 

            #set the keyframe
            cmds.setKeyframe(self.attrName, time= currentTime , value = currentValue)


    def show(self,*args):
        if cmds.window(self.windowName, query=True, exists=True):  # checks if the window exists already
            print("Deleting UI")
            cmds.deleteUI(self.windowName) #if yes , then delete already existing ones
        cmds.window(self.windowName, s = False , nde = True)
        self.buildUI() #call another method that builds the UI for this window
        cmds.showWindow()
        

    def buildUI(self,*args):
        
        #make a parent column layout
        column = cmds.columnLayout()
        row1 = cmds.rowLayout(numberOfColumns= 2)

        #create a refresh function
        cmds.text("Use this button to refresh ")
        cmds.button(label="Refresh",command = self.show)

        cmds.setParent(column)
        
        cmds.text("Use this Slider to create your Tween Keys")
        
        #make a row layout inside the column layout
        row2 = cmds.rowLayout(numberOfColumns= 4) # you need to specify the number of columns
        self.slider = cmds.floatSlider(min = 0, max = 100, value=50 , step = 1 , dragCommand = self.tween) #create a slider that sets the tween percentage for the tween() method. (dragCommand/changeCommand is used to pass a value into the tween function )
        cmds.button(label="Reset", command = self.resetSlider) #creates a button that calls the reset slider function
        cmds.button(label="Half Value",command = self.halfValue) #creates a button that calls the halfValye method
        cmds.button(label = "Delete",command = self.deleteFrame)
        #go back to the parent column
        cmds.setParent(column)

        
        #make a menu for selecting the attributes
        self.buildOptions()

    def resetSlider(self, *args): #we use *args to collect any unwanted parameters that will be passed during function call
        cmds.floatSlider(self.slider, edit=True, value= 50)

    def halfValue(self, *args): #we use *args to collect any unwanted parameters that will be passed during function call
        cmds.floatSlider(self.slider, edit=True, value= 50)
        self.tween(50)

    def deleteFrame(self,*args): 
        current_time = cmds.currentTime(query=True) #get current Time
        try:
            selected_objects = cmds.ls(selection=True)[0]
            selected_attr = self.attr #get selected attribute
            if selected_attr: #if there is one attribute selected
                cmds.cutKey("{0}.{1}".format(selected_objects,selected_attr), time=(current_time, current_time))
                    
            if not selected_attr:  #if there are more attributes selected
                selected_attr = cmds.listAttr(selected_objects, keyable=True)
                for attr in selected_attr:
                    cmds.cutKey("{0}.{1}".format(selected_objects,attr), time=(current_time, current_time))
        except IndexError:
            cmds.warning("No attribute selected to delete keyframe.")

    
    def buildOptions(self, attr1=None, obj2 = None, selection = True):
        #create a new menu
        self.menuName = "attributeLists" #name of the menu to be referred
        self.selectedOption = None #default option selected
        cmds.optionMenu( self.menuName, label='Attributes Affected', cc = self.changeAttribute) #new optionMenu is created which calls a func everytime it changes the menu.
      

        #checks if obj and selection is present
        if not obj2 and selection:
            selected_objects2 = cmds.ls(selection=True)
            if not selected_objects2:
                cmds.menuItem( label='Nothing is selected', parent = self.menuName )
                return
            obj2 = selected_objects2[0]
        
        # If attr is provided, use it directly; otherwise, list all keyable attributes
        if not attr1:
            attrs1 = cmds.listAttr(obj2, keyable=True, visible = True)
            if not attrs1:
                cmds.menuItem( label='No Keyable Attributes', parent = self.menuName )
                return
        else:
            attrs1 = [attr1]
            
        cmds.menuItem( label='All Tweenable', parent = self.menuName )#first menu item is created
        
        for attrOptions in attrs1:

            self.attrName1 = "{0}.{1}".format(obj2,attrOptions)#store the attribute name in format (objName.attribute)

            #lets check if the given attribute has any keyframes. we use cmds.keyframe for that. It will return a list of keyframes if there are any present.
            if cmds.keyframe(self.attrName1,query=True):
                cmds.menuItem(label = attrOptions , parent = self.menuName) #create MenuItems for the all other attributes with keyframes!
            
            
    def changeAttribute(self,*args):
        self.selectedOption = cmds.optionMenu(self.menuName, query=True, value=True) #queries the active option selected in the menu and stores it in a variable
        self.attr = ATTRIBUTES.get(self.selectedOption,None) #assigns a value to the self.attr if selected option matches with the global ATTRIBUTES dictionaries!


if __name__=="__main__":
    t1 = TweenWindow() #create instance of the class  
    t1.show() #call the show() in the instance



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
