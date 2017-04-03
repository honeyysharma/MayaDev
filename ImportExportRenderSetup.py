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

def importRenderSetup(filePath):
    currentLayers = map(lambda layer: layer.name(), rs.getRenderLayers())
    
    with open(filePath, "r") as file:
        data = json.load(file)
     
    if type(data) == dict:
        importedLayers = map(lambda layer: layer["renderSetupLayer"]["name"], data['renderSetup']['renderLayers'])
        
        if currentLayers:
            [deleteLayer(layer) for layer in importedLayers if layer in currentLayers]
            rs.decode(data, renderSetup.DECODE_AND_MERGE, None)
            
    else:
        raise TypeError("Can't perform import on the file which wasn't exported using Render Layer Setup")
    

def exportRenderSetup(filePath, note = None):
    with open(filePath, "w+") as file:
        json.dump(rs.encode(note), fp=file, indent=2, sort_keys=True) 
   


importRenderSetup("/homes/sharmah/maya/Templates/s1.json")

exportRenderSetup("/homes/sharmah/maya/Templates/s1_test.json")
