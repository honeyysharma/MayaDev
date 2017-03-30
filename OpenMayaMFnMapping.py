import maya.api.OpenMaya as OpenMaya
import maya.cmds as cmds

out = {}
for name in dir(OpenMaya.MFn):
    value = getattr(OpenMaya.MFn, name)
    if name.startswith('k'):
        out.setdefault(value, []).append(name)
        
        
print out[453]
