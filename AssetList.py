import maya.cmds as cmds

def isGroup(node):
    children = cmds.listRelatives(node, children=1)
    for child in children:
        if cmds.nodeType(child) != "transform":
            return False
        return True 

def getAssetList(type):
    topGroupNodes = cmds.ls(assemblies=True)
    assetNodes = filter(lambda node: isGroup(node), allNodes)
    filteredList = []

    for node in assetNodes:
        if "shot_cam" not in node:
            filename = cmds.referenceQuery(node, filename=True)
            if type == "ENVIR" and "environment" in filename:
                filteredList.append(node)
            elif type == "CHAR" and "character" in filename:
                filteredList.append(node)
            elif type == "PROP" and "prop" in filename:
                filteredList.append(node)
                
    return filteredList
            
print getAssetList("ENVIR")
print getAssetList("CHAR")
print getAssetList("PROP")
