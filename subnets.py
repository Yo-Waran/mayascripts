"""CREATING Subnets"""
import hou
#::Method::1::
#CREATING NODES

context= hou.node("/obj")
#create a subnet first
subnet = context.createNode("subnet")

objects = []
for obj in range(6):
    object = subnet.createNode("geo","sphere"+str(obj))
    objects.append(object)

subnet.layoutChildren()
print(objects)

#::Method::2::
objects2 = []

for nodes in range(6):
    node = context.createNode("geo","sphere"+str(obj))
    objects2.append(node)

#making a subnet by selecting the nodes and collapsing them
subnet02 = context.collapseIntoSubnet(objects2,"subnetName01")

subnet02.layoutChildren()


"""COPYING Nodes"""
import hou

context = hou.node("/obj")
myselection = hou.selectedNodes()[0]

if not myselection: #error out early
    print("select something!")

directorypath = hou.ui.selectNode(title="Select your node to copy to") 


contents = myselection.children()

copyToNode = hou.node(directorypath)

hou.copyNodesTo(contents,copyToNode) #copying nodes from destination to directory.

span = hou.ui.displayMessage("Nodes copied to : "+directorypath, buttons= ("Show me the nodes",'Select Copied node')) #display a message that stores 0 or 1 depending upon the button clicked.

if span == 1:
    copyToNode.setSelected(1,clear_all_selected = True)  #selects a node
else:
    context.setSelected(0,clear_all_selected = True) #deselects a node


"""Custom Parameters"""

import hou

context = hou.node("/obj")

#creating GEO
geo = context.createNode("subnet","customSubnet")

# Declare paramter GROUP Class first 
group = geo.parmTemplateGroup() #this wont be visible 

#creating a folder for new paramters
folder = hou.FolderParmTemplate("folder","Custom Properties")

#DECLARE a new paramter
intensity = hou.FloatParmTemplate("intensity","INTENSITY",num_components = 1) # creates a float parameter with label intensity and 1 represents number of components for input
parm2 = hou.IntParmTemplate("seed","SEED",num_components = 1,default_value = (5,0,0),min = 0, max =10) #create Int parameter
parm3 = hou.ToggleParmTemplate("intensityEnable","ENABLE") #create a check box


#CONDITIONS for Parameters
intensity.setConditional(hou.parmCondType.DisableWhen,"{"+"{0}".format(parm3.name())+ " 0}") #setting condition to Disable when enable is off


# APPENDING 

#Add intensity to the folder
folder.addParmTemplate(parm3) #append the check box
folder.addParmTemplate(intensity) #Append the parameter to the folder
folder.addParmTemplate(parm2) #append second parameter as well


group.append(folder) #append the folder to the group

#hiding rest of the folders
group.hideFolder("Transform",1)
group.hideFolder("Subnet",1)

geo.setParmTemplateGroup(group) #THIS IS IMPORTANT FOR ASSIGNING GROUP TEMPLATE TO THE TABS

geo.replaceSpareParmTuple(intensity.name(),intensity) #applying the condition on the parameters , this needs to done after setting the TemplateGroup.

"""SETTING EXPRESSIONS"""
import hou
context = hou.node("/obj")#define context

subnetnode = context.node("customSubnet")#store the subnet

lightnode = subnetnode.createNode("envlight") #creating the light node

path = subnetnode.parm("intensity").path() #stores the path of the parameter

lightnode.parm("light_intensity").setExpression('ch("'+path+'")') #set the expression for the other parameter
 

"""LIGHTS GROUPER SCRIPT"""

import hou

class LIGHTS_GROUP():
    def __init__(self):
        pass

    def lightsGlobalize(self):

        #SUBNETIZE FROM SELECTION
        my_selection = hou.selectedNodes()

        if not my_selection: #error out early
            raise ValueError("Nothing is Selected!")

        context =my_selection[0].parent() #define the context

        #first lets store the default values from first element
        def_intensity = my_selection[0].parm("light_intensity").eval() 
        def_exposure = my_selection[0].parm("light_exposure").eval() 
        def_radiusx = my_selection[0].parm("areasize1").eval() 
        def_radiusy = my_selection[0].parm("areasize2").eval() 
        def_color = my_selection[0].parmTuple("light_color").eval() 


        subnetnode = context.collapseIntoSubnet(my_selection,"ALL_LIGHTS") #collapse into subnets

        # DECLARE SUBNET PARAMETERS
        group = subnetnode.parmTemplateGroup() #this wont be visible 

        #creating a folder for new paramters
        folder = hou.FolderParmTemplate("folder","Custom Properties") #Top Most folder
        globals_folder =  hou.FolderParmTemplate("globalsettings","Global Values") #sub folder

        #declaring parameters
        globalEnable = hou.ToggleParmTemplate("globalEnable","Global Changes") #create a check box
        intensity = hou.FloatParmTemplate("intensity","Global Intensity",num_components = 1 , default_value = (def_intensity,0,0)) # creates a float parameter with label intensity and 1 represents number of components for input
        exposure = hou.FloatParmTemplate("exposure","Global Exposure",num_components = 1, default_value = (def_exposure,0,0))
        radius = hou.FloatParmTemplate("radius","Global Radius",num_components = 2, default_value= (def_radiusx,def_radiusy))
        color = hou.FloatParmTemplate("color","Global Color",num_components = 3, default_value = def_color, look = hou.parmLook.ColorSquare, naming_scheme = hou.parmNamingScheme.RGBA) #for color picking the data type should also be Float but with 3 components for rgb


        # Appending parameters 
        folder.addParmTemplate(globalEnable) #append the check box
        globals_folder.addParmTemplate(intensity) #append the parameter to the sub folder
        globals_folder.addParmTemplate(exposure) #append the parameter to the sub folder
        globals_folder.addParmTemplate(radius) #append the parameter to the sub folder
        globals_folder.addParmTemplate(color) #append the parameter to the sub folder
        folder.addParmTemplate(globals_folder) #append the sub folder
        group.append(folder) #append the folder to the group

        #hiding rest of the folders
        group.hideFolder("Transform",1)
        group.hideFolder("Subnet",1)

        #finalizing the parameters
        subnetnode.setParmTemplateGroup(group) #THIS IS IMPORTANT FOR ASSIGNING GROUP TEMPLATE TO THE TABS

        #Conditions for the folder
        globals_folder.setConditional(hou.parmCondType.DisableWhen,"{"+"{0}".format(globalEnable.name())+ " 0}") #setting condition to Disable when globalenable is off
        subnetnode.replaceSpareParmTuple(globals_folder.name(),globals_folder) #applying the condition on the parameters , this needs to done after setting the Template Group.

        #LINKING LIGHTS TO PARAMETERS


        for lgt in subnetnode.children(): #iterating through lights
            lgt.parm("light_intensity").setExpression('ch("../intensity")') #set the expression for intensity
            lgt.parm("light_exposure").setExpression('ch("../exposure")') #set the expression for exposure

            lgt.parm("areasize1").setExpression('ch("../radiusx")') #set the expression for radius 1
            lgt.parm("areasize2").setExpression('ch("../radiusy")') #set the expression for radius 2
            lgt.parm("light_colorr").setExpression('ch("../colorr")') #set the expression for color R

            lgt.parm("light_colorg").setExpression('ch("../colorg")') #set the expression for color G
            lgt.parm("light_colorb").setExpression('ch("../colorb")') #set the expression for color B
    

obj1 = LIGHTS_GROUP()
obj1.lightsGlobalize()
 

