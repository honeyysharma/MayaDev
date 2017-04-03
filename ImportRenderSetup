import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.model.renderLayer as renderLayer
import json

rs = renderSetup.instance()

def deleteLayer(layerName):
    layer = rs.getRenderLayer(layerName)
    if layer.isVisible():
        rs.switchToLayer(rs.getDefaultRenderLayer())
    rs.detachRenderLayer(layer)
    renderLayer.delete(layer)
    
    
def getRenderLayersFromFile(filePath):
    with open(filePath, "r") as file:
        data = json.load(file)
        
    return map(lambda layer: layer["renderSetupLayer"]["name"], data['renderSetup']['renderLayers'])
    

def importAllFromFile(filePath):
    currentLayers = map(lambda layer: layer.name(), rs.getRenderLayers())
    importedLayers = getRenderLayersFromFile(filePath)
    if currentLayers:
        [deleteLayer(layer) for layer in importedLayers if layer in currentLayers]
    
    with open(filePath, "r") as file:
        renderSetup.instance().decode(json.load(file), renderSetup.DECODE_AND_MERGE, None)
    
    
importAllFromFile("/homes/sharmah/maya/Templates/s3_v001.json")
