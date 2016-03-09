import os
import glob
import ntpath

from PyQt4.QtGui    import QListWidget,QListWidgetItem,QIcon
from PyQt4.QtCore   import QSize,QThread,pyqtSignal,QString

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
                                for image in imagelist:
                                    if len(image)>3:
                                        print "Loading Shot Image: "+image
                                        self.listWidget.addImageSignal.emit(image)
                                        #sharedDB.myAttributeEditorWidget.shotWidget.shotImagePath = newImage
                                        #sharedDB.myAttributeEditorWidget.shotWidget.shotImageFound.emit(newImage)
                                    
                            except:
                                print "No Image file found for selected shot"

class RenderTimelineWidget(QListWidget):
    addImageSignal = pyqtSignal(QString)   
   
    def __init__( self, parent = None ):
        
        super(RenderTimelineWidget, self).__init__( parent )
        
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(200,200))        
        self.setResizeMode(QListWidget.Adjust)
        
        self.cfip = CheckForImages()
	self.addImageSignal.connect(self.AddImage)
        self.cfip.listWidget = self
	self.shotImageDir = ''
        
        self.project = None
        
        self.itemList = []
        
        self.itemDoubleClicked.connect(self.openImage)

    def ChangeProject(self, proj):
        #global project
        #project = proj
        if proj is not None:
            
            self.project = proj
            self.clear()
            self.itemList = []
            self.cfip.project = proj 
            
            self.cfip.start()
    
    def AddImage(self,imagepath):
        base = ntpath.basename(str(imagepath))
        base = os.path.splitext(base)[0]
       
        currItem = QListWidgetItem(QIcon(imagepath),base)
        self.addItem(currItem);
        currItem.path = imagepath
        self.itemList.append(currItem)
        
        self.sortItems()
        
    def openImage(self, qitem):
        try:
            os.startfile(qitem.path)
        except:
            print "Unable to open image"