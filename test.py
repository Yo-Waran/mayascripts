import maya.cmds as cmds

val = cmds.HypershadeWindow()
panels = cmds.getPanel(wf=True)
print(panels)