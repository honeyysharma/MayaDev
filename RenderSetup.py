from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets
from RenderLayerController import RenderLayerController

class CustomLayerSetup(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent, renderLayerController):
        super(CustomLayerSetup, self).__init__(parent=parent)
        self.renderLayerController = renderLayerController
        self.generateUI()
        
    def generateUI(self):
        self.lblLayerName = QtWidgets.QLabel('Layer Name:')
        
        self.leLayerName = QtWidgets.QLineEdit()
        self.leLayerName.setPlaceholderText("Layer")
        
        self.lblLayerType = QtWidgets.QLabel('Layer Type:')
        
        self.comboLayerType = QtWidgets.QComboBox()
        self.comboLayerType.addItems(['ENVIR', 'CHAR'])
        
        self.cutOutCheckBox = QtWidgets.QCheckBox("With Cutouts")
        self.cutOutCheckBox.setChecked(False)
        
        self.btnAddLayer = QtWidgets.QPushButton('Add', self)
        self.btnAddLayer.move(20, 20)
        self.btnAddLayer.clicked.connect(self.createCustomLayer)
        
        #grid layout for adding custom widgets
        self.customLayerGridLayout = QtWidgets.QGridLayout()
        self.customLayerGridLayout.addWidget(self.lblLayerName, 0, 0)
        self.customLayerGridLayout.addWidget(self.leLayerName, 0, 1)
        self.customLayerGridLayout.addWidget(self.lblLayerType, 1, 0)
        self.customLayerGridLayout.addWidget(self.comboLayerType, 1, 1)
        self.customLayerGridLayout.addWidget(self.cutOutCheckBox, 2, 0)
        self.customLayerGridLayout.addWidget(self.btnAddLayer, 2, 1)
        
        self.setLayout(self.customLayerGridLayout)
            
    def createCustomLayer(self):
        if cmds.selectedNodes() is None:
            QtWidgets.QMessageBox.information(self, "Alert", "Please select assets in the Outliner!")    
        else:
            layerType = str(self.comboLayerType.currentText())
            layerName = str(self.leLayerName.text()).upper()
            parentList = list(set(map(lambda node: str(node).strip("|").split("|")[0], cmds.selectedNodes())))
            
            if layerType == "ENVIR":
                if "CHAR" in parentList:
                    QtWidgets.QMessageBox.information(self, "Alert", "CHAR type asset selected to create ENVIR layer!")
                else:
                    self.renderLayerController.createCustomEnvirLayer(layerName, self.cutOutCheckBox.isChecked())
            else:
                if "ENVIR" in parentList:
                    QtWidgets.QMessageBox.information(self, "Alert", "ENVIR type asset selected to create ENVIR layer!")
                else:
                    self.renderLayerController.createCustomCharLayer(layerName, self.cutOutCheckBox.isChecked())
        

class RenderLayerSetup(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RenderLayerSetup, self).__init__(parent=parent)
        self.showCustomLayer = 0
        self.renderLayerController = RenderLayerController()
        self.initUI()
        
    def initUI(self):
        #main layout
        vbox = QtWidgets.QVBoxLayout()
        
        #top frame
        topFrame = QtWidgets.QFrame()
        topFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        
        #bottom frame
        bottomFrame = QtWidgets.QFrame()
        bottomFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        
        #split window and add frame
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(topFrame)
        splitter.addWidget(bottomFrame)
        
        #add splitter to main layout
        vbox.addWidget(splitter)
        
        #create default layer buttons
        self.btnEnvir = QtWidgets.QPushButton('ENVIR', self)
        self.btnEnvir.move(20, 20)
        self.btnEnvir.clicked.connect(self.createEnvirLayer)
        
        self.btnChar = QtWidgets.QPushButton('CHAR', self)
        self.btnChar.move(20, 20)
        self.btnChar.clicked.connect(self.createCharLayer)
        
        self.btnCustom = QtWidgets.QPushButton('Custom', self)
        self.btnCustom.move(20, 20)
        self.btnCustom.clicked.connect(self.toggleAnimation)
        
        #self.btnCancelCustomLayer = QtGui.QPushButton('Cancel', self)
        #self.btnCancelCustomLayer.move(20, 20)
        #self.btnCancelCustomLayer.clicked.connect(self.hideCustomLayerWidget)
        
        #create grid layout to add buttons
        defaultBtnGridLayout = QtWidgets.QGridLayout()
        defaultBtnGridLayout.addWidget(self.btnEnvir, 0, 0)
        defaultBtnGridLayout.addWidget(self.btnChar, 0, 1)
        
        #set grid layout for top frame
        topFrame.setLayout(defaultBtnGridLayout)
        
        self.customLayer = CustomLayerSetup(self, self.renderLayerController)
        self.toggleAnimation()
        #vertical layout for bottom frame
        vboxCustom = QtWidgets.QVBoxLayout()
        vboxCustom.addWidget(self.btnCustom)
        vboxCustom.addWidget(self.customLayer)
        
        #set vertical layout for bottom frame
        bottomFrame.setLayout(vboxCustom)
        
        self.setLayout(vbox)
        self.setGeometry(300, 300, 300, 100)
        self.setWindowTitle('Render Layer Setup')
        self.show()
        
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
        
test = RenderLayerSetup()
