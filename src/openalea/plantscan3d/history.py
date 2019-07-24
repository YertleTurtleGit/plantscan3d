from PyQt4.QtCore import QObject, SIGNAL
from collections import OrderedDict

class FileHistory:
    def __init__(self, menu = None, callfunc = None, maxsize = 20):
        self.setMenu(menu)
        self.callfunc = callfunc
        self.maxsize = maxsize
        self.clear()

    def setMenu(self, menu):
        self.menu = menu
        if self.menu: 
            QObject.connect(menu, SIGNAL('aboutToShow()'),self.updateMenu)

    def add(self, file, param = None):
        self.files[file] = param
        while len(self.files) >= self.maxsize:
            del self.files[self.files.keys()[-1]]
        self.__discardedmenu = True

    def remove(self, file):
        del self.files[file]
        self.__discardedmenu = True

    def clear(self):
        self.files = OrderedDict([])
        self.__discardedmenu = True

    def check(self):
        import os
        files = OrderedDict([])
        for file, ftype in self.files.items():
            if os.path.exists(file):
                print file,'exists'
                files[file] = ftype
            else:
                print file,'do not exist'

        if len(files) != len(self.files):
            self.files = files
            self.__discardedmenu = True

    def getLastFile(self, ftype = None):
        for fname, data in reversed(self.files.items()):
            if data == ftype: return fname

    def updateMenu(self):
        from os.path import basename 
        if self.__discardedmenu :
            self.__discardedmenu = False
            self.menu.clear()
            def callbackgenerator(fname, param = None):
                if param:
                    def callback():
                        return self.callfunc(fname, param)
                else:
                    def callback():
                        return self.callfunc(fname)
                return callback
            for fname, param in self.files.items():
                self.menu.addAction(basename(fname), callbackgenerator(fname, param))
            self.menu.addSeparator()
            self.menu.addAction('Clear', self.clear)

    def retrieveSettings(self, settings):
        settings.beginGroup("FileHistory")
        files = settings.value("RecentFiles")
        print 'files:',files
        settings.endGroup()

        if not files is None:
            print 'check files'
            files = [file.split(':',1) for file in files]
            files = OrderedDict([(str(fname),str(ftype)) for ftype,fname in files])
            self.files = files
            print self.files
            self.check()        

    def setSettings(self, settings):
        settings.beginGroup("FileHistory")
        files = [ftype+':'+fname for fname, ftype in self.files.items()]
        settings.setValue("RecentFiles",files)
        files = settings.value("RecentFiles")
        settings.endGroup()
