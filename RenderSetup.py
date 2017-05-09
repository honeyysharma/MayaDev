import maya.cmds as cmds
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
        
        self.btnAddLayer = QtGui.QPushButton('ADD', self)
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
				self.renderLayerController.createCustomEnvirLayer(layerType+"_"+layerName, self.cutOutCheckBox.isChecked())
            elif layerType == "CHAR":
				self.renderLayerController.createCustomCharLayer(layerType+"_"+layerName, self.cutOutCheckBox.isChecked())
        

class RenderLayerSetup(QtGui.QWidget):
    
	signal_shown = QtCore.pyqtSignal()
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
		
		#light rig frame
		lightRigFrame = QtGui.QFrame()
		lightRigFrame.setFrameShape(QtGui.QFrame.StyledPanel)

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
		splitter.addWidget(lightRigFrame)
		splitter.addWidget(topFrame)
		splitter.addWidget(middleFrame)
		splitter.setStretchFactor(1,1)
		splitter.setSizes([100,100])
		splitter.addWidget(bottomFrame)


		#add splitter to main layout
		vbox.addWidget(splitter)
		
		#create import and export light rig buttons
		self.btnExportRig = QtGui.QPushButton('Export Rig', self)
		self.btnExportRig.move(20, 20)
		self.btnExportRig.clicked.connect(self.exportLightRig)
		
		self.btnImportRig = QtGui.QPushButton('Reference Rig', self)
		self.btnImportRig.move(20, 20)
		self.btnImportRig.clicked.connect(self.importLightRig)

		#create default layer buttons
		self.btnEnvir = QtGui.QPushButton('ADD ENVIR LAYER', self)
		self.btnEnvir.move(20, 20)
		self.btnEnvir.clicked.connect(self.createEnvirLayer)

		self.btnChar = QtGui.QPushButton('ADD CHAR LAYER', self)
		self.btnChar.move(20, 20)
		self.btnChar.clicked.connect(self.createCharLayer)

		self.btnCustom = QtGui.QPushButton('...  Add More Layers ...', self)
		self.btnCustom.move(20, 20)
		self.btnCustom.clicked.connect(self.toggleAnimation)
		
		#create grid layout to add import and export light rig buttons
		rigBtnGridLayout = QtGui.QGridLayout()
		rigBtnGridLayout.addWidget(self.btnExportRig, 0, 0)
		rigBtnGridLayout.addWidget(self.btnImportRig, 0, 1)
		
		#set grid layout for light rig frame
		lightRigFrame.setLayout(rigBtnGridLayout)

		#create grid layout to add envir and char layer buttons
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
		self.btnExport = QtGui.QPushButton('EXPORT RENDER SETUP', self)
		self.btnExport.move(20, 20)
		self.btnExport.clicked.connect(self.exportRenderSetup)

		self.btnImport = QtGui.QPushButton('IMPORT RENDER SETUP', self)
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

	def exportLightRig(self):
		self.renderLayerController.exportRig()
		
	def importLightRig(self):
		seqLightDir = self.renderLayerController.getSeqLightingDir()
		filePath = QtGui.QFileDialog.getOpenFileName(self, "Referece Light Rig File", seqLightDir, "Maya ASCII (*.ma)")
		self.renderLayerController.importRig(filePath)

	def showEvent(self, event):
		super(RenderLayerSetup, self).showEvent(event)
		self.signal_shown.emit()

	def exportRenderSetup(self):
		self.renderLayerController.exportSetup()

	def importRenderSetup(self):
		seqLightDir = self.renderLayerController.getSeqLightingDir()
		filePath = QtGui.QFileDialog.getOpenFileName(self, "Import File", seqLightDir, "JSON Files (*.json)")
		self.renderLayerController.importSetup(filePath)
		


class MainRLSWindow(QtGui.QMainWindow):
	def __init__(self):
		super(MainRLSWindow, self).__init__()
		self._RLSWindow = None
		
	def showRenderLayerSetupWidget(self):
		if self._RLSWindow is None:
			self._RLSWindow = RenderLayerSetup()
		self._RLSWindow.show()
