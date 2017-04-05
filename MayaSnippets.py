#To check is the give node is group or not
import maya.cmds as cmds

def isGroup(node):
    children = cmds.listRelatives(node, children=1)
    for child in children:
        if cmds.nodeType(child) != "transform":
            return False
        return True
    
 
#To get assets based on shot gun asset category
from sgtkLib import tkm, tkutil
import os

def getAssetList(type):
    prod = os.environ['PROD']
    tank, sgw, project = tkutil.getTk(prod, fast=True)
    filteredList = []
    
    topGroupNodes = cmds.ls(assemblies=True)
    assetNodes = filter(lambda node: isGroup(node), topGroupNodes)
    
    for node in assetNodes:
        filename = cmds.referenceQuery(node, filename=True)
        ctx =  tank.context_from_path(filename)
        entity = ctx.entity
        asset_name = str(entity['name'])
        asset = sgw.Asset(asset_name, project=project)
        asset_type = asset.sg_asset_type

        if type == "ENVIR" and asset_type == "environment":
            filteredList.append(node)
        elif type == "CHAR" and asset_type == "character":
            filteredList.append(node)
        elif type == "PROP" and asset_type == "prop":
            filteredList.append(node)
            
    return filteredList

#To get the parents of a shape node recursively
def getParent(node):
    parentNode = cmds.listRelatives(node, allParents=True)
    if parentNode is None:
        return []
    return [parentNode[0]] + getTopParent(parentNode)  

def getListUptoFirstMeshNode(groupName):
    shapeNode = cmds.ls(groupName, dag=1, type='mesh')[0]
    parentList = getParent(shapeNode)[::-1]
    return ("").join(map(lambda node: "|"+str(node), parentList))

#To get current maya scene file
print cmds.file(q=1, sceneName=1)

#To get current maya project
print cmds.workspace(q=1, fn=1)
