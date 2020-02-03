########################
# © InValidFire, 2020  #
########################
import sys, shutil, os, httplib2, time
from datetime import datetime
#pyqt, this cursed thing...
from PyQt5 import QtWidgets, uic, QtCore, Qt
#xml interpreting
import xml.etree.ElementTree as ET
# google drive auth stuff
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
connection = True
try:
    gauth.LocalWebserverAuth()
except httplib2.ServerNotFoundError:
    print("No Connection!")
    connection = False
except TimeoutError:
    print("No Connection!")
    connection = False

drive = GoogleDrive(gauth)
    
app = QtWidgets.QApplication(sys.argv)
class Main(QtWidgets.QMainWindow):
    global connection
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.show()
        self.home = os.getcwd()
        self.devicesavedict = {}
        self.drivesavedict = {}
        self.selectedItems = []
        self.selectedStorage = ""
        self.setup()
        self.drivefolderid = None
        self.localsaves()
        self.drivesetup()
        self.drivesaves()
    
    #creates temp folder for google drive downloads
    def setup(self):
        if(os.path.exists(self.home+"\\sss_temp")):
            pass
        else:
            os.mkdir(self.home+"\\sss_temp")

    #processes Stardew Save XML files, pulling what we need (player name and in-game date)
    def xmlprocess(self,filename,folder):
        savefile = ET.parse(filename)
        root = savefile.getroot()
        playername = root[0][0].text
        gameday = root[0].find('dayOfMonthForSaveGame').text
        gameseason = root[0].find('seasonForSaveGame').text
        seasons = { #gives the season a friendly name
            0: "Spring",
            1: "Summer",
            2: "Fall",
            3: "Winter",
        }
        gameseason = seasons.get(int(gameseason),"error") #switch case, except not really! :c
        gameyear = root[0].find('yearForSaveGame').text
        gametime = gameseason+" "+gameday+" Year "+gameyear
        hoursplayed = int((int(root[0].find('millisecondsPlayed').text)/1000)/60/60)
        minutesplayed = int((int(root[0].find('millisecondsPlayed').text)/1000)/60)
        timeplayed = str(hoursplayed)+":"+str(minutesplayed)
        result = {}
        result["name"] = playername
        result["time"] = gametime
        result["file"] = folder
        result["play"] = timeplayed
        print(result)
        return result
    
    #loads all local saves and sends them to be processed
    def localsaves(self):
        if(not os.path.exists(os.path.expanduser("~")+"\\AppData\Roaming\StardewValley\Saves")):
            print("Stardew Valley save folder not found")
            return
        saveList = os.listdir(os.path.expanduser("~")+"\\AppData\Roaming\StardewValley\Saves")
        tempList = []
        for i in saveList:
            tlist = []
            save = self.xmlprocess(os.path.expanduser("~")+"\\AppData\Roaming\StardewValley\Saves\\"+i+"\\"+i,i)
            print("Save: "+str(save))
            self.devicesavedict[save["file"]] = save
            for key, value in save.items():
                tlist.append(value)
            tempList.append(QtWidgets.QTreeWidgetItem(tlist))
        self.treeWidgetLocal.addTopLevelItems(tempList)
    
    # drive folder setup
    def drivesetup(self):
        global connection
        print("drivesetupConnection = "+str(connection))
        print("drivesetupdrivefolderid="+str(self.drivefolderid))
        if(connection == True):
            try:
                file_list = drive.ListFile({'q':"'root' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed=false"}).GetList()
                for item in file_list:
                    if(item.get('title')=='StardewSaveSync'):
                        self.drivefolderid = item.get('id')
                        print("Found folder with id: "+self.drivefolderid)
                        break
                if(self.drivefolderid==None):
                    folder = drive.CreateFile({'title': 'StardewSaveSync','mimeType':"application/vnd.google-apps.folder"})
                    folder.Upload() # Upload the file.
                    self.drivefolderid = folder.get('id')
            except httplib2.ServerNotFoundError as err:
                print("No Connection!")
                connection = False
        
    def upload(self,dir):
        folderid = None
        file_list = drive.ListFile({'q':"'"+self.drivefolderid+"' in parents and title='"+dir+"' and mimeType = 'application/vnd.google-apps.folder' and trashed=false"}).GetList()
        for folder in file_list:
            if(folder.get('title') == dir):
                folderid = folder.get('id')
        if folderid == None:
            folder = drive.CreateFile({'title': dir, 'parents': [{'id':self.drivefolderid}], 'mimeType': 'application/vnd.google-apps.folder'})
            folder.Upload()
            folderid = folder.get('id')
        print("Uploading directory "+dir+" to Google Drive")
        print(os.listdir(os.path.expanduser("~")+"\\AppData\Roaming\StardewValley\Saves\\"+dir))
        for item in os.listdir(os.path.expanduser("~")+"\\AppData\Roaming\StardewValley\Saves\\"+dir):
            file1 = drive.CreateFile({'parents': [{'id':folderid}], 'title': item})
            file1.SetContentFile(os.path.expanduser("~"+"\\AppData\Roaming\StardewValley\Saves\\"+dir+'\\'+item))
            file1.Upload()
            print("Uploaded "+file1['title'])

    def download(self,dir):
        print("Downloading directory "+dir+" from Google Drive")
        file_list = drive.ListFile({'q':"'"+self.drivefolderid+"' in parents and title='"+dir+"' and mimeType = 'application/vnd.google-apps.folder' and trashed=false"}).GetList()
        for folder in file_list:
            save_folder = drive.ListFile({'q':"'"+folder.get('id')+"' in parents"}).GetList()
            if(os.path.exists(os.path.expanduser("~")+"\\AppData\Roaming\StardewValley\Saves\\"+folder.get('title'))):
                pass
            else:
                os.mkdir(os.path.expanduser("~")+"\\AppData\Roaming\StardewValley\Saves\\"+folder.get('title'))
            for save in save_folder:
                save.GetContentFile(os.path.expanduser("~")+"\\AppData\Roaming\StardewValley\Saves\\"+folder.get('title')+'\\'+save.get('title'))
            print("downloaded "+folder.get('title')+" to location "+os.path.expanduser("~")+"\\AppData\Roaming\StardewValley\Saves\\")
    
    #REWRITE, MAKE MORE PYTHONIC
    #loads all drive saves and sends them to be processed
    # EXPLANATION: 
    #save_folder = list of files in each folder within StardewSaveSync
    #saveList = list of files to be processed by xmlprocess
    #           - pulls from the files downloaded from the save_folder
    def drivesaves(self):
        global connection
        print("drivesavesConnection = "+str(connection))
        if(connection == True):
            #lastEdited = {}
            print("Searching folder "+self.drivefolderid+" for saves.")
            file_list = drive.ListFile({'q':"'"+self.drivefolderid+"' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed=false"}).GetList()
            if(len(file_list)==0):
                print("No saves found in the cloud.")
            for folder in file_list: #for each folder in the StardewSaveSync
                save_folder = drive.ListFile({'q':"'"+folder.get('id')+"' in parents"}).GetList()
                if(os.path.exists(self.home+"\\sss_temp"+"\\"+folder.get('title'))): #makes save folder if it doesn't exist
                    pass
                else:
                    os.mkdir(self.home+"\\sss_temp"+"\\"+folder.get('title'))
                for save in save_folder: #downloads each save into the save's folder
                    save.GetContentFile("sss_temp\\"+folder.get('title')+"\\"+save.get('title'))
                print("temp'd "+folder.get('title'))
            saveList = os.listdir(self.home+"\\sss_temp")
            tempList = []
            for i in saveList:
                tlist = []
                save = self.xmlprocess(self.home+"\\sss_temp\\"+i+"\\"+i,i)
                self.drivesavedict[save["file"]] = save
                for key, value in save.items():
                    tlist.append(value)
                tempList.append(QtWidgets.QTreeWidgetItem(tlist))
                print("added file: "+str(save))
            self.treeWidgetDrive.addTopLevelItems(tempList)
    
    def compare(self): #responsible for building instruction dict for general sync
        print("Comparing!")
        print("Device: "+str(self.devicesavedict))
        print("Drive: "+str(self.drivesavedict))
        self.instructdict = {}
        for key in self.devicesavedict.keys():
            if(key in self.drivesavedict.keys()):
                if(self.drivesavedict[key] == self.devicesavedict[key]):
                    self.instructdict[key] = "Done"
                if(self.drivesavedict[key]['play'] > self.devicesavedict[key]['play']):
                    self.instructdict[key] = "Download"
                if(self.drivesavedict[key]['play'] < self.devicesavedict[key]['play']):
                    self.instructdict[key] = "Upload"
            if(key not in self.drivesavedict.keys()):
                self.instructdict[key] = "Upload"
        for key in self.drivesavedict.keys():
            if(key not in self.devicesavedict.keys()):
                self.instructdict[key] = "Download"
        print(str(self.instructdict))
    
    def cleantemp(self):
        if(os.path.exists(self.home+"\\sss_temp")):
            shutil.rmtree(self.home+"\\sss_temp")
        print("cleaned sss_temp")
    
    # UI Triggered functions
    def generalsync(self):
        self.compare()
        for item in self.instructdict:
            if(self.instructdict[item] == "Upload"):
                self.upload(item)
            if(self.instructdict[item] == "Download"):
                self.download(item)
    
    def selectedsync(self):
        if(self.selectedStorage == "Drive"):
            self.download(self.selectedItems[0].text(2))
        if(self.selectedStorage == "Local"):
            self.upload(self.selectedItems[0].text(2))
        if(self.selectedStorage == ""):
            print("No item selected.")
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def closeEvent(self, *args, **kwargs):
        super(QtWidgets.QMainWindow, self).closeEvent(*args, **kwargs)
        self.cleantemp()

    def refresh(self):
        global connection
        connection = True
        print("Refreshing")
        self.cleantemp()
        self.treeWidgetDrive.clear()
        self.treeWidgetLocal.clear()
        self.setup()
        self.localsaves()
        self.drivesetup()
        self.drivesaves()

    def localSelectionUpdate(self):
        self.selectedItems = self.treeWidgetLocal.selectedItems()
        self.selectedStorage = "Local"
        print(str(self.selectedItems[0].text(2))+" - "+self.selectedStorage)

    def driveSelectionUpdate(self):
        self.selectedItems = self.treeWidgetDrive.selectedItems()
        self.selectedStorage = "Drive"
        print(str(self.selectedItems[0].text(2))+" - "+self.selectedStorage)
    
    def consoleopen(self):
        self.console = Console(self)
        self.console.show()

class Console(Qt.QDialog):
    def __init__(self,parent):
        super(Console, self).__init__()
        uic.loadUi('console.ui')

window = Main()
app.exec_()