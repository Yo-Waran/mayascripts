from maya import cmds

class TweenWindow(object):

    def __init__(self):  #we initialzie the variables that we'll be using
        self.windowName = "TweenWindow" #make sure there is no space when creating the window Names!
    
    def tween(self,percentage,obj=None, attr = None , selection=True):
        """
        This function will created an inbetween keyframe based on the percentage , attribute selected and the previous+next keyframes from the current frame.

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
        if not attr:
            attrs = cmds.listAttr(obj, keyable=True)
            if not attrs:
                raise ValueError("No keyable attributes found on the specified object")
        else:
            attrs = [attr]
        
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
        cmds.window(self.windowName,  widthHeight=(250, 98), s = False , nde = True)
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
        row2 = cmds.rowLayout(numberOfColumns= 2) # you need to specify the number of columns
        self.slider = cmds.floatSlider(min = 0, max = 100, value=50 , step = 1 , dragCommand = self.tween) #create a slider that sets the tween percentage for the tween() method. (dragCommand/changeCommand is used to pass a value into the tween function )
        cmds.button(label="Reset", command = self.resetSlider) #creates a button that calls the reset slider function

        #go back to the parent column
        cmds.setParent(column)

        
        #make a menu for selecting the attributes
        self.buildOptions()

    def resetSlider(self, *args): #we use *args to collect any unwanted parameters that will be passed during function call
        cmds.floatSlider(self.slider, edit=True, value= 50)
    
    def buildOptions(self, attr1=None, obj2 = None, selection = True):
        
        self.menuName = "attributeLists"
        cmds.optionMenu( self.menuName, label='Attributes Affected')
      

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
            
        cmds.menuItem( label='All Tweenable', parent = self.menuName )
        
        for attrOpt in attrs1:

            self.attrName1 = "{0}.{1}".format(obj2,attrOpt)#store the attribute name in format (objName.attribute)

            #lets check if the given attribute has any keyframes. we use cmds.keyframe for that. It will return a list of keyframes if there are any present.
            if cmds.keyframe(self.attrName1,query=True):
                cmds.menuItem(label = attrOpt , parent = self.menuName)
        

if __name__=="__main__":
    t1 = TweenWindow()
    t1.show()
