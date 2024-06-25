"""
Script Name: skeletonJointCreate.py
Author: Ram Yogeshwaran
Company: The Mill
Contact: Ram.Yogeshwaran@themill.com
Description: This script generates skeleton joint at the center of each selected mesh in Maya.
"""

from maya import cmds

class JointCreator():
    """
    This is a Joint Creator class that lets us create a joint at the center of selected meshes
     
    Methods:
        __init__: Initializes the Joint Creator class.
        createUI: This function creates the UI for create Joints button
        createJoints: This function centers the pivots of the given meshes and creates the joints in the center position
    """
    def __init__(self):
        self.mysel = None
        self.windowName = "Joints Creator"

    def createUI(self):
        """
            This function creates the UI for create Joints button
        """
        if cmds.window(self.windowName,query=True,exists= True): #delete UI if exists already
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName,rtf=True,s=False) #
        column1 = cmds.columnLayout()
        cmds.button(label="Create Joints and Center Pivot",command = self.createJoints,width= 250, height = 50)
        cmds.showWindow()

    def createJoints(self,*args):
        """
            This function centers the pivots of the given meshes and creates the joints in the center position
        """

        #store selected geos
        self.mysel = cmds.ls(sl=True)

        if not self.mysel:
            cmds.warning("No transforms selected.")
            raise RuntimeError("No transforms selected.")
        
        #joint variables
        jointNum = 0
        self.jointList = []

        #iterate through selection
        for sel in self.mysel:
            cmds.xform(sel, worldSpace = True,cp = True) #center pivot 
            pos = cmds.xform(sel,query = True, worldSpace= True,rotatePivot = True) #query pivot rotate pos
            cmds.select(cl=True) #clear selection
            joint = cmds.joint(name = "joint_"+sel,position = pos) #make a joint in that pos
            jointNum+=1
            self.jointList.append(joint)
        
        print("Created the below joints at each mesh center")
        for joint in self.jointList:
            print(joint)
    

if __name__=="__main__":
    obj = JointCreator()
    obj.createUI()


  
