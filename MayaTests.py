"""
Get top parent using recursion
"""
def getTopParent(node):
    parentList = cmds.listRelatives(node, allParents=True)
    if parentList is None:
        return node
    
    return getTopParent(parentList[0])
    
print getTopParent(cmds.selectedNodes()[0])


"""
Get top parent using list
"""

print str(cmds.selectedNodes()[0]).strip("|").split("|")[0]
