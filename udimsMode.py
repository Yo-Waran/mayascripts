import maya.cmds as cmds
selection = cmds.ls(sl=True)

for texture in selection:
	cmds.setAttr(texture+ ".uvTilingMode",3)