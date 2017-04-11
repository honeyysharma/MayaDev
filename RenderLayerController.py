import sys
from RenderLayers import EnvirLayer, CharLayer, importRenderSetup, exportRenderSetup, getAssets


class RenderLayerController(object):
    def __init__(self):
		self.populateAssets = False
        
    def createEnvirLayer(self, layerName):
		if self.populateAssets == False:
			getAssets()
			self.populateAssets = True
		layer = EnvirLayer(layerName)
		layer.createCollectionForAllLights()
		#layer.turnOffCharLights()
		layer.turnOffAllChar(False)
		layer.createAllEnvirCollection()
		#layer.switchToLayer()
    
    def createCharLayer(self, layerName):
		if self.populateAssets == False:
			getAssets()
			self.populateAssets = True
		layer = CharLayer(layerName)
		layer.createCollectionForAllLights()
		#layer.turnOffEnvirLights()
		layer.turnOffAllEnvir(True)
		layer.createAllCharCollection()
		#layer.switchToLayer()
        
    def createCustomEnvirLayer(self, layerName, isCutoutChecked):
		if self.populateAssets == False:
			getAssets()
			self.populateAssets = True
		layer = EnvirLayer(layerName)
		layer.createCollectionForAllLights()
		#layer.turnOffCharLights()

		#toggle only Envir cutout
		layer.turnOffAllEnvir(isCutoutChecked)

		layer.createCustomEnvirCollection(isCutoutChecked)
		layer.turnOffAllChar(False)
		#layer.switchToLayer()
        
    def createCustomCharLayer(self, layerName, isCutoutChecked):
		if self.populateAssets == False:
			getAssets()
			self.populateAssets = True
		layer = CharLayer(layerName)
		layer.createCollectionForAllLights()
		#layer.turnOffEnvirLights()
		layer.turnOffAllEnvir(True)

		#toggle only Char cutout
		layer.turnOffAllChar(isCutoutChecked)

		layer.createCustomCharCollection(isCutoutChecked)
		#layer.switchToLayer()
        
    def importSetup(self, filePath):
        importRenderSetup(filePath)
        
    def exportSetup(self, filePath):
        exportRenderSetup(filePath)
