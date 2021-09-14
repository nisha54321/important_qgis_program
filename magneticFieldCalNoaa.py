# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'magneticFieldCal.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

#pyuic5 -x magneticFieldCal.ui -o magneticFieldCal.py

from PyQt5 import QtCore, QtGui, QtWidgets
from magnetic_field_calculator import MagneticFieldCalculator
import os
from geopy.geocoders import Nominatim

class Ui_Dialog(object):
    st_date = ''
    signlong = ''
    signlt = ''
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(494, 632)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(70, 170, 91, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(70, 230, 91, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(70, 290, 91, 21))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(70, 350, 91, 21))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(160, 10, 121, 41))
        self.label_5.setText("")
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(150, 80, 181, 21))
        self.label_6.setObjectName("label_6")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(150, 570, 101, 23))
        self.pushButton.setObjectName("pushButton")
        self.lineEdit_lt = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_lt.setGeometry(QtCore.QRect(170, 170, 113, 23))
        self.lineEdit_lt.setObjectName("lineEdit_lt")
        self.lineEdit_long = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_long.setGeometry(QtCore.QRect(170, 230, 113, 23))
        self.lineEdit_long.setObjectName("lineEdit_long")
        self.lineEdit_model = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_model.setGeometry(QtCore.QRect(170, 290, 113, 23))
        self.lineEdit_model.setObjectName("lineEdit_model")
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(50, 430, 341, 111))
        self.textEdit.setObjectName("textEdit")
        self.dateEdit = QtWidgets.QDateEdit(Dialog)
        self.dateEdit.setGeometry(QtCore.QRect(170, 350, 110, 24))
        self.dateEdit.setObjectName("dateEdit")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(310, 160, 101, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_lt = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_lt.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_lt.setObjectName("horizontalLayout_lt")
        self.radioButton_n = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_n.setObjectName("radioButton_n")
        self.horizontalLayout_lt.addWidget(self.radioButton_n)
        self.radioButton_s = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_s.setObjectName("radioButton_s")
        self.horizontalLayout_lt.addWidget(self.radioButton_s)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(310, 230, 101, 41))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_long = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_long.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_long.setObjectName("horizontalLayout_long")
        self.radioButton_e = QtWidgets.QRadioButton(self.horizontalLayoutWidget_2)
        self.radioButton_e.setObjectName("radioButton_e")
        self.horizontalLayout_long.addWidget(self.radioButton_e)
        self.radioButton_w = QtWidgets.QRadioButton(self.horizontalLayoutWidget_2)
        self.radioButton_w.setObjectName("radioButton_w")
        self.horizontalLayout_long.addWidget(self.radioButton_w)
        self.label_loc = QtWidgets.QLabel(Dialog)
        self.label_loc.setGeometry(QtCore.QRect(70, 120, 81, 16))
        self.label_loc.setObjectName("label_loc")
        self.lineEdit_location = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_location.setGeometry(QtCore.QRect(170, 120, 191, 23))
        self.lineEdit_location.setObjectName("lineEdit_location")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(380, 120, 61, 23))
        self.pushButton_2.setObjectName("pushButton_2")

        self.radioButton_n.toggled.connect(self.nselected)
        self.radioButton_e.toggled.connect(self.eselected)
        self.radioButton_w.toggled.connect(self.wselected)
        self.radioButton_s.toggled.connect(self.sselected)

        
        self.dateEdit.setMinimumDate(QtCore.QDate(2021, 8, 1))
        self.dateEdit.setMaximumDate(QtCore.QDate(2023, 1, 1))
        self.dateEdit.setCalendarPopup(True)

        def onDateChanged(qDate):
                self.st_date = "%02d-%02d-%02d"%(qDate.year(), qDate.month(), qDate.day())
        self.dateEdit.dateChanged.connect(onDateChanged)

        cwd = os.getcwd()

        self.label_5.setPixmap(QtGui.QPixmap(cwd+'/'+'bisag_n.png').scaledToWidth(120))

        self.pushButton.clicked.connect(self.calculation) 
        self.pushButton_2.clicked.connect(self.location)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.label.setStyleSheet("color: brown;") 
        self.label_2.setStyleSheet("color: brown;") 
        self.label_3.setStyleSheet("color: brown;") 
        self.label_4.setStyleSheet("color: brown;") 
        self.label_6.setStyleSheet("color: blue;")
        self.label_loc.setStyleSheet("color: darkslategray;font-size: 12pt;")  
        self.pushButton_2.setStyleSheet("color: purple;") 

        self.pushButton.setStyleSheet("color: green;font-size: 12pt;") 

    def nselected(self, selected):
        if selected:
            print("north")
    def eselected(self, selected):
        if selected:
            print("east")
    def wselected(self, selected):
        if selected:
            self.signlong = '-'
            print("west",self.signlong)
    def sselected(self, selected):
        if selected:
            self.signlt = '-'
            print("south",self.signlt)

    def location(self):
        geolocator = Nominatim(user_agent="my_user_agent")
        city1 = self.lineEdit_location.text()
        country ="India"
        loc = geolocator.geocode(city1+','+ country)

        ltt = loc.latitude
        longg = loc.longitude
        self.lineEdit_lt.setText(str(ltt))
        self.lineEdit_long.setText(str(longg))

        print("latitude is :-" ,loc.latitude,"\nlongtitude is:-" ,loc.longitude)
        location = geolocator.reverse(str(ltt)+","+str(longg))

        print(location)

    def calculation(self):
        lt = self.lineEdit_lt.text()
        long = self.lineEdit_long.text()

        lt1 =self.signlt +lt
        long1 =self.signlong +long

        print(lt1)
        print(long1)

        model1 = self.lineEdit_model.text()

        print(self.st_date)
        calculator = MagneticFieldCalculator()
        calculator = MagneticFieldCalculator(
            model=model1,
            revision='2020',
        )
        result = calculator.calculate(
            latitude=float(lt1),
            longitude=float(long1),
            altitude=0,

            date=str(self.st_date)
        )
        print(result)
        field_value = result['field-value']
        declination = field_value['declination']
        inclination = field_value['inclination']
        total_intensity = field_value['total-intensity']
        north_intensity = field_value['north-intensity']
        east_intensity = field_value['east-intensity']
        vertical_intensity = field_value['vertical-intensity']
        horizontal_intensity = field_value['horizontal-intensity']
        declval = str(declination["value"]) +" "+declination["units"]
        incval = str(inclination["value"]) +" "+inclination["units"]

        ti = str(total_intensity["value"]) +" "+total_intensity["units"]
        ni = str(north_intensity["value"]) +" "+north_intensity["units"]
        ei = str(east_intensity["value"]) +" "+east_intensity["units"]
        vi = str(vertical_intensity["value"]) +" "+vertical_intensity["units"]
        hi = str(horizontal_intensity["value"]) +" "+horizontal_intensity["units"]

        #secular-variation = result["secular-variation"]    
        self.textEdit.setPlainText("declination: "+str(declval)+"\n"+"inclination: "+str(incval)+"\n"+"total intensity: "+ti+"\n"+"north intensity: "+ni+"\n"+"horizontal intensity: "+hi+"\n"+"vertical intensity: "+vi)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Latitude:"))
        self.label_2.setText(_translate("Dialog", "Longitude:"))
        self.label_3.setText(_translate("Dialog", "Model:"))
        self.label_4.setText(_translate("Dialog", "Date:"))
        self.label_6.setText(_translate("Dialog", "Calculate Declination"))
        self.pushButton.setText(_translate("Dialog", "Calculate"))
        self.radioButton_s.setText(_translate("Dialog", "S"))
        self.radioButton_n.setText(_translate("Dialog", "N"))
        self.radioButton_w.setText(_translate("Dialog", "W"))
        self.radioButton_e.setText(_translate("Dialog", "E"))
        self.label_loc.setText(_translate("Dialog", "Location:"))
        self.pushButton_2.setText(_translate("Dialog", "Find.."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
