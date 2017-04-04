import maya.cmds as cmds
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.model.override as override
import os
from sgtkLib import tkm, tkutil


def isGroup(node):
    children = cmds.listRelatives(node, children=1)
    for child in children:
        if cmds.nodeType(child) != "transform":
            return False
        return True 

def getAssets():
    prod = os.environ['PROD']
    tank, sgw, project = tkutil.getTk(prod, fast=True)
    filteredList = []
    
    topGroupNodes = cmds.ls(assemblies=True)
    assetNodes = filter(lambda node: isGroup(node), topGroupNodes)

    envirList = []
    charList = []
    propList = []

    for node in assetNodes:
        filename = cmds.referenceQuery(node, filename=True)

        ctx =  tank.context_from_path(filename)
        entity = ctx.entity
        asset_name = str(entity['name'])

        asset = sgw.Asset(asset_name, project=project)
        asset_type = asset.sg_asset_type

        if asset_type == "environment":
            envirList.append(node)
        elif asset_type == "character":
            if "shot_cam" not in node:
                charList.append(node)
        elif asset_type == "prop":
            propList.append(node)
            
    assetsDict = {"ENVIR":envirList, "CHAR":charList, "PROP":propList}
    return assetsDict
    
assets = getAssets()

class Layer(object):
    def __init__(self, layerName):
        self.layerName = layerName
        self.renderSetupInstance = renderSetup.instance()
        self.layer = self.renderSetupInstance.createRenderLayer(self.layerName)
        
    def getParent(self, node):
        parentNode = cmds.listRelatives(node, allParents=True)
        if parentNode is None:
            return []
        return [parentNode[0]] + self.getParent(parentNode)  
    
    def getListUptoFirstMeshNode(self, groupName):
        shapeNode = cmds.ls(groupName, dag=1, type='mesh')[0]
        parentList = self.getParent(shapeNode)[::-1]
        return ("").join(map(lambda node: "|"+str(node), parentList))+"|"+shapeNode
        
    def createCollectionForAllLights(self):
        c_allLights = self.layer.createCollection("c_AllLights")
        c_allLights.getSelector().setFilterType(4)
        c_allLights.getSelector().setPattern("*")
        
    def createAllEnvirCollection(self):
        """create envir collection"""
        if assets["ENVIR"]:
            c_allEnvir = self.layer.createCollection("c_envirAllEnvir")
            c_allEnvir.getSelector().setFilterType(0)
            #c_allEnvir.getSelector().setPattern("ENVIR*")
            c_allEnvir.getSelector().staticSelection.set(assets["ENVIR"])
            return c_allEnvir
        
    def createAllCharCollection(self):
        """create char collection"""
        if assets["CHAR"]:
            c_allChar = self.layer.createCollection("c_charAllChar")
            c_allChar.getSelector().setFilterType(0)
            #c_allChar.getSelector().setPattern("CHAR*")
            c_allChar.getSelector().staticSelection.set(assets["CHAR"])
            return c_allChar
        return
        
    def turnOffAllChar(self, isCutoutChecked):
        """create collection to turn off all chars"""
        collection = self.createAllCharCollection()
        if collection is not None:
            o_charVisibility = collection.createOverride("CharVisibility", override.AbsOverride.kTypeId)
            attribute = self.getListUptoFirstMeshNode(assets["CHAR"][0])
            if isCutoutChecked == True:
                o_charVisibility.finalize(attribute+".aiMatte")
                o_charVisibility.setAttrValue(1)
            else:
                o_charVisibility.finalize(attribute+".primaryVisibility")
                o_charVisibility.setAttrValue(0)

        
        
    def turnOffAllEnvir(self, isCutoutChecked):
        """create collection to turn off all envir"""
        #if cmds.objExists("ENVIR"):
        collection = self.createAllEnvirCollection()
        if collection is not None:
            o_envirVisibility = collection.createOverride("EnvirVisibility", override.AbsOverride.kTypeId)
            attribute = self.getListUptoFirstMeshNode(assets["ENVIR"][0])
            if isCutoutChecked == True:
                o_envirVisibility.finalize(attribute+".aiMatte")
                o_envirVisibility.setAttrValue(1)
            else:
                o_envirVisibility.finalize(attribute+".primaryVisibility")
                o_envirVisibility.setAttrValue(0)
        
        
    def switchToLayer(self):
        """set render layer visible"""
        self.renderSetupInstance.switchToLayer(self.layer)
        
    def getTopParentOfSelectedNodes(nodes):
        return list(set(map(lambda node: str(node).strip("|").split("|")[0], nodes)))
        
