import sys
from RenderLayers import EnvirLayer, CharLayer, importRenderSetup, exportRenderSetup, getAssets


class RenderLayerController(object):
    def __init__(self):
        getAssets()
        
    def createEnvirLayer(self, layerName):
        layer = EnvirLayer(layerName)
        layer.createCollectionForAllLights()
        #layer.turnOffCharLights()
        layer.turnOffAllChar(False)
        layer.createAllEnvirCollection()
        layer.switchToLayer()
    
    def createCharLayer(self, layerName):
        layer = CharLayer(layerName)
        layer.createCollectionForAllLights()
        #layer.turnOffEnvirLights()
        layer.turnOffAllEnvir(True)
        layer.createAllCharCollection()
        layer.switchToLayer()
        
    def createCustomEnvirLayer(self, layerName, isCutoutChecked):
        layer = EnvirLayer(layerName)
        layer.createCollectionForAllLights()
        #layer.turnOffCharLights()
        
        #toggle only Envir cutout
        layer.turnOffAllEnvir(isCutoutChecked)
        
        layer.createCustomEnvirCollection(isCutoutChecked)
        layer.turnOffAllChar(False)
        layer.switchToLayer()
        
    def createCustomCharLayer(self, layerName, isCutoutChecked):
        layer = CharLayer(layerName)
        layer.createCollectionForAllLights()
        #layer.turnOffEnvirLights()
        layer.turnOffAllEnvir(True)
        
        #toggle only Char cutout
        layer.turnOffAllChar(isCutoutChecked)
        
        layer.createCustomCharCollection(isCutoutChecked)
        layer.switchToLayer()
        
    def importSetup(self, filePath):
        importRenderSetup(filePath)
        
    def exportSetup(self, filePath):
        exportRenderSetup(filePath)
