import sys
from RenderLayers import EnvirLayer, CharLayer
from RenderLayers import importRenderSetup, exportRenderSetup
from RenderLayers import getAssets, getSequenceLightingDir, getSceneFileName
from RenderLayers import importLightRig, exportLightRig


class RenderLayerController(object):
    def __init__(self):
		self.populateAssets = False
    
    def populateAssetTypes(self):
		getAssets()
		
    def getSeqLightingDir(self):
		return getSequenceLightingDir()
        
    def createEnvirLayer(self, layerName):
		if self.populateAssets == False:
			getAssets()
			self.populateAssets = True
		layer = EnvirLayer(layerName)
		layer.createCollectionForAllLights()
		layer.turnOffCharLights()
		layer.turnOffAllChar(False)
		layer.createAllEnvirCollection()
    
    def createCharLayer(self, layerName):
		if self.populateAssets == False:
			getAssets()
			self.populateAssets = True
		layer = CharLayer(layerName)
		layer.createCollectionForAllLights()
		layer.turnOffEnvirLights()
		layer.turnOffAllEnvir(True)
		layer.createAllCharCollection()
        
    def createCustomEnvirLayer(self, layerName, isCutoutChecked):
		if self.populateAssets == False:
			getAssets()
			self.populateAssets = True
		layer = EnvirLayer(layerName)
		layer.createCollectionForAllLights()
		layer.turnOffCharLights()

		#toggle only Envir cutout
		layer.turnOffAllEnvir(isCutoutChecked)

		layer.createCustomEnvirCollection(isCutoutChecked)
		layer.turnOffAllChar(False)
        
    def createCustomCharLayer(self, layerName, isCutoutChecked):
		if self.populateAssets == False:
			getAssets()
			self.populateAssets = True
		layer = CharLayer(layerName)
		layer.createCollectionForAllLights()
		layer.turnOffEnvirLights()
		layer.turnOffAllEnvir(True)

		#toggle only Char cutout
		layer.turnOffAllChar(isCutoutChecked)

		layer.createCustomCharCollection(isCutoutChecked)
        
    def importSetup(self, filePath):
        importRenderSetup(filePath)
        
    def exportSetup(self):
        exportRenderSetup()
        
    def importRig(self, filePath):
        importLightRig(filePath)
        
    def exportRig(self):
        exportLightRig()
        
	def getSceneFile():
		return getSceneFileName()
