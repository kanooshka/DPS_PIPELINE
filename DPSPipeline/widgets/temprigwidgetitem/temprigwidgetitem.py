from PyQt4	    import QtGui
from PyQt4.QtGui    import QTreeWidgetItem, QComboBox, QLineEdit
from PyQt4.QtCore   import QDate,QTime,QVariant,Qt

class TempRigWidgetItem(QTreeWidgetItem):
    
    def __init__(self, parent = '', rig = ''):
        super(QTreeWidgetItem, self).__init__()
        self.rig = rig
        self.parent = parent
        
        self.parent.addTopLevelItem(self)
        
        self.types = ["NONE","Product Rig","TV Rig","Vehicle"]
        self.statuses = ["Not Started","In Progress","Finished","NEEDS ATTENTION"]
        
        self.UpdateValues()
	
	if rig is not None:
	    self.rig.rigChanged.connect(self.UpdateValues)
         
    def UpdateValues(self):
        
        #shot id
        self.setText(0,(str(self.rig._idtemprigs)))
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setFlags(self.flags() ^ Qt.ItemIsSelectable)
        
	#shot name
        self.nameLineEdit = QLineEdit()
	self.nameLineEdit.setText(str(self.rig._name))
	self.parent.setItemWidget(self,1,self.nameLineEdit)
	self.nameLineEdit.editingFinished.connect(self.nameChanged)
	
	#self._folderLocation         = _folderLocation
        
        self.setNumberLineEdit = QLineEdit()
	self.setNumberLineEdit.setText(str(self.rig._setnumber))
	validator = QtGui.QIntValidator()
        self.setNumberLineEdit.setValidator(validator)
        self.parent.setItemWidget(self,2,self.setNumberLineEdit)
        self.setNumberLineEdit.editingFinished.connect(self.setNumberChanged)
	
	
        self.typeComboBox = QComboBox()
        for t in self.types:
	    self.typeComboBox.addItem(t)
	self.parent.setItemWidget(self,3,self.typeComboBox)
	self.typeComboBox.setCurrentIndex(int(self.rig._typ))
        self.typeComboBox.currentIndexChanged.connect(self.setType)
	
        self.statusComboBox = QComboBox()
	for s in self.statuses:
	    self.statusComboBox.addItem(s)
        self.parent.setItemWidget(self,4,self.statusComboBox)
	self.statusComboBox.setCurrentIndex(int(self.rig._status))
        self.statusComboBox.currentIndexChanged.connect(self.setStatus)
	
        self.descriptionLine = QLineEdit()
        self.parent.setItemWidget(self,5,self.descriptionLine)
	if self.rig._description is not None:
	    self.descriptionLine.setText(self.rig._description)
	self.descriptionLine.editingFinished.connect(self.setDescription)
	
    def nameChanged(self):
	self.rig.setName(self.nameLineEdit.text())
    
    def setNumberChanged(self):
	self.rig.setSetNumber(self.setNumberLineEdit.text())
	
    def setType(self):
	self.rig.setType(self.typeComboBox.currentIndex())
    
    def setStatus(self):
	self.rig.setStatus(self.statusComboBox.currentIndex())
    
    def setDescription(self):
	self.rig.setDescription(self.descriptionLine.text())