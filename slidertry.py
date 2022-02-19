from slider import *
#from slider import getValue

import sys
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
Dialog = QtWidgets.QDialog()
ui = Ui_Dialog()
ui.setupUi(Dialog)

ui.getValue()
x =ui.DILATE_KERNEL_KSIZE
ui.getValue()
print("dkk::",x)

# GAUSSIAN_BLUR_KSIZE,DILATE_KERNEL_KSIZE,DILATE_NB_ITERS,PAST_NB_FRAMES,MIN_CHANGE_INTENSITY,MIN_BOX_AREA = [23],[7],[7],[8],[67],[67]
# def getValue1():

#     gbk = ui.horizontalSlider_gbk.value()
#     dkk = ui.horizontalSlider_dkk.value()
#     dni = ui.horizontalSlider_dni.value()
#     pnf = ui.horizontalSlider_pnf.value()
#     mci = ui.horizontalSlider_mci.value()
#     mba = ui.horizontalSlider_mba.value()

#     with open("configs_slider.py", "w") as f:
#         f.write("GAUSSIAN_BLUR_KSIZE = ("+str(gbk)+", "+str(gbk)+")"+"\n")
#         f.write("DILATE_KERNEL_KSIZE = "+str(dkk)+"\n")
#         f.write("DILATE_NB_ITERS = "+str(dni)+"\n")
#         f.write("PAST_NB_FRAMES = "+str(pnf)+"\n")
#         f.write("HORIZONTAL_STRIPE_BLOCK_LIST = [[0, 43], [543, 'end']]\n")#static
#         f.write("MIN_CHANGE_INTENSITY = "+str(mci)+"\n")
#         f.write("MIN_BOX_AREA ="+str(mba)+"\n")

#     GAUSSIAN_BLUR_KSIZE[0]= (str(gbk))
#     DILATE_KERNEL_KSIZE[0]= (str(dkk))
#     DILATE_NB_ITERS[0]= (str(dni))
#     PAST_NB_FRAMES[0]= (str(pnf))
#     MIN_CHANGE_INTENSITY[0]= (str(mci))
#     MIN_BOX_AREA[0]= (str(mba))

#     print("local: ",gbk,dkk,dni,pnf,mci,mba)
#     #print("local: ",GAUSSIAN_BLUR_KSIZE[0],DILATE_KERNEL_KSIZE[0],DILATE_NB_ITERS[0],PAST_NB_FRAMES[0],MIN_CHANGE_INTENSITY[0],MIN_BOX_AREA[0])

# ui.horizontalSlider_gbk.valueChanged.connect(getValue1)
# ui.horizontalSlider_dkk.valueChanged.connect(getValue1)
# ui.horizontalSlider_dni.valueChanged.connect(getValue1)
# ui.horizontalSlider_pnf.valueChanged.connect(getValue1)
# ui.horizontalSlider_mci.valueChanged.connect(getValue1)
# ui.horizontalSlider_mba.valueChanged.connect(getValue1)

Dialog.show()
#print("global: ",GAUSSIAN_BLUR_KSIZE[0],DILATE_KERNEL_KSIZE[0],DILATE_NB_ITERS[0],PAST_NB_FRAMES[0],MIN_CHANGE_INTENSITY[0],MIN_BOX_AREA[0])

sys.exit(app.exec_())

#GAUSSIAN_BLUR_KSIZE = (27, 27)
# DILATE_KERNEL_KSIZE = 7
# DILATE_NB_ITERS = 4
# PAST_NB_FRAMES = 5
# HORIZONTAL_STRIPE_BLOCK_LIST = [[0, 43], [543, 'end']]
# MIN_CHANGE_INTENSITY = 20
# MIN_BOX_AREA =100

