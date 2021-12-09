class CustomSelectTool(QgsMapTool):   

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.identifier = QgsMapToolIdentify(canvas)
        self.featureId = None

    def canvasMoveEvent(self, ev):
        ### IT WORKS BUT MOUSE TRACKING IS NOT VERY ACCURATE
        features = QgsMapToolIdentify(self.canvas).identify(ev.x(), ev.y(), self.canvas.layers(),QgsMapToolIdentify.TopDownStopAtFirst)
        indentifiedFeatures = self.identifier.identify(ev.x(), ev.y(), self.identifier.TopDownAll)
        if not indentifiedFeatures[0].mFeature.id() == self.featureId: 
            self.featureId = indentifiedFeatures[0].mFeature.id()
            x= indentifiedFeatures[0].mLayer.select(self.featureId)
        x = ev.pos().x()
        y = ev.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

        print(point)
        feature = features[0].mFeature
        #And here you get the attribute's value
        parishName = feature['date']
        print(parishName)
        print (indentifiedFeatures[0].mFeature.id())
        
selectTool = CustomSelectTool(iface.mapCanvas())
iface.mapCanvas().setMapTool( selectTool ) # Use your Map Tool!
#print(selectTool)
