# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
# pyuic5 -x slider.ui -o slider.py
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (QWidget, QSlider, QHBoxLayout,
                             QLabel, QApplication)
class Ui_Dialog(object):
    GAUSSIAN_BLUR_KSIZE,DILATE_KERNEL_KSIZE,DILATE_NB_ITERS,PAST_NB_FRAMES,MIN_CHANGE_INTENSITY,MIN_BOX_AREA = "","","","","",""
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(552, 552)
        self.horizontalSlider_gbk = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_gbk.setGeometry(QtCore.QRect(290, 90, 160, 16))
        self.horizontalSlider_gbk.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_gbk.setObjectName("horizontalSlider_gbk")
        self.label_gbk = QtWidgets.QLabel(Dialog)
        self.label_gbk.setGeometry(QtCore.QRect(50, 80, 181, 31))
        self.label_gbk.setObjectName("label_gbk")
        self.label_dkk = QtWidgets.QLabel(Dialog)
        self.label_dkk.setGeometry(QtCore.QRect(50, 150, 181, 31))
        self.label_dkk.setObjectName("label_dkk")
        self.label_dni = QtWidgets.QLabel(Dialog)
        self.label_dni.setGeometry(QtCore.QRect(50, 220, 181, 31))
        self.label_dni.setObjectName("label_dni")
        self.label_pnf = QtWidgets.QLabel(Dialog)
        self.label_pnf.setGeometry(QtCore.QRect(50, 300, 171, 21))
        self.label_pnf.setObjectName("label_pnf")
        self.label_mci = QtWidgets.QLabel(Dialog)
        self.label_mci.setGeometry(QtCore.QRect(50, 371, 171, 20))
        self.label_mci.setObjectName("label_mci")
        self.horizontalSlider_dkk = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_dkk.setGeometry(QtCore.QRect(290, 160, 160, 16))
        self.horizontalSlider_dkk.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_dkk.setObjectName("horizontalSlider_dkk")
        self.horizontalSlider_dni = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_dni.setGeometry(QtCore.QRect(290, 230, 160, 16))
        self.horizontalSlider_dni.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_dni.setObjectName("horizontalSlider_dni")
        self.horizontalSlider_pnf = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_pnf.setGeometry(QtCore.QRect(290, 310, 160, 16))
        self.horizontalSlider_pnf.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_pnf.setObjectName("horizontalSlider_pnf")
        self.horizontalSlider_mci = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_mci.setGeometry(QtCore.QRect(290, 380, 160, 16))
        self.horizontalSlider_mci.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_mci.setObjectName("horizontalSlider_mci")
        self.label_mba = QtWidgets.QLabel(Dialog)
        self.label_mba.setGeometry(QtCore.QRect(50, 450, 171, 20))
        self.label_mba.setObjectName("label_mba")
        self.horizontalSlider_mba = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_mba.setGeometry(QtCore.QRect(290, 450, 160, 16))
        self.horizontalSlider_mba.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_mba.setObjectName("horizontalSlider_mba")
        self.label_gbkval = QtWidgets.QLabel(Dialog)
        self.label_gbkval.setGeometry(QtCore.QRect(490, 90, 51, 16))
        self.label_gbkval.setText("")
        self.label_gbkval.setObjectName("label_gbkval")
        self.label_dkkval = QtWidgets.QLabel(Dialog)
        self.label_dkkval.setGeometry(QtCore.QRect(490, 160, 51, 16))
        self.label_dkkval.setText("")
        self.label_dkkval.setObjectName("label_dkkval")
        self.label_mbaval = QtWidgets.QLabel(Dialog)
        self.label_mbaval.setGeometry(QtCore.QRect(490, 450, 51, 16))
        self.label_mbaval.setText("")
        self.label_mbaval.setObjectName("label_mbaval")
        self.label_pnfval = QtWidgets.QLabel(Dialog)
        self.label_pnfval.setGeometry(QtCore.QRect(490, 310, 51, 16))
        self.label_pnfval.setText("")
        self.label_pnfval.setObjectName("label_pnfval")
        self.label_dnival = QtWidgets.QLabel(Dialog)
        self.label_dnival.setGeometry(QtCore.QRect(490, 230, 51, 16))
        self.label_dnival.setText("")
        self.label_dnival.setObjectName("label_dnival")
        self.label_mci_2 = QtWidgets.QLabel(Dialog)
        self.label_mci_2.setGeometry(QtCore.QRect(490, 380, 51, 16))
        self.label_mci_2.setText("")
        self.label_mci_2.setObjectName("label_mci_2")
       
        self.pushButton_default = QtWidgets.QPushButton(Dialog)
        self.pushButton_default.setGeometry(QtCore.QRect(180, 510, 101, 23))
        self.pushButton_default.setObjectName("pushButton_default")

        #set range value min max
        self.horizontalSlider_gbk.setRange(1, 50)
        self.horizontalSlider_dkk.setRange(1, 20)
        self.horizontalSlider_dni.setRange(1, 10)
        self.horizontalSlider_pnf.setRange(1, 60)
        self.horizontalSlider_mci.setRange(1, 255)
        self.horizontalSlider_mba.setRange(1, 400)

        ##set value
        self.horizontalSlider_gbk.setValue(21)
        self.horizontalSlider_dkk.setValue(7)
        self.horizontalSlider_dni.setValue(4)
        self.horizontalSlider_pnf.setValue(5)
        self.horizontalSlider_mci.setValue(20)
        self.horizontalSlider_mba.setValue(100)

        ##mouse hover get odd value (increament by two)
        self.horizontalSlider_gbk.setSingleStep(2) # arrow-key step-size
        self.horizontalSlider_gbk.setPageStep(2) # mouse-wheel/page-key step-size

        self.horizontalSlider_dkk.setSingleStep(2) # arrow-key step-size
        self.horizontalSlider_dkk.setPageStep(2) 
        ##tick add
        self.horizontalSlider_gbk.setTickPosition(QSlider.TicksAbove)
        self.horizontalSlider_gbk.setTickInterval(10)
        self.horizontalSlider_dkk.setTickPosition(QSlider.TicksAbove)
        self.horizontalSlider_dkk.setTickInterval(5)
        self.horizontalSlider_dni.setTickPosition(QSlider.TicksAbove)
        self.horizontalSlider_dni.setTickInterval(2)
        self.horizontalSlider_pnf.setTickPosition(QSlider.TicksAbove)
        self.horizontalSlider_pnf.setTickInterval(10)
        self.horizontalSlider_mci.setTickPosition(QSlider.TicksAbove)
        self.horizontalSlider_mci.setTickInterval(50)
        self.horizontalSlider_mba.setTickPosition(QSlider.TicksAbove)
        self.horizontalSlider_mba.setTickInterval(50)

        #signal
        self.horizontalSlider_gbk.valueChanged.connect(self.getValue)
        self.horizontalSlider_dkk.valueChanged.connect(self.getValue)
        self.horizontalSlider_dni.valueChanged.connect(self.getValue)
        self.horizontalSlider_pnf.valueChanged.connect(self.getValue)
        self.horizontalSlider_mci.valueChanged.connect(self.getValue)
        self.horizontalSlider_mba.valueChanged.connect(self.getValue)

        self.pushButton_default.clicked.connect(self.default)


        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
    def getValue(self):
        self.GAUSSIAN_BLUR_KSIZE = self.horizontalSlider_gbk.value()
        self.DILATE_KERNEL_KSIZE = self.horizontalSlider_dkk.value()

        ###odd
        # if (GAUSSIAN_BLUR_KSIZE % 2) != 0  :
        #     self.label_gbkval.setText(str(GAUSSIAN_BLUR_KSIZE))

        # elif  (DILATE_KERNEL_KSIZE % 2) != 0 :
        #     self.label_dkkval.setText(str(DILATE_KERNEL_KSIZE))

        self.DILATE_NB_ITERS = self.horizontalSlider_dni.value()
        self.PAST_NB_FRAMES = self.horizontalSlider_pnf.value()
        self.MIN_CHANGE_INTENSITY = self.horizontalSlider_mci.value()
        self.MIN_BOX_AREA = self.horizontalSlider_mba.value()

        self.label_gbkval.setText(str(self.GAUSSIAN_BLUR_KSIZE))
        self.label_dkkval.setText(str(self.DILATE_KERNEL_KSIZE))
        self.label_dnival.setText(str(self.DILATE_NB_ITERS))
        self.label_pnfval.setText(str(self.PAST_NB_FRAMES))
        self.label_mci_2.setText(str(self.MIN_CHANGE_INTENSITY))
        self.label_mbaval.setText(str(self.MIN_BOX_AREA))

        with open("configs_slider.py", "w") as f:
            f.write("GAUSSIAN_BLUR_KSIZE = ("+str(self.GAUSSIAN_BLUR_KSIZE)+", "+str(self.GAUSSIAN_BLUR_KSIZE)+")"+"\n")
            f.write("DILATE_KERNEL_KSIZE = "+str(self.DILATE_KERNEL_KSIZE)+"\n")
            f.write("DILATE_NB_ITERS = "+str(self.DILATE_NB_ITERS)+"\n")
            f.write("PAST_NB_FRAMES = "+str(self.PAST_NB_FRAMES)+"\n")

            ##static value:
            f.write("HORIZONTAL_STRIPE_BLOCK_LIST = [[0, 43], [543, 'end']]\n")


            f.write("MIN_CHANGE_INTENSITY = "+str(self.MIN_CHANGE_INTENSITY)+"\n")
            f.write("MIN_BOX_AREA ="+str(self.MIN_BOX_AREA)+"\n")

        #print(self.GAUSSIAN_BLUR_KSIZE,self.DILATE_KERNEL_KSIZE,self.DILATE_NB_ITERS,self.PAST_NB_FRAMES,self.MIN_CHANGE_INTENSITY,self.MIN_BOX_AREA)

    def default(self):
        ##set value
        self.horizontalSlider_gbk.setValue(21)
        self.horizontalSlider_dkk.setValue(7)
        self.horizontalSlider_dni.setValue(4)
        self.horizontalSlider_pnf.setValue(5)
        self.horizontalSlider_mci.setValue(20)
        self.horizontalSlider_mba.setValue(100)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_gbk.setText(_translate("Dialog", "GAUSSIAN_BLUR_KSIZE :"))
        self.label_dkk.setText(_translate("Dialog", "DILATE_KERNEL_KSIZE :"))
        self.label_dni.setText(_translate("Dialog", "DILATE_NB_ITERS :"))
        self.label_pnf.setText(_translate("Dialog", "PAST_NB_FRAMES :"))
        self.label_mci.setText(_translate("Dialog", "MIN_CHANGE_INTENSITY :"))
        self.label_mba.setText(_translate("Dialog", "MIN_BOX_AREA :"))
        self.pushButton_default.setText(_translate("Dialog", "default value"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

