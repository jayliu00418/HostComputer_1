
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from main import MainWindow


class Ui_Dialog(object):

    def setupUI(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1, 1)
        Dialog.setWindowFlag(Qt.FramelessWindowHint)
        Dialog.centralwidget = QtWidgets.QWidget(Dialog)
        Dialog.centralwidget.setObjectName("centralwidget")

        Dialog.label_SLM_PlayImg = QtWidgets.QLabel(Dialog.centralwidget)
        Dialog.label_SLM_PlayImg.setObjectName("label_SLM_PlayImg")
        Dialog.label_SLM_PlayImg.setGeometry(QtCore.QRect(0,0,400,400))

#        Dialog.label_SLM_PlayImg.setText("1222222222222")


        # 控件