class EnvirLayer(Layer):
    
    def __init__(self, layerName):
        super(EnvirLayer, self).__init__(layerName)
        
    def turnOffCharLights(self):
        """turn off char lights in envir"""
        c_offCharLights = self.layer.createCollection("c_OffCharLights")
        c_offCharLights.getSelector().setFilterType(4)
        c_offCharLights.getSelector().setPattern("LIGHTS:LIGHTS_CHAR*")
        o_offCharLgtVisibility = c_offCharLights.createOverride("offCharLgtVisibility", override.AbsOverride.kTypeId)
        o_offCharLgtVisibility.finalize("LIGHTS:LIGHTS_CHAR.visibility")
        o_offCharLgtVisibility.setAttrValue(0)
        
    def createCustomEnvirCollection(self, isCutoutChecked):
        """create custom envir collection"""
        c_customEnvir = self.layer.createCollection("c_envirCustomEnvir")
        c_customEnvir.getSelector().setFilterType(0)
        c_customEnvir.getSelector().setPattern((",").join(cmds.selectedNodes()))
        o_customEnvirVisibility = c_customEnvir.createOverride("customEnvirVisibility", override.AbsOverride.kTypeId)
        attribute = self.getListUptoFirstMeshNode(cmds.selectedNodes()[0])
        if isCutoutChecked == True:
            o_customEnvirVisibility.finalize(attribute+".aiMatte")
            o_customEnvirVisibility.setAttrValue(0)
        else:
            o_customEnvirVisibility.finalize(attribute+".primaryVisibility")
            o_customEnvirVisibility.setAttrValue(1)

class CharLayer(Layer):
    
    def __init__(self, layerName):
        super(CharLayer, self).__init__(layerName)
        
    def turnOffEnvirLights(self):
        """turn off envir lights in char"""
        c_offEnvirLights = self.layer.createCollection("c_OffEnvirLights")
        c_offEnvirLights.getSelector().setFilterType(4)
        c_offEnvirLights.getSelector().setPattern("LIGHTS:LIGHTS_ENVIR*")
        o_offEnvirLgtVisibility = c_offEnvirLights.createOverride("offEnvirLgtVisibility", override.AbsOverride.kTypeId)
        o_offEnvirLgtVisibility.finalize("LIGHTS:LIGHTS_ENVIR.visibility")
        o_offEnvirLgtVisibility.setAttrValue(0)
        
    def createCustomCharCollection(self, isCutoutChecked):
        """create collection custom char collection"""
        c_customChar = self.layer.createCollection("c_customCharAllChar")
        c_customChar.getSelector().setFilterType(0)
        c_customChar.getSelector().setPattern((",").join(cmds.selectedNodes()))
        o_customCharVisibility = c_customChar.createOverride("customCharVisibility", override.AbsOverride.kTypeId)
        attribute = self.getListUptoFirstMeshNode(cmds.selectedNodes()[0])
        if isCutoutChecked == True:
            o_customCharVisibility.finalize(attribute+".aiMatte")
            o_customCharVisibility.setAttrValue(0)
        else:
            o_customCharVisibility.finalize(attribute+".primaryVisibility")
            o_customCharVisibility.setAttrValue(1)
            
"""           
def createEnvirLayer(layerName):
    layer = EnvirLayer(layerName)
    layer.createCollectionForAllLights()
    #layer.turnOffCharLights()
    layer.turnOffAllChar(False)
    layer.createAllEnvirCollection()
    #layer.switchToLayer()     #-------- Throwing RuntimeError----------#
    
def createCharLayer(layerName):
    layer = CharLayer(layerName)
    layer.createCollectionForAllLights()
    #layer.turnOffEnvirLights()
    layer.turnOffAllEnvir(False)
    layer.createAllCharCollection()
    #layer.switchToLayer()
    
def createCustomEnvirLayer(layerName, isCutoutChecked):
    layer = EnvirLayer(layerName)
    layer.createCollectionForAllLights()
    #layer.turnOffCharLights()
    
    #toggle only Envir cutout
    layer.turnOffAllEnvir(isCutoutChecked)
    
    layer.createCustomEnvirCollection(isCutoutChecked)
    layer.turnOffAllChar(False)
    #layer.switchToLayer()

def createCustomCharLayer(layerName, isCutoutChecked):
    layer = CharLayer(layerName)
    layer.createCollectionForAllLights()
    #layer.turnOffEnvirLights()
    layer.turnOffAllEnvir(True)
    
    #toggle only Char cutout
    layer.turnOffAllChar(isCutoutChecked)
    
    layer.createCustomCharCollection(isCutoutChecked)
    #layer.switchToLayer()

createEnvirLayer("ENVIR")
createCharLayer("CHAR")
createCustomEnvirLayer("Tree", False)
createCustomCharLayer("Shirt", False)
"""
