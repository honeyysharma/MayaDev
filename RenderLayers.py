import maya.cmds as cmds
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.model.renderLayer as renderLayer
import maya.app.renderSetup.model.override as override
import os
import json
from sgtkLib import tkm, tkutil

__assets = {}

def isGroup(node):
    children = cmds.listRelatives(node, children=1)
    for child in children:
        if cmds.nodeType(child) != "transform":
            return False
        return True 

def getAssets():
	
	sceneFileName = os.path.basename(cmds.file(q=1, sceneName=1))
	assetCategoryFilePath = os.path.join(os.path.dirname(os.path.abspath(cmds.file(q=1, sceneName=1))), "AssetCategory.json")
	
	if not os.path.isfile(assetCategoryFilePath):
		prod = os.environ['PROD']
		tank, sgw, project = tkutil.getTk(prod, fast=True)
		filteredList = []
		
		topGroupNodes = cmds.ls(assemblies=True)
		assetNodes = filter(lambda node: isGroup(node), topGroupNodes)

		envirList = []
		charList = []
		propList = []

		for node in assetNodes:
			if "light" not in node and "LIGHT" not in node:
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
				
		global __assets 
		__assets = {"ENVIR":envirList, "CHAR":charList, "PROP":propList}
		
		with open(assetCategoryFilePath, 'w') as file:
			json.dump(__assets, file, sort_keys=True, indent=4)
			
	else:
		with open(assetCategoryFilePath, 'r') as file:
			__assets = json.load(file)
 
def assets():
    return __assets

def deleteLayer(layerName):
	layer = renderSetup.instance().getRenderLayer(layerName)
	if layer.isVisible():
		renderSetup.instance().switchToLayer(renderSetup.instance().getDefaultRenderLayer())
	renderSetup.instance().detachRenderLayer(layer)
	renderLayer.delete(layer)

def importRenderSetup(filePath):
    currentLayers = map(lambda layer: layer.name(), renderSetup.instance().getRenderLayers())
    
    with open(filePath, "r") as file:
        data = json.load(file)
     
    if type(data) == dict:
        importedLayers = map(lambda layer: layer["renderSetupLayer"]["name"], data['renderSetup']['renderLayers'])
        
        if currentLayers:            
            #take backup of exisiting render setup in the scene file dir
            sceneFileName = os.path.basename(cmds.file(q=1, sceneName=1))
            bckupFilePath = os.path.join(os.path.dirname(os.path.abspath(cmds.file(q=1, sceneName=1))), "RS_Bckup_"+sceneFileName[:sceneFileName.find(".")]+".json")
            with open(bckupFilePath, "w+") as file:
                json.dump(renderSetup.instance().encode(None), fp=file, indent=2, sort_keys=True) 

            #delete layers from render setup that are there in the imported file
            [deleteLayer(layer) for layer in importedLayers if layer in currentLayers]
            
            #import render setup
            renderSetup.instance().decode(data, renderSetup.DECODE_AND_MERGE, None)
            
    else:
        raise TypeError("Can't perform import on the file which wasn't exported using Render Layer Setup")
        
def exportRenderSetup(filePath, note = None):
    with open(filePath, "w+") as file:
        json.dump(renderSetup.instance().encode(note), fp=file, indent=2, sort_keys=True) 

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
        if assets()["ENVIR"]:
            c_allEnvir = self.layer.createCollection("c_envirAllEnvir")
            c_allEnvir.getSelector().setFilterType(0)
            #c_allEnvir.getSelector().setPattern("ENVIR*")
            c_allEnvir.getSelector().staticSelection.set(assets()["ENVIR"])
            return c_allEnvir
        
    def createAllCharCollection(self):
        """create char collection"""
        if assets()["CHAR"]:
            c_allChar = self.layer.createCollection("c_charAllChar")
            c_allChar.getSelector().setFilterType(0)
            #c_allChar.getSelector().setPattern("CHAR*")
            c_allChar.getSelector().staticSelection.set(assets()["CHAR"])
            return c_allChar
        return
        
    def turnOffAllChar(self, isCutoutChecked):
        """create collection to turn off all chars"""
        collection = self.createAllCharCollection()
        if collection is not None:
            o_charVisibility = collection.createOverride("CharVisibility", override.AbsOverride.kTypeId)
            attribute = self.getListUptoFirstMeshNode(assets()["CHAR"][0])
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
            attribute = self.getListUptoFirstMeshNode(assets()["ENVIR"][0])
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
        c_offCharLights.getSelector().setPattern("*LIGHTS_CHAR*")
        o_offCharLgtVisibility = c_offCharLights.createOverride("offCharLgtVisibility", override.AbsOverride.kTypeId)
        
        lgtCharGrp = str(cmds.ls("*LIGHTS_CHAR*")[0])
        
        o_offCharLgtVisibility.finalize(lgtCharGrp+".visibility")
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
        c_offEnvirLights.getSelector().setPattern("*LIGHTS_ENVIR*")
        o_offEnvirLgtVisibility = c_offEnvirLights.createOverride("offEnvirLgtVisibility", override.AbsOverride.kTypeId)
        
        lgtEnvGrp = str(cmds.ls("*LIGHTS_ENVIR*")[0])
        
        o_offEnvirLgtVisibility.finalize(lgtEnvGrp+".visibility")
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
