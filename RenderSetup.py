from PyQt4 import QtCore, QtGui
from RenderLayerController import RenderLayerController
import sys

class CustomLayerSetup(QtGui.QWidget):
    def __init__(self, parent, renderLayerController):
        QtGui.QWidget.__init__(self, parent)
        self.renderLayerController = renderLayerController
        self.generateUI()
        
    def generateUI(self):
        self.lblLayerName = QtGui.QLabel('Layer Name:')
        
        self.leLayerName = QtGui.QLineEdit()
        self.leLayerName.setPlaceholderText("Layer")
        
        self.lblLayerType = QtGui.QLabel('Layer Type:')
        
        self.comboLayerType = QtGui.QComboBox()
        self.comboLayerType.addItems(['ENVIR', 'CHAR'])
        
        self.cutOutCheckBox = QtGui.QCheckBox("With Cutouts")
        self.cutOutCheckBox.setChecked(False)
        
        self.btnAddLayer = QtGui.QPushButton('Add', self)
        self.btnAddLayer.move(20, 20)
        self.btnAddLayer.clicked.connect(self.createCustomLayer)
        
        #grid layout for adding custom widgets
        self.customLayerGridLayout = QtGui.QGridLayout()
        self.customLayerGridLayout.addWidget(self.lblLayerName, 0, 0)
        self.customLayerGridLayout.addWidget(self.leLayerName, 0, 1)
        self.customLayerGridLayout.addWidget(self.lblLayerType, 1, 0)
        self.customLayerGridLayout.addWidget(self.comboLayerType, 1, 1)
        self.customLayerGridLayout.addWidget(self.cutOutCheckBox, 2, 0)
        self.customLayerGridLayout.addWidget(self.btnAddLayer, 2, 1)
        
        self.setLayout(self.customLayerGridLayout)
            
    def createCustomLayer(self):
        if cmds.selectedNodes() is None:
            QtGui.QMessageBox.information(self, "Alert", "Please select assets in the Outliner!")    
        else:
            layerType = str(self.comboLayerType.currentText())
            layerName = str(self.leLayerName.text()).upper()
            
            if layerType == "ENVIR":
				self.renderLayerController.createCustomEnvirLayer(layerType+":"+layerName, self.cutOutCheckBox.isChecked())
            elif layerType == "CHAR":
				self.renderLayerController.createCustomCharLayer(layerType+":"+layerName, self.cutOutCheckBox.isChecked())
        

class RenderLayerSetup(QtGui.QWidget):
    
    def __init__ (self):
        super(RenderLayerSetup, self).__init__ ()
        
        self._RLSWindow = None
        self.renderLayerController = RenderLayerController()
        
        self.showCustomLayer = 0
        self.customLayer = CustomLayerSetup(self, self.renderLayerController)
        self.toggleAnimation()
        
        self.initUI()
        
    def initUI(self):
        #main layout
        vbox = QtGui.QVBoxLayout()
        
        #top frame
        topFrame = QtGui.QFrame()
        topFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        
        #middle frame
        middleFrame = QtGui.QFrame()
        middleFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        
        #bottom frame
        bottomFrame = QtGui.QFrame()
        bottomFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        
        #split window and add frame
        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(topFrame)
        splitter.addWidget(middleFrame)
        splitter.setStretchFactor(1,1)
        splitter.setSizes([100,100])
        splitter.addWidget(bottomFrame)

        
        #add splitter to main layout
        vbox.addWidget(splitter)
        
        #create default layer buttons
        self.btnEnvir = QtGui.QPushButton('ENVIR', self)
        self.btnEnvir.move(20, 20)
        self.btnEnvir.clicked.connect(self.createEnvirLayer)
        
        self.btnChar = QtGui.QPushButton('CHAR', self)
        self.btnChar.move(20, 20)
        self.btnChar.clicked.connect(self.createCharLayer)
        
        self.btnCustom = QtGui.QPushButton('...  Add More Layers ...', self)
        self.btnCustom.move(20, 20)
        self.btnCustom.clicked.connect(self.toggleAnimation)
        
        #create grid layout to add buttons
        defaultBtnGridLayout = QtGui.QGridLayout()
        defaultBtnGridLayout.addWidget(self.btnEnvir, 0, 0)
        defaultBtnGridLayout.addWidget(self.btnChar, 0, 1)
        
        #set grid layout for top frame
        topFrame.setLayout(defaultBtnGridLayout)
        
        
        #vertical layout for bottom frame
        vboxCustom = QtGui.QVBoxLayout()
        vboxCustom.addWidget(self.btnCustom)
        vboxCustom.addWidget(self.customLayer)
        
        #set vertical layout for bottom frame
        middleFrame.setLayout(vboxCustom)
        
        
        #create import export buttons
        self.btnExport = QtGui.QPushButton('EXPORT', self)
        self.btnExport.move(20, 20)
        self.btnExport.clicked.connect(self.exportRenderSetup)
        
        self.btnImport = QtGui.QPushButton('IMPORT', self)
        self.btnImport.move(20, 20)
        self.btnImport.clicked.connect(self.importRenderSetup)
        
        #create grid layout to add import export buttons
        imExpBtnsGridLayout = QtGui.QGridLayout()
        imExpBtnsGridLayout.addWidget(self.btnExport, 0, 0)
        imExpBtnsGridLayout.addWidget(self.btnImport, 0, 1)
        
        #set grid layout for bottom frame
        bottomFrame.resize(100,100)
        bottomFrame.setLayout(imExpBtnsGridLayout)
        
        self.setLayout(vbox)
        self.setGeometry(300, 300, 300, 100)
        self.setWindowTitle('Render Layer Setup')
        #self.show()
   
    def toggleAnimation(self):
        self.animation = QtCore.QPropertyAnimation(self.customLayer, "maximumHeight")
        
        if self.showCustomLayer == 0:
            self.animation.setDuration(300)
            self.animation.setStartValue(100)
            self.animation.setEndValue(0)
            self.animation.start()
            self.showCustomLayer = 1
        else:
            self.animation.setDuration(300)
            self.animation.setStartValue(0)
            self.animation.setEndValue(100)
            self.animation.start()
            self.showCustomLayer = 0
   
    def createEnvirLayer(self):
        self.renderLayerController.createEnvirLayer("ENVIR")
        
    def createCharLayer(self):
        self.renderLayerController.createCharLayer("CHAR")
        
    def populateAssets(self):
        self.renderLayerController.populateAssetTypes()
        
    def exportRenderSetup(self):
        templateDir = "/homes/sharmah/maya/Templates/"
        filename = QtGui.QFileDialog.getSaveFileName(self, "Export File", templateDir, "JSON Files (*.json)")
        filePath = filename
        self.renderLayerController.exportSetup(filePath)
        
        
    def importRenderSetup(self):
        templateDir = "/homes/sharmah/maya/Templates/"
        filename = QtGui.QFileDialog.getOpenFileName(self, "Import File", templateDir, "JSON Files (*.json)")
        filePath = filename
        self.renderLayerController.importSetup(filePath)
		


class MainRLSWindow(QtGui.QMainWindow):
	def __init__(self):
		super(MainRLSWindow, self).__init__()
		self._RLSWindow = None
		
	def showRenderLayerSetupWidget(self):
		if self._RLSWindow is None:
			self._RLSWindow = RenderLayerSetup()
		self._RLSWindow.show()
		#timer = QtCore.QTimer()
		#timer.singleShot(0,myapp.onQApplicationStarted)
	
	def getAssetTypes(self):
		self._RLSWindow.populateAssets()
