
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .line_hape_dialog import LineShapeDialog
import os.path
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog

class LineShape:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LineShape_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Line Shape')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LineShape', message)


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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

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

        plugin_dir = os.path.dirname(__file__)
        icon_path = plugin_dir+os.sep+'BISAG-N_MeitY.jpg'
        
        self.menu = self.iface.mainWindow().findChild( QMenu, '&Algorithm' )

        if not self.menu:
            self.menu = QMenu( '&Algorithm', self.iface.mainWindow().menuBar() )
            self.menu.setObjectName( '&Algorithm' )
            actions = self.iface.mainWindow().menuBar().actions()
            lastAction = actions[-1]
            self.iface.mainWindow().menuBar().insertMenu( lastAction, self.menu )
            self.action = QAction(QIcon(icon_path),"LineShape", self.iface.mainWindow())
            self.action.setObjectName( 'LineShape' )
            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)

        else:
            self.action = QAction(QIcon(icon_path),"LineShape", self.iface.mainWindow())
            self.action.setObjectName( 'LineShape' )

            self.action.triggered.connect(self.run)
            self.menu.addAction(self.action)
       
        self.first_start = True


    def unload(self):
        #menuBar = self.menu.parentWidget()
        #print("reload:\n",self.menu.actions(),'\n',menuBar)
        for action in self.menu.actions():
            #print(" inside",": ",action.objectName())
            if action.objectName() == "LineShape":
                print("remove :::","",action.objectName())
                #icon.setEnabled(False)
                self.menu.removeAction(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = LineShapeDialog()
        import csv
        import ogr
        import os
        import osr
        import sys
        import qgis
        import qgis.core
        from qgis.core import QgsApplication
        from qgis.core import QgsProcessingFeedback
        #sys.path.append('C://Program Files//QGIS 3.4//apps//qgis//python//plugins//')
        from qgis import processing

        #qgis.core.QgsApplication.setPrefixPath(r'C:/Program Files/QGIS 3.4/apps/qgis', True)
        # qgs = qgis.core.QgsApplication([], False)
        # qgs.initQgis()
        # processing.core.Processing.Processing.initialize()
        # qgis.core.QgsApplication.processingRegistry().addProvider(qgis.analysis.QgsNativeAlgorithms())

        #print(sys.path)

        input_folder = "/home/bisag/Documents/wfh/1WFH/algo_python/input/"
        rasterfolder = "/home/bisag/Documents/wfh/1WFH/algo_python/input/" #'E:/dem sumit narmada/'
        # input_folder = 'C:/volume/test/'
        # rasterfolder = 'C:/volume/test/'
        input_file  = input_folder+"lines.txt"
        output_file = input_folder+"shape"

        # input_folder = r'C:\Users\Jai Shree Ram\Downloads\filesCombine\input'
        # rasterfolder = r'C:\Users\Jai Shree Ram\Downloads\filesCombine'
        # input_file  = input_folder+"\lines.txt"
        # output_file = input_folder+"shape"

        import os.path
        layer_name  = os.path.splitext(os.path.basename(output_file))[0]
        print(layer_name)
        spatialref = osr.SpatialReference()
        spatialref.ImportFromProj4('+proj=longlat +datum=WGS84 +no_defs')
        #spatialref.SetWellKnownGeogCS('WGS84')
        nooflines=0
        with open(input_file) as fin:
            for row in fin.readlines():
                nooflines = nooflines + 1
        print("nooflines::",nooflines)
        from osgeo import ogr

        #create field for shp file
        driver = ogr.GetDriverByName("ESRI Shapefile")
        i=0
        nooflines1 = nooflines
        nooflines = 'shp'

        alg_name = 'native:mergevectorlayers'
        #nooflines = 4#This value will be available from the above code - comment this for production

        for i in range(0,nooflines1):#print(i)
            feedback = qgis.core.QgsProcessingFeedback()
            params = {'LAYERS': 
            [input_folder+str(nooflines)+'/shape'+str(i)+'.shp',input_folder+str(nooflines)+'/line.shp'],
            'OUTPUT': input_folder+str(nooflines)+'/merged'+str(i)+'.shp'}
            processing.run(alg_name, params, feedback=feedback)

        alg_name = 'qgis:polygonize'
        for i in range(0,nooflines1):
            print(i)
            feedback = QgsProcessingFeedback()
            params = {'INPUT': input_folder+str(nooflines)+'/merged'+str(i)+'.shp','OUTPUT': input_folder+str(nooflines)+'/polygonized'+str(i)+'.shp'}
            res = processing.run(alg_name, params, feedback=feedback)

        alg_name = 'native:extractbylocation'
        for i in range(0,nooflines1):#print(i)
            feedback = qgis.core.QgsProcessingFeedback()
            params = {'INPUT': input_folder+str(nooflines)+'/polygonized'+str(i)+'.shp','PREDICATE':0,'INTERSECT': input_folder+str(nooflines)+'/point.shp','OUTPUT': input_folder+str(nooflines)+'/extract'+str(i)+'.shp'}
            res = processing.run(alg_name, params, feedback=feedback)

        alg_name = 'native:mergevectorlayers'
        tobemergedextracts = []
        for i in range(0,nooflines1):#print(i)
            tobemergedextracts.append(input_folder+str(nooflines)+'/extract'+str(i)+'.shp')

        #print(tobemergedextracts)
        feedback = qgis.core.QgsProcessingFeedback()
        params = {'LAYERS': tobemergedextracts,'OUTPUT': input_folder+str(nooflines)+'/extractmerged'+'.shp'}
        res = processing.run(alg_name, params, feedback=feedback)

        alg_name = 'native:dissolve'
        feedback = qgis.core.QgsProcessingFeedback()
        params = {'INPUT': input_folder+str(nooflines)+'/extractmerged'+'.shp','OUTPUT': input_folder+str(nooflines)+'/extractmergeddissolved'+'.shp'}
        res = processing.run(alg_name, params, feedback=feedback)

        alg_name = 'gdal:cliprasterbymasklayer'

        inputrasterfilename = 'Narmada_UTM.tif'
        inputraster = rasterfolder + inputrasterfilename
        outputraster = input_folder + "clip"+inputrasterfilename
        #print(outputraster)
        feedback = qgis.core.QgsProcessingFeedback()
        params = {'INPUT': inputraster,'MASK': input_folder+str(nooflines)+'/extractmergeddissolved'+'.shp','ALPHA_BAND': False,'CROP_TO_CUTLINE': True,'KEEP_RESOLUTION': True, 'DATA_TYPE':1 ,'OUTPUT': outputraster}
        res = processing.run(alg_name, params, feedback=feedback)

        #This has been added later
        folder = input_folder
        filename = folder + 'qgis.log'

        def write_log_message(message, tag, level):
            with open(filename, 'a') as logfile:
                logfile.write('{tag}({level}): {message}'.format(tag=tag, level=level, message=message))

        QgsApplication.messageLog().messageReceived.connect(write_log_message)

        #alg_name = 'saga:rastervolume'
        alg_name = 'native:rastersurfacevolume'
        folder = input_folder #'E:/dem sumit narmada/'
        #inputrasterfilename = 'clipNarmada_UTM.tif'
        inputraster = outputraster # we use the clip file instead of the original DEM file
        feedback = qgis.core.QgsProcessingFeedback()
        #params = {'GRID': inputraster,'METHOD': 1 ,'LEVEL': 125.0}
        params = {'INPUT': inputraster,'BAND':1,'METHOD': 1 ,'LEVEL': 120.0}
        res = processing.run(alg_name, params, feedback=feedback)

        import re
        import os
        f = open(input_folder+'qgis.log')
        g = open(input_folder+'volume.txt','w')
        i=0
        for linee in f.readlines():
            matches = re.search(r'Results.*\}',linee)
            if matches:
                g.write(matches.group())
                i=1
            else:
                pass

        if i == 0:
            g.write('Volume not found')

        f.close()
        g.close()
        #shptoWKT
        # from osgeo import ogr
        # myfile = ogr.Open(input_folder+'/shp/extractmergeddissolved'+'.shp')#input Shapefile
        # myshape = myfile.GetLayer(0)
        # feature = myshape.GetFeature(0)
        # myfeature = feature.ExportToJson()
        # import json
        # myfeature = json.loads(myfeature)
        # myfeature['geometry'] #output WKT file
        # import geodaisy.converters as convert
        # wkt_str = convert.geojson_to_wkt(myfeature['geometry'])
        # outfile = open(input_folder+'/shp/extractmergeddissolved'+'.wkt','w')#output WKT file
        # outfile.write(wkt_str)
        # outfile.close()
        #shptoWKTEnds

        #from qgis.utils import iface
        #iface.actionExit().trigger()

        #import os
        #os._exit(0)
        #qgis --nologo --code C:/volume/1_linestoshp.py

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
