import maya.cmds as cmds
# Check if the commandPort is already open
if not cmds.commandPort(':7001', q=True): 
    cmds.commandPort(name=":7001", sourceType="mel", echoOutput=True)
