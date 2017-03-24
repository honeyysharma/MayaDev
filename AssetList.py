import maya.cmds as cmds

def isGroup(node):
    children = cmds.listRelatives(node, children=1)
    for child in children:
        if cmds.nodeType(child) == "transform":
            return True
        else:
            return False

cmds.select(cmds.ls(assemblies=True))    

topGroupNodes = cmds.ls(assemblies=True)
assetNodes = filter(lambda node: isGroup(node), allNodes)
envirList = []
charList = []
propList = []

for node in assetNodes:
    filename = cmds.referenceQuery(node, filename=True)
    if "environment" in filename:
        envirList.append(node)
    elif "character" in filename:
        charList.append(node)
    else:
        propList.append(node)
        
print envirList
print charList
print propList
