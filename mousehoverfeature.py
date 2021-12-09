class CustomSelectTool(QgsMapTool):   

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.identifier = QgsMapToolIdentify(canvas)
        self.featureId = None

    def canvasMoveEvent(self, ev):
        ### IT WORKS BUT MOUSE TRACKING IS NOT VERY ACCURATE
        indentifiedFeatures = self.identifier.identify(ev.x(), ev.y(), self.identifier.TopDownAll)
        if not indentifiedFeatures[0].mFeature.id() == self.featureId: 
            self.featureId = indentifiedFeatures[0].mFeature.id()
            indentifiedFeatures[0].mLayer.select(self.featureId)
        print(indentifiedFeatures)
selectTool = CustomSelectTool(iface.mapCanvas())
iface.mapCanvas().setMapTool( selectTool ) # Use your Map Tool!
print(selectTool)
