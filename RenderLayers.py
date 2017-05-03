import maya.cmds as cmds
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.model.renderLayer as renderLayer
import maya.app.renderSetup.model.override as override
import os
import json
from sgtkLib import tkm, tkutil

__assets = {}
__seq = ""
__shot = ""
__tank = ""

def isGroup(node):
    children = cmds.listRelatives(node, children=1)
    for child in children:
        if cmds.nodeType(child) != "transform":
            return False
        return True 

def getShotgunTank():
	prod = os.environ['PROD']
	tank, sgw, project = tkutil.getTk(prod, fast=True)
	return tank,sgw,project

def getAssets():
	global __tank
	
	__tank,sgw,project = getShotgunTank()
	
	scene_file = cmds.file(q=True,exn=True)
	tpl = __tank.template_from_path(scene_file)
	
	global __seq
	__seq = tpl.get_fields(scene_file)['Sequence']
	
	filteredList = []
	
	assetNodes = cmds.ls(assemblies=True, ro=True)
	#assetNodes = filter(lambda node: isGroup(node), topGroupNodes)

	envirList = []
	charList = []
	propList = []

	for node in assetNodes:
		if "light" not in node and "LIGHT" not in node:
			filename = cmds.referenceQuery(node, filename=True)

			ctx =  __tank.context_from_path(filename)
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
 
def assets():
    return __assets
	
def getSequenceLightingDir():
	global __tank
	global __seq
	
	if __tank == "":
		__tank,sgw,project = getShotgunTank()
		scene_file = cmds.file(q=True,exn=True)
		tpl = __tank.template_from_path(scene_file)
		__seq = tpl.get_fields(scene_file)['Sequence']

	#__seq = "seq_test"
	seqLightingDir = os.path.join("/s", "prods", "dinner", "sequence", __seq, "common", "light")
	if not os.path.exists(seqLightingDir):
		os.mkdir(seqLightingDir)

	return seqLightingDir

def getSceneFileName():
	return os.path.basename(cmds.file(q=1, sceneName=1))

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
			sceneFileName = getSceneFileName()
			bckupFilePath = os.path.join(os.path.dirname(os.path.abspath(cmds.file(q=1, sceneName=1))), "RS_Bckup_"+sceneFileName[:sceneFileName.find(".")]+".json")
			with open(bckupFilePath, "w+") as file:
				json.dump(renderSetup.instance().encode(None), fp=file, indent=2, sort_keys=True) 

			#delete layers from render setup that are there in the imported file
			[deleteLayer(layer) for layer in importedLayers if layer in currentLayers]

		#import render setup
		renderSetup.instance().decode(data, renderSetup.DECODE_AND_MERGE, None)   
	   
	else:
		raise TypeError("Can't perform import on the file which wasn't exported using Render Layer Setup")
        
def exportRenderSetup():
	sceneName = getSceneFileName()
	sceneName = sceneName[:sceneName.find(".")]
	filePath = os.path.join(getSequenceLightingDir(), sceneName+"_rls"+".json")
	
	with open(filePath, "w+") as file:
		json.dump(renderSetup.instance().encode(None), fp=file, indent=2, sort_keys=True)
		
	cmds.confirmDialog(title='Information', message="Render Setup exported to "+filePath, button=['OK'], defaultButton='OK')
		
def importLightRig(filePath):
	cmds.file(str(filePath), mergeNamespacesOnClash=True, reference=True, prompt=False)
	
def exportLightRig():
	
	if cmds.selectedNodes():
		sceneName = getSceneFileName()
		sceneName = sceneName[:sceneName.find(".")]
		filePath = os.path.join(getSequenceLightingDir(), sceneName+"_rig")
		cmds.file(filePath, f=True, exportSelected=True, type="mayaAscii")
		cmds.confirmDialog(title='Information', message="Rig exported to "+filePath, button=['OK'], defaultButton='OK')
	else:
		cmds.confirmDialog(title='Alert', message="LIGHTS not selected in the Outliner!", button=['OK'], defaultButton='OK')


class Layer(object):
    def __init__(self, layerName):
		self.createLightsGroups()
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
            
    def createLightsGroups(self):
		if "LIGHTS" not in cmds.ls(type="transform"):
			grpLgtChar = cmds.group(n='LIGHTS_CHAR', em=True)
			grpLgtEnvir = cmds.group(n='LIGHTS_ENVIR', em=True)
			cmds.select([grpLgtChar, grpLgtEnvir])
			cmds.group(n="LIGHTS")
        
    def createCollectionForAllLights(self):
        c_allLights = self.layer.createCollection("c_AllLights")
        c_allLights.getSelector().setFilterType(0)
        c_allLights.getSelector().setPattern("*LIGHTS*")
        
    def createAllEnvirCollection(self):
        """create envir collection"""
        if assets()["ENVIR"]:
            c_allEnvir = self.layer.createCollection("c_envirAllEnvir")
            c_allEnvir.getSelector().setFilterType(0)
            c_allEnvir.getSelector().staticSelection.set(assets()["ENVIR"])
            return c_allEnvir
        
    def createAllCharCollection(self):
        """create char collection"""
        if assets()["CHAR"]:
            c_allChar = self.layer.createCollection("c_charAllChar")
            c_allChar.getSelector().setFilterType(0)
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
        
    def getTopParentOfSelectedNodes(self, nodes):
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

