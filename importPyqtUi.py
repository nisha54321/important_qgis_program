# imports
from PyQt5 import uic

# load ui file
# imports
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from magnetic_field_calculator import MagneticFieldCalculator
import os
from geopy.geocoders import Nominatim
import sys


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'magneticFieldCal1.ui'))


class VectorlayerDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(VectorlayerDialog, self).__init__(parent)
        self.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = VectorlayerDialog()
    ui.setupUi(Dialog)
    ui.label_2.setStyleSheet("color: red;") 

    Dialog.show()
    sys.exit(app.exec_())
