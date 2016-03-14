import os
import glob
import ntpath

import sharedDB

from PyQt4.QtGui    import QListWidget,QListWidgetItem,QIcon,QImage,QPixmap
from PyQt4.QtCore   import QSize,QThread,pyqtSignal,QString,Qt

#project = None

class CheckForImages(QThread):

    def run(self):
	#search for image

        if self.project is not None:

            proj = self.project
            
            if proj._folderLocation is not None:
                if len(proj._folderLocation)>3:
                    sequences = self.project._sequences.values()
                    
                    for seq in sequences:
                        
                        shots = seq._shots.values()
                        for shot in shots:
                            
                            d = str(proj._folderLocation+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\img\\renders\\")	   

                            try:
                                imagelist = glob.iglob(os.path.join(d, '*.[Jj][Pp]*[Gg]'))
                                for imagepath in imagelist:
                                    if len(imagepath)>3:
                                        print "Loading Shot Image: "+imagepath
                                        
					#base = ntpath.basename(str(imagepath))
					#base = os.path.splitext(base)[0]
				       
					qimg = QImage()
					qimg.load(imagepath)
					
					#currItem = QListWidgetItem(QIcon(imagepath),base)
					
					#currItem.path = imagepath
					#self.listWidget.itemList.append(currItem)					
					self.listWidget.addImageSignal.emit(qimg,imagepath,str(shot.id()))
                                    
                            except:
                                print "No Image file found for selected shot"

class RenderTimelineWidget(QListWidget):
    addImageSignal = pyqtSignal(QImage,QString,QString)   
   
    def __init__( self, parent = None ,sizeSlider = ''):
        
        super(RenderTimelineWidget, self).__init__( parent )
        
        self.setViewMode(QListWidget.IconMode)
	self.sizeSlider = sizeSlider
        self.updateIconSize()
	self.sizeSlider.valueChanged.connect(self.updateIconSize)
	
        self.setResizeMode(QListWidget.Adjust)
        
        self.cfip = CheckForImages()
	self.addImageSignal.connect(self.AddImage)
        self.cfip.listWidget = self
	self.shotImageDir = ''
        
        self.project = None
        
        self.itemList = []
        
	self.setSelectionMode(self.NoSelection)
	self.setVerticalScrollMode(self.ScrollPerItem)
        #self.itemDoubleClicked.connect(self.openImage)
	self.itemClicked.connect(self.selectShot)

    def ChangeProject(self, proj):
        #global project
        #project = proj
        if proj is not None:
            
            self.project = proj
            self.clear()
            self.itemList = []
            self.cfip.project = proj 
            
            self.cfip.start()
    
    def AddImage(self,image,imagepath,shotid):
 	base = ntpath.basename(str(imagepath))
        base = os.path.splitext(base)[0]
       
        currItem = QListWidgetItem(QIcon(QPixmap(image)),base)        
        currItem.path = imagepath
	currItem.shot = sharedDB.myShots[str(shotid)]
        self.itemList.append(currItem)

        self.addItem(currItem);
        self.sortItems()
    '''
    def openImage(self, qitem):
        try:
            os.startfile(qitem.path)
        except:
            print "Unable to open image"
    '''    
    def selectShot(self,item):
	sharedDB.sel.select([item.shot])
    
    def updateIconSize(self):
	self.setIconSize(QSize(self.sizeSlider.value(),self.sizeSlider.value()))