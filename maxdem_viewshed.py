# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .maxdem_viewshed_dialog import MaxdemViewshedDialog
import os.path
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class MaxdemViewshed:

    def __init__(self, iface):
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        print('locale;',locale)
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MaxdemViewshed_{}.qm'.format(locale))
        print('locale_path:',locale_path)

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Maxdem Viewshed')

        
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        return QCoreApplication.translate('MaxdemViewshed', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):

        icon_path = ':/plugins/maxdem_viewshed/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Maxdem Viewshed'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Maxdem Viewshed'),
                action)
            self.iface.removeToolBarIcon(action)

    def data1(self):
        print("clickesd")
        self.dlg.label.setText("well come:")
        #self.dlg.tab_2.show()
    def run(self):

        if self.first_start == True:
            print("true")
            self.first_start = False
            self.dlg = MaxdemViewshedDialog()
            self.dlg.pushButton.clicked.connect(self.data1)  
       
        self.dlg.tabWidget.setTabText(0,"Home") ##set tab name 
        self.dlg.tabWidget.setTabText(1,"Algorithm")
        self.dlg.tabWidget.setTabEnabled(1,False) #enable/disable the tab
        self.dlg.tabWidget.setTabEnabled(2,False) #enable/disable the tab

        self.dlg.tabWidget.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")

        
        def main():
            self.dlg.tabWidget.setStyleSheet("QTabBar::tab::enable ")
            self.dlg.tabWidget.setTabEnabled(1,True) #enable/disable the tab
            self.dlg.tabWidget.setCurrentIndex (1)##change tab (activate)
            
        self.dlg.pushButton.clicked.connect(main)  
        
        def main1():
            self.dlg.tabWidget.setStyleSheet("QTabBar::tab::enable ")
            self.dlg.tabWidget.setTabEnabled(2,True) #enable/disable the tab
            self.dlg.tabWidget.setCurrentIndex (2)##change tab (activate)
            self.dlg.label_2.setText("Thank you..")
        self.dlg.pushButton_2.clicked.connect(main1)  




        self.dlg.show()
        #self.dlg.exec_()
          
