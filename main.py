import datetime
import inspect
import sys
import time
import numpy
import cv2
import numpy as np
from PySide2.QtCore import Signal
import re
from win32api import GetSystemMetrics
from win32con import SM_CMONITORS, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ctypes import cdll,c_long, c_ulong, c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_int16,c_double, sizeof
from TLPM import TLPM
import SLM_Window
from MainWindow import Ui_MainWindow
from SLM_Window import *
import DahengCamera
from ALP4 import *
import os
import threading
import ctypes
import pandas as pd
import tkinter as tk
from pathlib import Path

from win32.lib import win32con

def __async_raise(thread_Id, exctype):
    thread_Id = ctypes.c_long(thread_Id)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        thread_Id, ctypes.py_object(exctype)
    )
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_Id, None)
        raise SystemError("PyThreadState_SEtAsyncExc failed")

def terminator(thread):
    __async_raise(thread.ident, SystemExit)

'''
'  IIIIIIIIIINNNNNNNN        NNNNNNNNIIIIIIIIIITTTTTTTTTTTTTTTTTTTTTTT
'  I::::::::IN:::::::N       N::::::NI::::::::IT:::::::::::::::::::::T
'  I::::::::IN::::::::N      N::::::NI::::::::IT:::::::::::::::::::::T
'  II::::::IIN:::::::::N     N::::::NII::::::IIT:::::TT:::::::TT:::::T
'    I::::I  N::::::::::N    N::::::N  I::::I  TTTTTT  T:::::T  TTTTTT
'    I::::I  N:::::::::::N   N::::::N  I::::I          T:::::T        
'    I::::I  N:::::::N::::N  N::::::N  I::::I          T:::::T        
'    I::::I  N::::::N N::::N N::::::N  I::::I          T:::::T        
'    I::::I  N::::::N  N::::N:::::::N  I::::I          T:::::T        
'    I::::I  N::::::N   N:::::::::::N  I::::I          T:::::T        
'    I::::I  N::::::N    N::::::::::N  I::::I          T:::::T        
'    I::::I  N::::::N     N:::::::::N  I::::I          T:::::T        
'  II::::::IIN::::::N      N::::::::NII::::::II      TT:::::::TT      
'  I::::::::IN::::::N       N:::::::NI::::::::I      T:::::::::T      
'  I::::::::IN::::::N        N::::::NI::::::::I      T:::::::::T      
'  IIIIIIIIIINNNNNNNN         NNNNNNNIIIIIIIIII      TTTTTTTTTTT 
'''

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

            #变量
        self.count_DMDrunning = 0
        self.ImageWidthInGraphicsView = 600
        self.ImageWidthInGraphicsView1= 600
        self.imgSeqreadytosendnum = 0
        self.WavelengthtoSet = 350
        self.imgSeqreadytosend = np.zeros((1, 1))
        self.DMDready = False
        self.SLMready = False
        self.SLMPlaying = False
        self.ImgSeqGeneRunning = False
        self.ImgSeqOpenRunning = False
        self.CamSaving = False
        self.isFirstpic = False
        self.DMDrunning = False
        self.imgSeqready = False
        self.PMready = False
        self.isLineEditDistheSavePathofImgSeqGeneratetextChanged = False
        self.isLineEditDistheOpenPathofImgSeqGeneratetextChanged = False
        self.isLineEditDistheSavePathofCamImgtextChanged = False
        self.DMD = ALP4(version="4.3")

            #进程
        self.t_DMDrunning = "t_DMDrunning" + str(self.count_DMDrunning)
        self.t_DMDrunning = threading.Thread(target=self.runDMD)
        self.t_ImgSeqOpen = threading.Thread(target=self.ImgSeqOpen)
        self.t_ImgSeqGene = threading.Thread(target=self.ImgSeqGenerate)
        self.t_CamImgSave = threading.Thread(target=self.CamImgSave)
        self.t_CamImgSaveTogether = threading.Thread(target=self.CamImgSaveTogether)
        self.t_SLMplay = threading.Thread(target=self.SLMplay)
        self.t_SetPreofGeneImgSeq = threading.Thread(target=self.SetPreofGeneImgSeq)
        self.t_connectSLM = threading.Thread(target=self.connectSLM)
        self.t_connectPM = threading.Thread(target=self.connectPM)
        self.t_refreshPM = threading.Thread(target=self.refreshPM)
        #self.t_uptoSLM = threading.Thread(target=self.uptoSLM)

            #timer
        self.TimerForShowImageInGraphicsView = QTimer()
        self.TimerForShowImageInGraphicsView1 = QTimer()
        self.TimerForSaveImageFromCam = QTimer()
        self.Camera = DahengCamera.DahengCamera()
        self.Camera_1 = DahengCamera.DahengCamera()
        self.scene = QGraphicsScene()
        self.scene1 = QGraphicsScene()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.SlotInit()
        self.UpdateUI()

    """ 初始化槽信号函数"""

    def SlotInit(self):
            #Cam0
        self.ui.pushButton_OpenCamera.clicked.connect(self.PB_OpenCamera_clicked)
        self.ui.pushButton_CloseCamera.clicked.connect(self.PB_CloseCamera_clicked)
        self.ui.pushButton_StartAcq.clicked.connect(self.PB_StartAcq_clicked)
        self.ui.pushButton_StopAcq.clicked.connect(self.PB_StopAcq_clicked)
        self.ui.pushButton_ZoomIn.clicked.connect(self.PB_ZoomIn_clicked)
        self.ui.pushButton_ZoomOut.clicked.connect(self.PB_ZoomOut_clicked)
        self.TimerForShowImageInGraphicsView.timeout.connect(self.SlotForShowImageInGraphicsView)
        self.ui.pushButton_SendSoftwareCommand.clicked.connect(self.SendSoftwareCommand)
            #Cam1
        self.ui.pushButton_UpdateCameraList.clicked.connect(self.PB_UpdateCameraList_clicked)
        self.ui.pushButton_UpdateCameraList1.clicked.connect(self.PB_UpdateCameraList1_clicked)
        self.ui.pushButton_OpenCamera1.clicked.connect(self.PB_OpenCamera1_clicked)
        self.ui.pushButton_CloseCamera1.clicked.connect(self.PB_CloseCamera1_clicked)
        self.ui.pushButton_StartAcq1.clicked.connect(self.PB_StartAcq1_clicked)
        self.ui.pushButton_StopAcq1.clicked.connect(self.PB_StopAcq1_clicked)
        self.ui.pushButton_ZoomIn1.clicked.connect(self.PB_ZoomIn1_clicked)
        self.ui.pushButton_ZoomOut1.clicked.connect(self.PB_ZoomOut1_clicked)
        self.TimerForShowImageInGraphicsView1.timeout.connect(self.SlotForShowImageInGraphicsView1)
        self.ui.pushButton_SendSoftwareCommand1.clicked.connect(self.SendSoftwareCommand1)
            #SLM
        self.ui.pushButton_connectSLM.clicked.connect(self.PB_connectSLM_clicked)
        self.ui.pushButton_uptoSLM.clicked.connect(self.PB_uptoSLM_clicked)
        self.ui.pushButton_playSLM.clicked.connect(self.PB_SLMplay_clicked)
            #PM
        self.ui.pushButton_connectPMdev.clicked.connect(self.PB_connectPM_clicked)
        self.ui.pushButton_refreshPMdev.clicked.connect(self.PB_refreshPM_clicked)
            #CAMSave
        self.ui.pushButton_SelecttheSavePathofCamImg.clicked.connect(self.PB_SelecttheSavePathofCamImg_clicked)
        self.ui.pushButton_SelecttheSavePathofCamImg1.clicked.connect(self.PB_SelecttheSavePathofCamImg_clicked1)
        self.ui.pushButton_StartCamImgSave.clicked.connect(self.PB_StartCamImgSave_clicked)
        self.ui.pushButton_StartCamImgSave1.clicked.connect(self.PB_StartCamImgSaveTogether_clicked)
            #imgSeq_Gene_and_Open
        self.ui.pushButton_SelectSavePathofImgSeqGenerate.clicked.connect(self.PB_SelectSavePathofImgSeqGenerate_clicked)
        self.ui.pushButton_SelectOpenPathofImgSeqGenerate.clicked.connect(self.PB_SelectOpenPathofImgSeqGenerate_clicked)
        self.ui.pushButton_ImgSeqGenerate.clicked.connect(self.PB_ImgSeqGenerate_clicked)
        self.ui.pushButton_ImgSeqOpen.clicked.connect(self.PB_ImgSeqOpen_clicked)
            #DMD
        self.ui.pushButton_UptoDMD.clicked.connect(self.PB_UptoDMD_clicked)
        self.ui.pushButton_cleanDMD.clicked.connect(self.cleanDMD)
        self.ui.pushButton_runDMD.clicked.connect(self.PB_runDMD_clicked)
        self.ui.pushButton_stopDMD.clicked.connect(self.PB_stopDMD_clicked)
        self.ui.pushButton_InitializetheDMD.clicked.connect(self.PB_InitializetheDMD_clicked)
        self.ui.pushButton_ManualDisconnectDMD.clicked.connect(self.PB_ManualDisconnectDMD_clicked)

        self.SlotConnect()

    """槽连接"""

    def SlotConnect(self):
            #Cam0
        self.ui.comboBox_ExposureAuto.currentIndexChanged.connect(self.SetExposureAuto)
        self.ui.doubleSpinBox_ExposureTime.valueChanged.connect(self.SetExposureTime)
        self.ui.comboBox_TriggerMode.currentIndexChanged.connect(self.SetTriggerAuto)
        self.ui.comboBox_TriggerSource.currentIndexChanged.connect(self.SetTriggerSource)
        self.ui.comboBox_GainAuto.currentIndexChanged.connect(self.SetGainAuto)
        self.ui.doubleSpinBox_GainValue.valueChanged.connect(self.SetGainValue)
            #Cam1
        self.ui.comboBox_ExposureAuto1.currentIndexChanged.connect(self.SetExposureAuto1)
        self.ui.doubleSpinBox_ExposureTime1.valueChanged.connect(self.SetExposureTime1)
        self.ui.comboBox_TriggerMode1.currentIndexChanged.connect(self.SetTriggerAuto1)
        self.ui.comboBox_TriggerSource1.currentIndexChanged.connect(self.SetTriggerSource1)
        self.ui.comboBox_GainAuto1.currentIndexChanged.connect(self.SetGainAuto1)
        self.ui.doubleSpinBox_GainValue1.valueChanged.connect(self.SetGainValue1)
            #ImgSeqGene
        self.ui.spinBox_NumofGeneImgSeq.valueChanged.connect(self.SetNumofGeneImgSeq)
        self.ui.LineEditDistheSavePathofImgSeqGenerate.textChanged.connect(self.SetisLineEditDistheSavePathofImgSeqGeneratetextChanged)
        self.ui.LineEditDistheOpenPathofImgSeqGenerate.textChanged.connect(self.SetisLineEditDistheOpenPathofImgSeqGeneratetextChanged)
        self.ui.spinBox_BlockWofGeneImgSeq.valueChanged.connect(self.Valuechanged_SetPreofGeneImgSeq)
            #PM
        self.ui.comboBox_PMwavelength.currentIndexChanged.connect(self.SetPMwl)
            #CamSave
        self.ui.LineEditDistheSavePathofCamImg.textChanged.connect(self.SetisLineEditDistheSavePathofCamImgtextChanged)
        self.ui.LineEditDistheSavePathofCamImg1.textChanged.connect(self.SetisLineEditDistheSavePathofCamImgtextChanged1)
    
    """槽断开连接"""
    
    def SlotDisConnect(self):
            ##Cam0
        self.ui.comboBox_ExposureAuto.currentIndexChanged.disconnect(self.SetExposureAuto)
        self.ui.doubleSpinBox_ExposureTime.valueChanged.disconnect(self.SetExposureTime)
        self.ui.comboBox_TriggerMode.currentIndexChanged.disconnect(self.SetTriggerAuto)
        self.ui.comboBox_TriggerSource.currentIndexChanged.disconnect(self.SetTriggerSource)
        self.ui.comboBox_GainAuto.currentIndexChanged.disconnect(self.SetGainAuto)
        self.ui.doubleSpinBox_GainValue.valueChanged.disconnect(self.SetGainValue)
            ##Cam1
        self.ui.comboBox_ExposureAuto1.currentIndexChanged.disconnect(self.SetExposureAuto1)
        self.ui.doubleSpinBox_ExposureTime1.valueChanged.disconnect(self.SetExposureTime1)
        self.ui.comboBox_TriggerMode1.currentIndexChanged.disconnect(self.SetTriggerAuto1)
        self.ui.comboBox_TriggerSource1.currentIndexChanged.disconnect(self.SetTriggerSource1)
        self.ui.comboBox_GainAuto1.currentIndexChanged.disconnect(self.SetGainAuto1)
        self.ui.doubleSpinBox_GainValue1.valueChanged.disconnect(self.SetGainValue1)
            #PM
        self.ui.comboBox_PMwavelength.currentIndexChanged.disconnect(self.SetPMwl)
            #ImgSeqGene
        self.ui.LineEditDistheSavePathofImgSeqGenerate.textChanged.disconnect(self.SetisLineEditDistheSavePathofImgSeqGeneratetextChanged)
        self.ui.LineEditDistheOpenPathofImgSeqGenerate.textChanged.disconnect(self.SetisLineEditDistheOpenPathofImgSeqGeneratetextChanged)
        self.ui.LineEditDistheSavePathofCamImg.textChanged.disconnect(self.SetisLineEditDistheSavePathofCamImgtextChanged)
   
    """ 更新UI界面"""

    def UpdateUI(self):
            #Cam0
        self.ui.pushButton_OpenCamera.setDisabled(self.Camera.IsCameraOpened)
        self.ui.pushButton_CloseCamera.setDisabled(not self.Camera.IsCameraOpened)
        self.ui.pushButton_StartAcq.setDisabled(not self.Camera.IsCameraOpened or self.Camera.IsCameraStartAcq)
        self.ui.pushButton_StopAcq.setDisabled(not self.Camera.IsCameraStartAcq)
        self.ui.comboBox_ExposureMode.setDisabled(not self.Camera.IsCameraOpened)
        self.ui.comboBox_ExposureAuto.setDisabled(not self.Camera.IsCameraOpened)
        self.ui.doubleSpinBox_ExposureTime.setDisabled(not self.Camera.IsCameraOpened or not self.ui.comboBox_ExposureAuto.currentIndex() == 0)
        self.ui.pushButton_ZoomIn.setDisabled(not self.Camera.IsCameraStartAcq)
        self.ui.pushButton_ZoomOut.setDisabled(not self.Camera.IsCameraStartAcq)
        self.ui.comboBox_TriggerMode.setDisabled(not self.Camera.IsCameraOpened)
        self.ui.comboBox_TriggerSource.setDisabled(not self.Camera.IsCameraOpened or self.ui.comboBox_TriggerMode.currentIndex() == 0)
        self.ui.pushButton_SendSoftwareCommand.setDisabled(not self.Camera.IsCameraOpened or self.ui.comboBox_TriggerMode.currentIndex() == 0 or not self.ui.comboBox_TriggerSource.currentIndex() == 0)
        self.ui.comboBox_GainAuto.setDisabled(not self.Camera.IsCameraOpened)
        self.ui.doubleSpinBox_GainValue.setDisabled(not self.Camera.IsCameraOpened or not self.ui.comboBox_GainAuto.currentIndex() == 0)
            #Cam1
        self.ui.pushButton_OpenCamera1.setDisabled(self.Camera.IsCameraOpened1)
        self.ui.pushButton_CloseCamera1.setDisabled(not self.Camera.IsCameraOpened1)
        self.ui.pushButton_StartAcq1.setDisabled(not self.Camera.IsCameraOpened1 or self.Camera.IsCameraStartAcq1)
        self.ui.pushButton_StopAcq1.setDisabled(not self.Camera.IsCameraStartAcq1)
        self.ui.comboBox_ExposureMode1.setDisabled(not self.Camera.IsCameraOpened1)
        self.ui.comboBox_ExposureAuto1.setDisabled(not self.Camera.IsCameraOpened1)
        self.ui.doubleSpinBox_ExposureTime1.setDisabled(not self.Camera.IsCameraOpened1 or not self.ui.comboBox_ExposureAuto1.currentIndex() == 0)
        self.ui.pushButton_ZoomIn1.setDisabled(not self.Camera.IsCameraStartAcq1)
        self.ui.pushButton_ZoomOut1.setDisabled(not self.Camera.IsCameraStartAcq1)
        self.ui.comboBox_TriggerMode1.setDisabled(not self.Camera.IsCameraOpened1)
        self.ui.comboBox_TriggerSource1.setDisabled(not self.Camera.IsCameraOpened1 or self.ui.comboBox_TriggerMode1.currentIndex() == 0)
        self.ui.pushButton_SendSoftwareCommand1.setDisabled(not self.Camera.IsCameraOpened1 or self.ui.comboBox_TriggerMode1.currentIndex() == 0 or not self.ui.comboBox_TriggerSource1.currentIndex() == 0)
        self.ui.comboBox_GainAuto1.setDisabled(not self.Camera.IsCameraOpened1)
        self.ui.doubleSpinBox_GainValue1.setDisabled(not self.Camera.IsCameraOpened1 or not self.ui.comboBox_GainAuto1.currentIndex() == 0)
            #DMD
        self.ui.pushButton_InitializetheDMD.setDisabled(self.DMD.IsDMDdevalloc)
        self.ui.pushButton_ManualDisconnectDMD.setDisabled(not self.DMD.IsDMDdevalloc)
        self.ui.pushButton_UptoDMD.setDisabled(not self.DMD.IsDMDdevalloc or self.DMDready)
        self.ui.pushButton_cleanDMD.setDisabled(not self.DMD.IsDMDdevalloc or not self.DMDready or self.DMDrunning)
        self.ui.pushButton_runDMD.setDisabled(not self.DMD.IsDMDdevalloc or not self.DMDready or self.DMDrunning)
        self.ui.pushButton_stopDMD.setDisabled(not self.DMD.IsDMDdevalloc or not self.DMDready or not self.DMDrunning)
            #SLM
        self.ui.pushButton_playSLM.setDisabled(not self.SLMready or self.SLMPlaying)
        self.ui.pushButton_ImgSeqGenerate.setDisabled(self.ImgSeqGeneRunning or not self.isLineEditDistheSavePathofImgSeqGeneratetextChanged)
        self.ui.pushButton_ImgSeqOpen.setDisabled(self.ImgSeqOpenRunning or not self.isLineEditDistheOpenPathofImgSeqGeneratetextChanged)

    """
        CCCCCCCCCCCCC               AAA               MMMMMMMM               MMMMMMMM   
     CCC::::::::::::C              A:::A              M:::::::M             M:::::::M 
   CC:::::::::::::::C             A:::::A             M::::::::M           M::::::::M
  C:::::CCCCCCCC::::C            A:::::::A            M:::::::::M         M:::::::::M
 C:::::C       CCCCCC           A:::::::::A           M::::::::::M       M::::::::::M
C:::::C                        A:::::A:::::A          M:::::::::::M     M:::::::::::M
C:::::C                       A:::::A A:::::A         M:::::::M::::M   M::::M:::::::M
C:::::C                      A:::::A   A:::::A        M::::::M M::::M M::::M M::::::M
C:::::C                     A:::::A     A:::::A       M::::::M  M::::M::::M  M::::::M
C:::::C                    A:::::AAAAAAAAA:::::A      M::::::M   M:::::::M   M::::::M
C:::::C                   A:::::::::::::::::::::A     M::::::M    M:::::M    M::::::M
 C:::::C       CCCCCC    A:::::AAAAAAAAAAAAA:::::A    M::::::M     MMMMM     M::::::M
  C:::::CCCCCCCC::::C   A:::::A             A:::::A   M::::::M               M::::::M
   CC:::::::::::::::C  A:::::A               A:::::A  M::::::M               M::::::M
     CCC::::::::::::C A:::::A                 A:::::A M::::::M               M::::::M 
        CCCCCCCCCCCCCAAAAAAA                   AAAAAAAMMMMMMMM               MMMMMMMM    
    """

    """ 更新相机0参数的可选项目"""

    def UpdateCameraPara_Range(self):
        self.SlotDisConnect()

        self.ui.comboBox_ExposureMode.clear()
        for Range in self.Camera.GetExposureModeRange():
            self.ui.comboBox_ExposureMode.addItem(Range)

        self.ui.comboBox_ExposureAuto.clear()
        for Range in self.Camera.GetExposureAutoRange():
            self.ui.comboBox_ExposureAuto.addItem(Range)

        self.ui.comboBox_TriggerMode.clear()
        for Range in self.Camera.GetTriggerAutoRange():
            self.ui.comboBox_TriggerMode.addItem(Range)

        self.ui.comboBox_TriggerSource.clear()
        for Range in self.Camera.GetTriggerSourceRange():
            self.ui.comboBox_TriggerSource.addItem(Range)

        self.ui.comboBox_GainAuto.clear()
        for Range in self.Camera.GetGainAutoRange():
            self.ui.comboBox_GainAuto.addItem(Range)

        self.SlotConnect()

    """ 读取相机0当前参数值"""

    def GetCameraPara(self):
        self.SlotDisConnect()

        ExposureAuto = self.Camera.GetExposureAuto()
        self.ui.comboBox_ExposureAuto.setCurrentText(ExposureAuto[1])

        ExposureTime = self.Camera.GetExposureTime()
        self.ui.doubleSpinBox_ExposureTime.setValue(ExposureTime)

        TriggerMode = self.Camera.GetTriggerAuto()
        self.ui.comboBox_TriggerMode.setCurrentText(TriggerMode[1])

        TriggerSource = self.Camera.GetTriggerSource()
        self.ui.comboBox_TriggerSource.setCurrentText(TriggerSource[1])

        GainAuto = self.Camera.GetGainAuto()
        self.ui.comboBox_GainAuto.setCurrentText(GainAuto[1])

        GainValue = self.Camera.GetGainValue()
        self.ui.doubleSpinBox_GainValue.setValue(GainValue)

        self.SlotConnect()

    """ 更新相机1参数的可选项目"""

    def UpdateCameraPara_Range1(self):
        self.SlotDisConnect()

        self.ui.comboBox_ExposureMode1.clear()
        for Range in self.Camera.GetExposureModeRange1():
            self.ui.comboBox_ExposureMode1.addItem(Range)

        self.ui.comboBox_ExposureAuto1.clear()
        for Range in self.Camera.GetExposureAutoRange1():
            self.ui.comboBox_ExposureAuto1.addItem(Range)

        self.ui.comboBox_TriggerMode1.clear()
        for Range in self.Camera.GetTriggerAutoRange1():
            self.ui.comboBox_TriggerMode1.addItem(Range)

        self.ui.comboBox_TriggerSource1.clear()
        for Range in self.Camera.GetTriggerSourceRange1():
            self.ui.comboBox_TriggerSource1.addItem(Range)

        self.ui.comboBox_GainAuto1.clear()
        for Range in self.Camera.GetGainAutoRange1():
            self.ui.comboBox_GainAuto1.addItem(Range)

        self.SlotConnect()

    """ 读取相机1当前参数值"""

    def GetCameraPara1(self):
        self.SlotDisConnect()

        ExposureAuto1 = self.Camera.GetExposureAuto1()
        self.ui.comboBox_ExposureAuto1.setCurrentText(ExposureAuto1[1])

        ExposureTime1 = self.Camera.GetExposureTime1()
        self.ui.doubleSpinBox_ExposureTime.setValue(ExposureTime1)

        TriggerMode1 = self.Camera.GetTriggerAuto1()
        self.ui.comboBox_TriggerMode.setCurrentText(TriggerMode1[1])

        TriggerSource1 = self.Camera.GetTriggerSource1()
        self.ui.comboBox_TriggerSource.setCurrentText(TriggerSource1[1])

        GainAuto1 = self.Camera.GetGainAuto1()
        self.ui.comboBox_GainAuto.setCurrentText(GainAuto1[1])

        GainValue1 = self.Camera.GetGainValue1()
        self.ui.doubleSpinBox_GainValue.setValue(GainValue1)

        self.SlotConnect()

    """ 点击UpdateCameraList"""

    def PB_UpdateCameraList_clicked(self):
        status, CameraNameList = self.Camera.UpdateCameraList()
        if status:
            for CameraName in CameraNameList:
                self.ui.comboBox_CameraList.addItem(CameraName)

    """ 点击UpdateCameraList1"""

    def PB_UpdateCameraList1_clicked(self):
        status, CameraNameList = self.Camera.UpdateCameraList()
        if status:
            for CameraName in CameraNameList:
                self.ui.comboBox_CameraList1.addItem(CameraName)

    """ 点击OpenCamera"""

    def PB_OpenCamera_clicked(self):
        if self.ui.comboBox_CameraList.count() == 0:
            return
        self.Camera.OpenCamera(int(self.ui.comboBox_CameraList.currentIndex()) + 1)
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
        self.UpdateUI()

    """ 点击OpenCamera1"""

    def PB_OpenCamera1_clicked(self):
        if self.ui.comboBox_CameraList1.count() == 0:
            return
        self.Camera.OpenCamera1(int(self.ui.comboBox_CameraList1.currentIndex()) + 1)
        self.UpdateCameraPara_Range1()
        self.GetCameraPara1()
        self.UpdateUI()

    """ 点击CloseCamera"""

    def PB_CloseCamera_clicked(self):
        self.Camera.CloseCamera(int(self.ui.comboBox_CameraList.currentIndex()) + 1)
        if self.TimerForShowImageInGraphicsView.isActive():
            self.TimerForShowImageInGraphicsView.stop()
        DahengCamera.num = 0
        self.UpdateUI()

    """ 点击CloseCamera1"""

    def PB_CloseCamera1_clicked(self):
        self.Camera.CloseCamera1(int(self.ui.comboBox_CameraList1.currentIndex()) + 1)
        if self.TimerForShowImageInGraphicsView1.isActive():
            self.TimerForShowImageInGraphicsView1.stop()
        DahengCamera.num = 0
        self.UpdateUI()

    """ 点击StartAcq"""

    def PB_StartAcq_clicked(self):
        self.Camera.StartAcquisition()
        self.TimerForShowImageInGraphicsView.start(10)
        self.UpdateUI()

    """ 点击StartAcq1"""

    def PB_StartAcq1_clicked(self):
        self.Camera.StartAcquisition1()
        self.TimerForShowImageInGraphicsView1.start(10)
        self.UpdateUI()

    """ 点击StopAcq"""

    def PB_StopAcq_clicked(self):
        self.Camera.StopAcquisition()
        self.TimerForShowImageInGraphicsView.stop()
        self.UpdateUI()

        DahengCamera.num = 0

    """ 点击StopAcq1"""      

    def PB_StopAcq1_clicked(self):
        self.Camera.StopAcquisition1()
        self.TimerForShowImageInGraphicsView1.stop()
        self.UpdateUI()
        DahengCamera.num1 = 0

    """ 点击ZoomIn"""

    def PB_ZoomIn_clicked(self):
        self.ImageWidthInGraphicsView += 100

    """ 点击ZoomIn1"""

    def PB_ZoomIn1_clicked(self):
        self.ImageWidthInGraphicsView1 += 100

    """ 点击ZoomOut"""

    def PB_ZoomOut_clicked(self):
        if self.ImageWidthInGraphicsView >= 200:
            self.ImageWidthInGraphicsView -= 100

    """ 点击ZoomOut1"""

    def PB_ZoomOut1_clicked(self):
        if self.ImageWidthInGraphicsView1 >= 200:
            self.ImageWidthInGraphicsView1 -= 100

    """ 图像显示回调函数"""

    def SlotForShowImageInGraphicsView(self):
        if DahengCamera.rawImageUpdate is None:
            return
        else:
            ImageShow = DahengCamera.rawImageUpdateList[0]
            ImageRatio = float(ImageShow.shape[0] / ImageShow.shape[1])
            image_width = self.ImageWidthInGraphicsView
            show = cv2.resize(ImageShow, (image_width, int(image_width * ImageRatio)))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            show_forsave = cv2.cvtColor(ImageShow, cv2.COLOR_BGR2RGB)
            showImage = QImage(show.data, show.shape[1], show.shape[0],
                               QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            self.ImagetoSave = QImage(
                show_forsave.data, show_forsave.shape[1], show_forsave.shape[0], QImage.Format_RGB888
            )
            item = QGraphicsPixmapItem(QPixmap.fromImage(showImage))
            self.scene.clear()
            self.scene.addItem(item)
            self.scene.setSceneRect(0, 0, image_width + 1, image_width * ImageRatio + 1)
            self.ui.graphicsView.setScene(self.scene)
            self.ui.graphicsView.show()

    """ 图像显示回调函数1"""

    def SlotForShowImageInGraphicsView1(self):
        if DahengCamera.rawImageUpdate1 is None:
            return
        else:
            ImageShow1 = DahengCamera.rawImageUpdateList1[0]
            ImageRatio1 = float(ImageShow1.shape[0] / ImageShow1.shape[1])
            image_width1 = self.ImageWidthInGraphicsView1
            show1 = cv2.resize(ImageShow1, (image_width1, int(image_width1 * ImageRatio1)))
            show1 = cv2.cvtColor(show1, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            show_forsave1 = cv2.cvtColor(ImageShow1, cv2.COLOR_BGR2RGB)
            showImage1 = QImage(show1.data, show1.shape[1], show1.shape[0],
                               QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            self.ImagetoSave1 = QImage(
                show_forsave1.data, show_forsave1.shape[1], show_forsave1.shape[0], QImage.Format_RGB888
            )
            item1 = QGraphicsPixmapItem(QPixmap.fromImage(showImage1))
            self.scene1.clear()
            self.scene1.addItem(item1)
            self.scene1.setSceneRect(0, 0, image_width1 + 1, image_width1 * ImageRatio1 + 1)
            self.ui.graphicsView1.setScene(self.scene1)
            self.ui.graphicsView1.show()

    """ ExposureAuto值改变"""

    def SetExposureAuto(self):
        self.Camera.SetExposureAuto(self.ui.comboBox_ExposureAuto.currentText())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
        self.UpdateUI()

    """ ExposureAuto1值改变"""

    def SetExposureAuto1(self):
        self.Camera.SetExposureAuto1(self.ui.comboBox_ExposureAuto1.currentText())
        self.UpdateCameraPara_Range1()
        self.GetCameraPara1()
        self.UpdateUI()

    """ ExposureTime改变"""

    def SetExposureTime(self):
        self.Camera.SetExposureTime(self.ui.doubleSpinBox_ExposureTime.value())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
    
    """ ExposureTime1改变"""

    def SetExposureTime1(self):
        self.Camera.SetExposureTime1(self.ui.doubleSpinBox_ExposureTime1.value())
        self.UpdateCameraPara_Range1()
        self.GetCameraPara1()

    """ TriggerMode改变"""

    def SetTriggerAuto(self):
        self.Camera.SetTriggerAuto(self.ui.comboBox_TriggerMode.currentText())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
        self.UpdateUI()

    """ TriggerMode1改变"""

    def SetTriggerAuto1(self):
        self.Camera.SetTriggerAuto1(self.ui.comboBox_TriggerMode1.currentText())
        self.UpdateCameraPara_Range1()
        self.GetCameraPara1()
        self.UpdateUI()

    """ TriggerSource改变"""

    def SetTriggerSource(self):
        self.Camera.SetTriggerSource(self.ui.comboBox_TriggerSource.currentText())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
        self.UpdateUI()

    """ TriggerSource1改变"""

    def SetTriggerSource1(self):
        self.Camera.SetTriggerSource1(self.ui.comboBox_TriggerSource1.currentText())
        self.UpdateCameraPara_Range1()
        self.GetCameraPara1()
        self.UpdateUI()

    """ 发送软触发"""

    def SendSoftwareCommand(self):
        self.Camera.SendSoftWareCommand()

    """ 发送软触发1"""

    def SendSoftwareCommand1(self):
        self.Camera.SendSoftWareCommand1()

    """ GainAuto改变"""

    def SetGainAuto(self):
        self.Camera.SetGainAuto(self.ui.comboBox_GainAuto.currentText())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
        self.UpdateUI()

    """ GainAuto1改变"""

    def SetGainAuto1(self):
        self.Camera.SetGainAuto1(self.ui.comboBox_GainAuto1.currentText())
        self.UpdateCameraPara_Range1()
        self.GetCameraPara1()
        self.UpdateUI()

    """ GainValue值改变"""

    def SetGainValue(self):
        self.Camera.SetGainValue(self.ui.doubleSpinBox_GainValue.value())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()

    """ GainValue1值改变"""

    def SetGainValue1(self):
        self.Camera.SetGainValue1(self.ui.doubleSpinBox_GainValue1.value())
        self.UpdateCameraPara_Range1()
        self.GetCameraPara1()

    """ 点击停止播放"""

    def PB_StopAcq_clicked(self):
        self.Camera.StopAcquisition()
        self.TimerForShowImageInGraphicsView.stop()
        self.UpdateUI()
        DahengCamera.num = 0

    """ 点击放大"""

    def PB_ZoomIn_clicked(self):
        self.ImageWidthInGraphicsView += 100

    """
'   222222222222222       SSSSSSSSSSSSSSS              AAA   VVVVVVVV           VVVVVVVVEEEEEEEEEEEEEEEEEEEEEE
'  2:::::::::::::::22   SS:::::::::::::::S            A:::A  V::::::V           V::::::VE::::::::::::::::::::E
'  2::::::222222:::::2 S:::::SSSSSS::::::S           A:::::A V::::::V           V::::::VE::::::::::::::::::::E
'  2222222     2:::::2 S:::::S     SSSSSSS          A:::::::AV::::::V           V::::::VEE::::::EEEEEEEEE::::E
'              2:::::2 S:::::S                     A:::::::::AV:::::V           V:::::V   E:::::E       EEEEEE
'              2:::::2 S:::::S                    A:::::A:::::AV:::::V         V:::::V    E:::::E             
'           2222::::2   S::::SSSS                A:::::A A:::::AV:::::V       V:::::V     E::::::EEEEEEEEEE   
'      22222::::::22     SS::::::SSSSS          A:::::A   A:::::AV:::::V     V:::::V      E:::::::::::::::E   
'    22::::::::222         SSS::::::::SS       A:::::A     A:::::AV:::::V   V:::::V       E:::::::::::::::E   
'   2:::::22222               SSSSSS::::S     A:::::AAAAAAAAA:::::AV:::::V V:::::V        E::::::EEEEEEEEEE   
'  2:::::2                         S:::::S   A:::::::::::::::::::::AV:::::V:::::V         E:::::E             
'  2:::::2                         S:::::S  A:::::AAAAAAAAAAAAA:::::AV:::::::::V          E:::::E       EEEEEE
'  2:::::2       222222SSSSSSS     S:::::S A:::::A             A:::::AV:::::::V         EE::::::EEEEEEEE:::::E
'  2::::::2222222:::::2S::::::SSSSSS:::::SA:::::A               A:::::AV:::::V          E::::::::::::::::::::E
'  2::::::::::::::::::2S:::::::::::::::SSA:::::A                 A:::::AV:::V           E::::::::::::::::::::E
'  22222222222222222222 SSSSSSSSSSSSSSS AAAAAAA                   AAAAAAAVVV            EEEEEEEEEEEEEEEEEEEEEE
    """

    """同步采集进程唤起"""

    def PB_StartCamImgSaveTogether_clicked(self):
        if self.imgSeqready:
            child.show()
            position = (
                self.ui.spinBox_SLMdislocation_x.value() + GetSystemMetrics(0),
                self.ui.spinBox_SLMdislocation_y.value())
            child.move(position[0], position[1])
            child.resize(self.ui.spinBox_SLMdisresloution_x.value(),
                         self.ui.spinBox_SLMdisresloution_y.value())
        if self.t_CamImgSaveTogether.is_alive() is False:
            self.count_DMDrunning = self.count_DMDrunning + 1
            self.t_CamImgSaveTogether = "t_CamImgSaveTogether" + str(self.count_DMDrunning)
            self.t_CamImgSaveTogether = threading.Thread(target=self.CamImgSaveTogether)
            self.t_CamImgSaveTogether.start()



    """同步采集"""

    def CamImgSaveTogether(self):
        NbofSave = self.ui.spinBox_Camsavenb.value()
        SaveTiming = 1 / self.ui.spinBox_Camsavefre.value()
        power_measurements = []
        print(SaveTiming)
        if self.DMDready:
            self.DMDrunning = True
            self.CamSaving = True
            self.UpdateUI()
            for i in range(NbofSave):
                FileName = "{:05}.jpeg".format(i + 1)
                SaveFile = os.path.join(
                    self.ui.LineEditDistheSavePathofCamImg.text(), FileName
                )
                self.DMD.Run(SequenceId=i + 1, loop=False)
                time.sleep(SaveTiming - 0.001)
                self.ImagetoSave.save(SaveFile)
                if self.PMready:
                    power_measurements.append(self.power.value)

                else:
                    SaveFile1 = os.path.join(
                        self.ui.LineEditDistheSavePathofCamImg1.text(), FileName
                    )
                    self.ImagetoSave1.save(SaveFile1)
                self.DMD.Wait()
            df = pd.DataFrame(power_measurements)
            FileName = "PM.xlsx"
            SaveFile1 = os.path.join(
                self.ui.LineEditDistheSavePathofCamImg1.text(), FileName
            )
            df.to_excel(SaveFile1, index=False, engine='openpyxl')
            self.DMD.Wait()
            self.DMD.Halt()
            self.DMDrunning = False
            self.CamSaving = False
        if self.SLMready:
            self.CamSaving = True
            self.UpdateUI()
            FileName = None
            print("camsavestart")
            for i in range(NbofSave):
                FileName = "{:05}.jpeg".format(i + 1)
                SaveFile = os.path.join(
                    self.ui.LineEditDistheSavePathofCamImg.text(), FileName
                )
                img_slm = self.imgSeqforSLM[i].astype(np.uint8)
                img_slm = cv2.cvtColor(img_slm, cv2.COLOR_GRAY2RGB)
                len_x = img_slm.shape[1]  # 获取图像大小
                wid_y = img_slm.shape[0]
                frame = QImage(
                    img_slm.data, len_x, wid_y, len_x * 3, QImage.Format_RGB888
                )  # 此处如果不加len_x*3，就会发生倾斜
                pix = QPixmap(frame)
                child.label_SLM_PlayImg.setPixmap(pix)
                time.sleep(30 / 1000)
                self.ImagetoSave.save(SaveFile)
                if self.PMready:
                    power_measurements.append(self.power.value)
                else:
                    SaveFile1 = os.path.join(
                        self.ui.LineEditDistheSavePathofCamImg1.text(), FileName
                    )
                    self.ImagetoSave1.save(SaveFile1)
                time.sleep(SaveTiming - (30 / 1000))
            df = pd.DataFrame(power_measurements)
            FileName = "PM.xlsx"
            SaveFile1 = os.path.join(
                self.ui.LineEditDistheSavePathofCamImg1.text(), FileName
            )
            df.to_excel(SaveFile1, index=False, engine='openpyxl')
            print("camsaveover")
            self.CamSaving = False
            #child.close()
            print("slm dis closed")
            self.UpdateUI()

        else:
            return
    
    """选择同步保存路径"""

    def PB_SelecttheSavePathofCamImg_clicked1(self):
        theSavePathofCamImg1 = QtWidgets.QFileDialog.getExistingDirectory(
            None, "选取文件夹", r"C:/Users\59727\Desktop\gi_catch"
        )  # 起始路径
        self.ui.LineEditDistheSavePathofCamImg1.setText(theSavePathofCamImg1)
        self.UpdateUI()

    """
'     SSSSSSSSSSSSSSS              AAA   VVVVVVVV           VVVVVVVVEEEEEEEEEEEEEEEEEEEEEE
'   SS:::::::::::::::S            A:::A  V::::::V           V::::::VE::::::::::::::::::::E
'  S:::::SSSSSS::::::S           A:::::A V::::::V           V::::::VE::::::::::::::::::::E
'  S:::::S     SSSSSSS          A:::::::AV::::::V           V::::::VEE::::::EEEEEEEEE::::E
'  S:::::S                     A:::::::::AV:::::V           V:::::V   E:::::E       EEEEEE
'  S:::::S                    A:::::A:::::AV:::::V         V:::::V    E:::::E             
'   S::::SSSS                A:::::A A:::::AV:::::V       V:::::V     E::::::EEEEEEEEEE   
'    SS::::::SSSSS          A:::::A   A:::::AV:::::V     V:::::V      E:::::::::::::::E   
'      SSS::::::::SS       A:::::A     A:::::AV:::::V   V:::::V       E:::::::::::::::E   
'         SSSSSS::::S     A:::::AAAAAAAAA:::::AV:::::V V:::::V        E::::::EEEEEEEEEE   
'              S:::::S   A:::::::::::::::::::::AV:::::V:::::V         E:::::E             
'              S:::::S  A:::::AAAAAAAAAAAAA:::::AV:::::::::V          E:::::E       EEEEEE
'  SSSSSSS     S:::::S A:::::A             A:::::AV:::::::V         EE::::::EEEEEEEE:::::E
'  S::::::SSSSSS:::::SA:::::A               A:::::AV:::::V          E::::::::::::::::::::E
'  S:::::::::::::::SSA:::::A                 A:::::AV:::V           E::::::::::::::::::::E
'   SSSSSSSSSSSSSSS AAAAAAA                   AAAAAAAVVV            EEEEEEEEEEEEEEEEEEEEEE
    """

    """采集函数进程唤起"""

    def PB_StartCamImgSave_clicked(self):
        if self.imgSeqready and self.SLMready:
            child.show()
            position = (
                self.ui.spinBox_SLMdislocation_x.value() + GetSystemMetrics(0),
                self.ui.spinBox_SLMdislocation_y.value())
            child.move(position[0], position[1])
            child.resize(self.ui.spinBox_SLMdisresloution_x.value(),
                         self.ui.spinBox_SLMdisresloution_y.value())
        if self.t_CamImgSave.is_alive() is False:
            self.count_DMDrunning = self.count_DMDrunning + 1
            self.t_CamImgSave = "t_CamImgSave" + str(self.count_DMDrunning)
            self.t_CamImgSave = threading.Thread(target=self.CamImgSave)
            self.t_CamImgSave.start()

    """采集函数"""

    def CamImgSave(self):

        NbofSave = self.ui.spinBox_Camsavenb.value()
        SaveTiming = 1 / self.ui.spinBox_Camsavefre.value()
        if self.DMDready:
            self.DMDrunning = True
            self.CamSaving = True
            self.UpdateUI()
            for i in range(NbofSave):
                FileName = "{:05}.jpeg".format(i + 1)
                SaveFile = os.path.join(
                    self.ui.LineEditDistheSavePathofCamImg.text(), FileName
                )
                self.DMD.Run(SequenceId=i + 1, loop=False)
                time.sleep(SaveTiming - 0.001)
                self.ImagetoSave.save(SaveFile)
                self.DMD.Wait()
            self.DMD.Wait()
            self.DMD.Halt()
            self.DMDrunning = False
            self.CamSaving = False
        if self.SLMready:
            self.CamSaving = True
            self.UpdateUI()
            FileName = None
            SaveFile = None
            for i in range(NbofSave):
                FileName = "{:05}.jpeg".format(i + 1)
                SaveFile = os.path.join(
                    self.ui.LineEditDistheSavePathofCamImg.text(), FileName
                )
                img_slm = self.imgSeqforSLM[i].astype(np.uint8)
                img_slm = cv2.cvtColor(img_slm, cv2.COLOR_GRAY2RGB)
                len_x = img_slm.shape[1]  # 获取图像大小
                wid_y = img_slm.shape[0]
                frame = QImage(
                    img_slm.data, len_x, wid_y, len_x * 3, QImage.Format_RGB888
                )  # 此处如果不加len_x*3，就会发生倾斜
                pix = QPixmap(frame)
                child.label_SLM_PlayImg.setPixmap(pix)
                time.sleep(10 / 1000)
                print(i)
                self.ImagetoSave.save(SaveFile)
                time.sleep(1 / SaveTiming-(10 / 1000))
            self.CamSaving = False
            child.close()
            self.UpdateUI()
        else:
            return

    """选择保存路径"""

    def PB_SelecttheSavePathofCamImg_clicked(self):
        theSavePathofCamImg = QtWidgets.QFileDialog.getExistingDirectory(
            None, "选取文件夹", r"C:/Users\59727\Desktop\gi_catch\ccd_511"
        )  # 起始路径
        self.ui.LineEditDistheSavePathofCamImg.setText(theSavePathofCamImg)
        self.UpdateUI()

    """
   SSSSSSSSSSSSSSS LLLLLLLLLLL             MMMMMMMM               MMMMMMMM
 SS:::::::::::::::SL:::::::::L             M:::::::M             M:::::::M
S:::::SSSSSS::::::SL:::::::::L             M::::::::M           M::::::::M
S:::::S     SSSSSSSLL:::::::LL             M:::::::::M         M:::::::::M
S:::::S              L:::::L               M::::::::::M       M::::::::::M
S:::::S              L:::::L               M:::::::::::M     M:::::::::::M
 S::::SSSS           L:::::L               M:::::::M::::M   M::::M:::::::M
  SS::::::SSSSS      L:::::L               M::::::M M::::M M::::M M::::::M
    SSS::::::::SS    L:::::L               M::::::M  M::::M::::M  M::::::M
       SSSSSS::::S   L:::::L               M::::::M   M:::::::M   M::::::M
            S:::::S  L:::::L               M::::::M    M:::::M    M::::::M
            S:::::S  L:::::L         LLLLLLM::::::M     MMMMM     M::::::M
SSSSSSS     S:::::SLL:::::::LLLLLLLLL:::::LM::::::M               M::::::M
S::::::SSSSSS:::::SL::::::::::::::::::::::LM::::::M               M::::::M
S:::::::::::::::SS L::::::::::::::::::::::LM::::::M               M::::::M
 SSSSSSSSSSSSSSS   LLLLLLLLLLLLLLLLLLLLLLLLMMMMMMMM               MMMMMMMM
    """

    """ 点击连接SLM"""

    def PB_connectSLM_clicked(self):
        if self.t_connectSLM.is_alive() is False:  # 判断线程的状态
            self.count_DMDrunning = self.count_DMDrunning + 1
            self.t_connectSLM = "t_connectSLM" + str(self.count_DMDrunning)
            self.t_connectSLM = threading.Thread(target=self.connectSLM)
            self.t_connectSLM.start()

    """ 连接SLM函数"""

    def connectSLM(self):
        FileName = os.path.join(
            os.getcwd(),'sample.png'
        )
        image_sample = cv2.imread(FileName)
        image_sample = image_sample[0:self.imgSeqforSLM[0].shape[0],0:self.imgSeqforSLM[0].shape[1]]
        print(image_sample.shape)
        image_sample = cv2.cvtColor(image_sample, cv2.COLOR_BGR2GRAY)
        for i in range(self.imgSeqreadytosendnum):
            self.imgSeqforSLM[i] = self.imgSeqforSLM[i]+image_sample
            #self.imgSeqforSLM[i] = cv2.add(self.imgSeqforSLM[i]+image_sample)
        MonitorNumber = GetSystemMetrics(SM_CMONITORS)
        MajorScreenWidth = GetSystemMetrics(0)
        MajorScreenHeight = GetSystemMetrics(1)
        aScreenWidth = GetSystemMetrics(SM_CXVIRTUALSCREEN)
        aScreenHeight = GetSystemMetrics(SM_CYVIRTUALSCREEN)
        self.AllScreen = (aScreenWidth, aScreenHeight)
        ResolvingPower = [1280, 720, 1920, 1080, 1920,1200,2560, 1440, 3840, 2160, 2160, 7680, 4320, ]
        self.MainScreen = None
        self.SecondaryScreen = None
        if MonitorNumber > 1:
            self.SLMready = True
            self.UpdateUI()
            SecondaryScreenWidth = aScreenWidth - MajorScreenWidth
            if GetSystemMetrics(0) > GetSystemMetrics(1):
                self.MainScreen = (GetSystemMetrics(0), GetSystemMetrics(1))
            else:
                self.MainScreen = (GetSystemMetrics(0), GetSystemMetrics(1))
            for i in range(0, len(ResolvingPower) - 1, 2):
                if SecondaryScreenWidth == ResolvingPower[i]:
                    self.SecondaryScreen = (ResolvingPower[i], ResolvingPower[i + 1])
                    self.ui.label_SLMInformation.setText(
                        "SLM已连接"
                      #  + str(ResolvingPower[i])
                       # + " X "
                       # + str(ResolvingPower[i + 1])
                    )
                    return "副屏(竖屏)尺寸：", self.SecondaryScreen
                    break
            for i in range(1, len(ResolvingPower) - 1, 2):
                if SecondaryScreenWidth == ResolvingPower[i]:
                    self.SecondaryScreen = (ResolvingPower[i], ResolvingPower[i + 1])
                    self.ui.label_SLMInformation.setText(
                        "SLM已连接，分辨率："
                        #+ str(ResolvingPower[i])
                        #+ " X "
                        #+ str(ResolvingPower[i - 1])
                    )
                    return "副屏(竖屏)尺寸", self.SecondaryScreen
                    break

    def PB_uptoSLM_clicked(self):
        #if self.t_uptoSLM.is_alive() is False:  # 判断线程的状态
            #self.count_DMDrunning = self.count_DMDrunning + 1
            #self.t_uptoSLM = "t_uptoSLM" + str(self.count_DMDrunning)
            #self.t_uptoSLM = threading.Thread(target=self.uptoSLM)
            #self.t_uptoSLM.start()
        print(self.imgSeqforSLM[0].shape[0])

    #def uptoSLM(self):
        #child.show()

    def PB_SLMplay_clicked(self):
        child.show()
        if self.imgSeqready:
            position = (
            self.ui.spinBox_SLMdislocation_x.value() + GetSystemMetrics(0), self.ui.spinBox_SLMdislocation_y.value())
            child.move(position[0], position[1])
            child.resize(self.ui.spinBox_SLMdisresloution_x.value(),
                self.ui.spinBox_SLMdisresloution_y.value())


        if self.t_SLMplay.is_alive() is False:  # 判断线程的状态
             self.count_DMDrunning = self.count_DMDrunning + 1
             self.t_SLMplay = "t_SLMplay" + str(self.count_DMDrunning)
             self.t_SLMplay = threading.Thread(target=self.SLMplay)
             self.t_SLMplay.start()

    def SLMplay(self):
        self.SLMPlaying = True
        self.UpdateUI()
        if self.imgSeqready:
            for i in range(self.imgSeqreadytosendnum):
                img_slm = self.imgSeqforSLM[i].astype(np.uint8)
                img_slm = cv2.cvtColor(img_slm, cv2.COLOR_GRAY2RGB)
                len_x = img_slm.shape[1]  # 获取图像大小
                wid_y = img_slm.shape[0]
                frame = QImage(
                    img_slm.data, len_x, wid_y, len_x * 3, QImage.Format_RGB888
                )  # 此处如果不加len_x*3，就会发生倾斜
                pix = QPixmap(frame)
                child.label_SLM_PlayImg.setPixmap(pix)
                time.sleep(1 / self.ui.spinBox_SLMdisfre.value())
        self.SLMPlaying = False
        print(1111)

        self.UpdateUI()

        return

    """
DDDDDDDDDDDDD        MMMMMMMM               MMMMMMMMDDDDDDDDDDDDD        
D::::::::::::DDD     M:::::::M             M:::::::MD::::::::::::DDD     
D:::::::::::::::DD   M::::::::M           M::::::::MD:::::::::::::::DD   
DDD:::::DDDDD:::::D  M:::::::::M         M:::::::::MDDD:::::DDDDD:::::D  
  D:::::D    D:::::D M::::::::::M       M::::::::::M  D:::::D    D:::::D 
  D:::::D     D:::::DM:::::::::::M     M:::::::::::M  D:::::D     D:::::D
  D:::::D     D:::::DM:::::::M::::M   M::::M:::::::M  D:::::D     D:::::D
  D:::::D     D:::::DM::::::M M::::M M::::M M::::::M  D:::::D     D:::::D
  D:::::D     D:::::DM::::::M  M::::M::::M  M::::::M  D:::::D     D:::::D
  D:::::D     D:::::DM::::::M   M:::::::M   M::::::M  D:::::D     D:::::D
  D:::::D     D:::::DM::::::M    M:::::M    M::::::M  D:::::D     D:::::D
  D:::::D    D:::::D M::::::M     MMMMM     M::::::M  D:::::D    D:::::D 
DDD:::::DDDDD:::::D  M::::::M               M::::::MDDD:::::DDDDD:::::D  
D:::::::::::::::DD   M::::::M               M::::::MD:::::::::::::::DD   
D::::::::::::DDD     M::::::M               M::::::MD::::::::::::DDD     
DDDDDDDDDDDDD        MMMMMMMM               MMMMMMMMDDDDDDDDDDDDD  
    """

    """ 点击初始化DMD"""

    def PB_InitializetheDMD_clicked(self):
        self.DMD = ALP4(version="4.3")
        returnofInitializetheDMD = self.DMD.Initialize()
        if type(returnofInitializetheDMD) == tuple:
            self.ui.label_DMDIni.setText(
                "DMD已连接，分辨率："
                + str(returnofInitializetheDMD[0])
                + " X "
                + str(returnofInitializetheDMD[1])
            )
        else:
            self.ui.label_DMDIni.setText(str(returnofInitializetheDMD))
        self.UpdateUI()

    """ 点击断开DMD连接（手动）"""

    def PB_ManualDisconnectDMD_clicked(self):

        if self.DMDrunning:
            self.DMD.Halt()
            for i in range(self.imgSeqreadytosendnum):
                self.DMD.FreeSeq(SequenceId=self.DMD.Seqs[0])
            self.DMDrunning = False
            self.DMDready = False
        elif self.DMDready:
            for i in range(self.imgSeqreadytosendnum):
                self.DMD.FreeSeq(SequenceId=self.DMD.Seqs[0])
            self.DMDrunning = False
            self.DMDready = False
        returnofManualDisconnectDMD = self.DMD.Free()
        if type(returnofManualDisconnectDMD) == str:
            self.ui.label_DMDIni.setText(returnofManualDisconnectDMD)
            self.DMDready = False
            self.ui.label_DMDInformation.setText("")
        else:
            self.ui.label_DMDIni.setText(str(returnofManualDisconnectDMD))
        self.UpdateUI()

    def PB_UptoDMD_clicked(self):
        if self.imgSeqready:
            self.ui.spinBox_DMDdisfre.setReadOnly(True)
            self.ui.spinBox_DMDdisfre.setStyleSheet(
                "QSpinBox" "{" "background-color : transparent;" "}"
            )
            for i in range(self.imgSeqreadytosendnum):
                self.DMD.SeqAlloc(1, bitDepth=1)
            for i in range(self.imgSeqreadytosendnum):
                if i != self.imgSeqreadytosendnum - 1:
                    self.DMD.SeqPut(
                        SequenceId=i + 1,
                        imgData=self.imgSeqreadytosend[
                                i * self.resolution: (i + 1) * self.resolution
                                ],
                    )
                    self.DMD.SeqControl(ALP_BITNUM, 1, i + 1)
                    self.DMD.SeqControl(ALP_BIN_MODE, ALP_BIN_UNINTERRUPTED, i + 1)
                if i == self.imgSeqreadytosendnum - 1:
                    self.DMD.SeqPut(
                        SequenceId=i + 1,
                        imgData=self.imgSeqreadytosend[i * self.resolution:],
                    )
                    self.DMD.SeqControl(ALP_BITNUM, 1, i + 1)
                    self.DMD.SeqControl(ALP_BIN_MODE, ALP_BIN_UNINTERRUPTED, i + 1)
                self.DMD.SetTiming(
                    SequenceId=i + 1,
                    pictureTime=int(1 / self.ui.spinBox_DMDdisfre.value() * 1000000),
                )
            self.DMDready = True
            self.ui.label_DMDInformation.setText("加载成功，ALP设备就绪")
            self.UpdateUI()
        else:
            self.ui.label_DMDInformation.setText("目前图片序列为空")

    def cleanDMD(self):
        if self.DMDready:
            self.ui.spinBox_DMDdisfre.setReadOnly(False)
            self.ui.spinBox_DMDdisfre.setStyleSheet(
                "QSpinBox" "{" "background-color : white;" "}"
            )
            self.DMDready = False
            self.DMD.Halt()
            for i in range(len(self.DMD.Seqs)):
                self.DMD.FreeSeq(SequenceId=self.DMD.Seqs[0])
            self.ui.label_DMDInformation.setText("DMD内存已清空")
            self.DMD.Free()
            self.DMD = ALP4(version="4.3")
            self.DMD.Initialize()
            self.UpdateUI()
        else:
            self.ui.label_DMDInformation.setText("DMD内存为空")

    def PB_stopDMD_clicked(self):
        self.DMD.Halt()
        self.DMDrunning = False
        threadtokill = self.t_DMDrunning
        terminator(threadtokill)
        self.UpdateUI()

    def PB_runDMD_clicked(self):
        if self.t_DMDrunning.is_alive() is False:  # 判断线程的状态
            self.count_DMDrunning = self.count_DMDrunning + 1
            self.t_DMDrunning = "t_DMDrunning" + str(self.count_DMDrunning)
            self.t_DMDrunning = threading.Thread(target=self.runDMD)
            self.t_DMDrunning.start()

    def runDMD(self):
        if self.DMDready:
            self.DMDrunning = True
            self.UpdateUI()
            for i in range(self.imgSeqreadytosendnum):
                self.DMD.Run(SequenceId=i + 1, loop=False)
                self.DMD.Wait()
            self.DMD.Halt()
            self.DMDrunning = False
            # self.ui.label_DMDInformation.setText("DMD内存已清空")
            self.UpdateUI()
        else:
            return
        
    """
IIIIIIIIIIMMMMMMMM               MMMMMMMM        GGGGGGGGGGGGGEEEEEEEEEEEEEEEEEEEEEENNNNNNNN        NNNNNNNNEEEEEEEEEEEEEEEEEEEEEE
I::::::::IM:::::::M             M:::::::M     GGG::::::::::::GE::::::::::::::::::::EN:::::::N       N::::::NE::::::::::::::::::::E
I::::::::IM::::::::M           M::::::::M   GG:::::::::::::::GE::::::::::::::::::::EN::::::::N      N::::::NE::::::::::::::::::::E
II::::::IIM:::::::::M         M:::::::::M  G:::::GGGGGGGG::::GEE::::::EEEEEEEEE::::EN:::::::::N     N::::::NEE::::::EEEEEEEEE::::E
  I::::I  M::::::::::M       M::::::::::M G:::::G       GGGGGG  E:::::E       EEEEEEN::::::::::N    N::::::N  E:::::E       EEEEEE
  I::::I  M:::::::::::M     M:::::::::::MG:::::G                E:::::E             N:::::::::::N   N::::::N  E:::::E             
  I::::I  M:::::::M::::M   M::::M:::::::MG:::::G                E::::::EEEEEEEEEE   N:::::::N::::N  N::::::N  E::::::EEEEEEEEEE   
  I::::I  M::::::M M::::M M::::M M::::::MG:::::G    GGGGGGGGGG  E:::::::::::::::E   N::::::N N::::N N::::::N  E:::::::::::::::E   
  I::::I  M::::::M  M::::M::::M  M::::::MG:::::G    G::::::::G  E:::::::::::::::E   N::::::N  N::::N:::::::N  E:::::::::::::::E   
  I::::I  M::::::M   M:::::::M   M::::::MG:::::G    GGGGG::::G  E::::::EEEEEEEEEE   N::::::N   N:::::::::::N  E::::::EEEEEEEEEE   
  I::::I  M::::::M    M:::::M    M::::::MG:::::G        G::::G  E:::::E             N::::::N    N::::::::::N  E:::::E             
  I::::I  M::::::M     MMMMM     M::::::M G:::::G       G::::G  E:::::E       EEEEEEN::::::N     N:::::::::N  E:::::E       EEEEEE
II::::::IIM::::::M               M::::::M  G:::::GGGGGGGG::::GEE::::::EEEEEEEE:::::EN::::::N      N::::::::NEE::::::EEEEEEEE:::::E
I::::::::IM::::::M               M::::::M   GG:::::::::::::::GE::::::::::::::::::::EN::::::N       N:::::::NE::::::::::::::::::::E
I::::::::IM::::::M               M::::::M     GGG::::::GGG:::GE::::::::::::::::::::EN::::::N        N::::::NE::::::::::::::::::::E
IIIIIIIIIIMMMMMMMM               MMMMMMMM        GGGGGG   GGGGEEEEEEEEEEEEEEEEEEEEEENNNNNNNN         NNNNNNNEEEEEEEEEEEEEEEEEEEEEE
    """

    """选择生成新序列路径"""

    def PB_SelectSavePathofImgSeqGenerate_clicked(self):
        SavePathofImgSeqGene = QtWidgets.QFileDialog.getExistingDirectory(
            None, "选取文件夹", r"C:/Users\59727\Desktop\gi_catch\origin_511"
        )  # 起始路径
        self.ui.LineEditDistheSavePathofImgSeqGenerate.setText(SavePathofImgSeqGene)
        self.UpdateUI()
        
    """选择打开序列路径"""

    def PB_SelectOpenPathofImgSeqGenerate_clicked(self):
        OpenPathofImgSeqGene = QtWidgets.QFileDialog.getExistingDirectory(
            None, "选取文件夹", "C:/"
        )  # 起始路径
        self.ui.LineEditDistheOpenPathofImgSeqGenerate.setText(OpenPathofImgSeqGene)
        self.UpdateUI()


    def PB_ImgSeqGenerate_clicked(self):
        if self.t_ImgSeqGene.is_alive() is False:  # 判断线程的状态
            self.count_DMDrunning = self.count_DMDrunning + 1
            self.t_ImgSeqGene = "t_ImgSeqGene" + str(self.count_DMDrunning)
            self.t_ImgSeqGene = threading.Thread(target=self.ImgSeqGenerate)
            self.t_ImgSeqGene.start()

    def ImgSeqGenerate(self):
        nbImg = self.ui.spinBox_NumofGeneImgSeq.value()
        resall = self.ui.spinBox_SizeY.value() * nbImg * self.ui.spinBox_SizeX.value()
        imgSeq = np.empty(shape=(resall, 1))
        self.ImgSeqGeneRunning = True
        self.UpdateUI()
        self.imgSeqforSLM = {}
        for i in range(nbImg):
            FileName = "{:05}.jpeg".format(i + 1)
            SaveFile = os.path.join(
                self.ui.LineEditDistheSavePathofImgSeqGenerate.text(), FileName
            )
            img_randint = np.random.randint(
                256,
                high=None,
                size=[
                    self.ui.spinBox_SizeY.value()
                    // self.ui.spinBox_BlockWofGeneImgSeq.value(),
                    self.ui.spinBox_SizeX.value()
                    // self.ui.spinBox_BlockWofGeneImgSeq.value(),
                ],
                dtype=int,
            )
            #) * (2 ** 8 - 1)
            img_randint = img_randint.astype(float)
            img_randint = cv2.resize(
                img_randint,
                None,
                fx=self.ui.spinBox_BlockWofGeneImgSeq.value(),
                fy=self.ui.spinBox_BlockWofGeneImgSeq.value(),
                interpolation=cv2.INTER_AREA,
            )
            img_randint = img_randint.astype(int)

            self.imgSeqforSLM[i] = img_randint.astype("uint8")
            cv2.imwrite(SaveFile, img_randint)
            self.ui.label_ImgGeneinf.setText("(" + str(i + 1) + "/" + str(nbImg) + ")")

            if i < nbImg - 1:
                imgSeq[
                i
                * self.ui.spinBox_SizeY.value()
                * self.ui.spinBox_SizeX.value(): (i + 1)
                                                 * self.ui.spinBox_SizeY.value()
                                                 * self.ui.spinBox_SizeX.value(),
                0,
                ] = img_randint.ravel()
            elif i == nbImg - 1:
                imgSeq[
                i * self.ui.spinBox_SizeY.value() * self.ui.spinBox_SizeX.value():,
                0,
                ] = img_randint.ravel()

            # imgSeq = np.concatenate([imgSeq.ravel(), img_randint.ravel()])
        self.ImgSeqGeneRunning = False
        # self.imgSeqreadytosend = imgSeq
        print("test")
        self.imgSeqreadytosend = np.ones_like(imgSeq)
        self.imgSeqreadytosend = self.imgSeqreadytosend * 255
        self.imgSeqready = True
        self.resolution = self.ui.spinBox_SizeY.value() * self.ui.spinBox_SizeX.value()
        self.imgSeqreadytosendnum = np.size(imgSeq) // self.resolution
        self.ui.label_Seqloadinf.setText(
            "当前序列："
            + str(self.imgSeqreadytosendnum)
            + "张 "
            + str(self.ui.spinBox_SizeX.value())
            + " X "
            + str(self.ui.spinBox_SizeY.value())
        )
        self.UpdateUI()

    def Valuechanged_SetPreofGeneImgSeq(self):
        if self.t_SetPreofGeneImgSeq.is_alive() is False:  # 判断线程的状态
            self.count_DMDrunning = self.count_DMDrunning + 1
            self.t_SetPreofGeneImgSeq = "t_SetPreofGeneImgSeq" + str(
                self.count_DMDrunning
            )
            self.t_SetPreofGeneImgSeq = threading.Thread(target=self.SetPreofGeneImgSeq)
            self.t_SetPreofGeneImgSeq.start()

    def SetPreofGeneImgSeq(self):
        if self.ui.spinBox_BlockWofGeneImgSeq.value() > min(
                self.ui.spinBox_SizeX.value(), self.ui.spinBox_SizeY.value()
        ):
            self.ui.label_PreImgGene.setText("块宽度过大")
        else:
            if (
                    self.ui.spinBox_SizeX.value() > 1000
                    or self.ui.spinBox_SizeY.value() > 1000
            ):
                ratio = self.ui.spinBox_SizeX.value() / self.ui.spinBox_SizeY.value()
                self.ui.label_PreImgGene.setGeometry(
                    QtCore.QRect(115, 124, int(100 * ratio), 100)
                )
            else:
                self.ui.label_PreImgGene.setGeometry(
                    QtCore.QRect(
                        115,
                        124,
                        int(self.ui.spinBox_SizeX.value() // 10),
                        int(self.ui.spinBox_SizeY.value() / 10),
                    )
                )
            img_pre = np.random.randint(
                256,
                high=None,
                size=[
                    self.ui.spinBox_SizeY.value()
                    // self.ui.spinBox_BlockWofGeneImgSeq.value(),
                    self.ui.spinBox_SizeX.value()
                    // self.ui.spinBox_BlockWofGeneImgSeq.value(),
                ],
                dtype=int,
            )
            #) * (2 ** 8 - 1)
            img_pre = img_pre.astype(float)
            img_pre = cv2.resize(
                img_pre,
                None,
                fx=self.ui.spinBox_BlockWofGeneImgSeq.value(),
                fy=self.ui.spinBox_BlockWofGeneImgSeq.value(),
                interpolation=cv2.INTER_AREA,
            )
            img_pre = img_pre.astype(int)
            img_pre = img_pre.astype(np.uint8)
            img_pre = cv2.cvtColor(img_pre, cv2.COLOR_GRAY2RGB)
            len_x = img_pre.shape[1]  # 获取图像大小
            wid_y = img_pre.shape[0]
            frame = QImage(
                img_pre.data, len_x, wid_y, len_x * 3, QImage.Format_RGB888
            )  # 此处如果不加len_x*3，就会发生倾斜
            pix = QPixmap(frame)
            self.ui.label_PreImgGene.setPixmap(pix)
            self.ui.label_PreImgGene.setScaledContents(True)
        self.UpdateUI()
















    def PB_refreshPM_clicked(self):
        if self.t_refreshPM.is_alive() is False:  # 判断线程的状态
            self.count_DMDrunning = self.count_DMDrunning + 1
            self.t_refreshPM = "t_refreshPM" + str(self.count_DMDrunning)
            self.t_refreshPM = threading.Thread(target=self.refreshPM)
            self.t_refreshPM.start()

    def refreshPM(self):
        tlPM = TLPM()
        deviceCount = c_uint32()
        tlPM.findRsrc(byref(deviceCount))
        if deviceCount ==0:
            self.ui.label_PMinf.setText("未找到设备" )
        else:
            self.ui.label_PMinf.setText("找到设备: " + str(deviceCount.value))
            self.resourceName = create_string_buffer(1024)
            for i in range(0, deviceCount.value):
                tlPM.getRsrcName(c_int(i), self.resourceName)
                self.ui.comboBox_PMlist.addItem(str(c_char_p(self.resourceName.raw).value))
                break

        tlPM.close()

    def PB_connectPM_clicked(self):
        if self.t_connectPM.is_alive() is False:  # 判断线程的状态
            self.count_DMDrunning = self.count_DMDrunning + 1
            self.t_connectPM = "t_connectPM" + str(self.count_DMDrunning)
            self.t_connectPM = threading.Thread(target=self.connectPM)
            self.t_connectPM.start()

    def SetPMwl(self):
        self.WavelengthtoSet = c_double(int(self.ui.comboBox_PMwavelength.currentText()))

    def connectPM(self):
        tlPM = TLPM()
        tlPM.open(self.resourceName, c_bool(True), c_bool(True))
        message = create_string_buffer(1024)
        tlPM.getCalibrationMsg(message)
        print(c_char_p(message.raw).value)
        tlPM.setWavelength(c_double(350))
        self.PMready = True
        PowerUnitDisplay ="W"
        self.power = c_double()
        Wavelength2dis = c_double()
        while self.PMready:
            tlPM.measPower(byref(self.power))
            tlPM.setWavelength(self.WavelengthtoSet)
            tlPM.getWavelength(0, byref(Wavelength2dis))
            #power_measurements.append(power.value)
            if self.power.value<1e-6:
                power2dis = self.power.value*1e9
                PowerUnitDisplay ="nW"
            elif self.power.value<1e-3:
                power2dis = self.power.value*1e6
                PowerUnitDisplay ="μW"
            elif self.power.value<1:
                power2dis = self.power.value*1e3
                PowerUnitDisplay ="mW"
            power2dis = "{:.4f}".format(power2dis)
            self.ui.label_PMwl2dis.setText("当前波长："+str(Wavelength2dis.value))
            self.ui.label_PMmeasure.setText(str(power2dis)+PowerUnitDisplay)
            time.sleep(0.05)














    def PB_ImgSeqOpen_clicked(self):
        self.start = time.perf_counter()
        if self.t_ImgSeqOpen.is_alive() is False:  # 判态
            self.count_DMDrunning = self.count_DMDrunning + 1
            self.t_ImgSeqOpen = "t_ImgSeqOpen" + str(self.count_DMDrunning)
            self.t_ImgSeqOpen = threading.Thread(target=self.ImgSeqOpen)
            self.t_ImgSeqOpen.start()

    def ImgSeqOpen(self):
        imgexistcount = 0
        resolution_all = 0
        self.ImgSeqOpenRunning = True
        self.UpdateUI()
        self.imgSeqforSLM = {}
        self.ui.label_ImgOpeninf.setText("正在获取文件内容")
        for name in os.listdir(self.ui.LineEditDistheOpenPathofImgSeqGenerate.text()):
            FileName = os.path.join(
                self.ui.LineEditDistheOpenPathofImgSeqGenerate.text(), name
            )
            if os.path.isfile(FileName):
                # imgc = cv2.imread(FileName)
                imgc = cv2.imdecode(np.fromfile(FileName, dtype=np.uint8), -1)
                if imgc is None:
                    continue
                else:
                    imgexistcount = imgexistcount + 1
                    resolution_imgi = imgc.shape[0] * imgc.shape[1]
                    resolution_all = resolution_all + resolution_imgi
        if imgexistcount == 0:
            self.ui.label_ImgOpeninf.setText("选择的文件夹中无图片")
        else:
            self.ui.label_ImgOpeninginf.setText("正在读取：")
            count = 0
            imgSeq = np.empty(shape=(resolution_all, 1))
            for name in os.listdir(
                    self.ui.LineEditDistheOpenPathofImgSeqGenerate.text()
            ):
                FileName = os.path.join(
                    self.ui.LineEditDistheOpenPathofImgSeqGenerate.text(), name
                )
                if os.path.isfile(FileName):
                    # imgchannelread = cv2.imread(FileName)
                    imgi = cv2.imdecode(np.fromfile(FileName, dtype=np.uint8), 1)
                    gray = cv2.cvtColor(imgi, cv2.COLOR_BGR2GRAY)  ##要二值化图像，必须先将图像转为灰度图
                    ret, binary = cv2.threshold(
                        gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
                    )
                    imgi = gray
                    #imgi = binary
                    imgi_dis = imgi
                    imgir = imgi.ravel()
                    if imgir is None:
                        continue
                    len_x = imgi_dis.shape[1]  # 获取图像大小
                    wid_y = imgi_dis.shape[0]
                    self.resolution = len_x * wid_y
                    if count < imgexistcount - 1:
                        self.imgSeqforSLM[count] = imgi_dis
                        imgSeq[
                        count * self.resolution: (count + 1) * self.resolution, 0
                        ] = imgir
                    elif count == imgexistcount - 1:
                        self.imgSeqforSLM[count] = imgi_dis
                        imgSeq[count * self.resolution:, 0] = imgir
                        self.ui.label_ImgOpeninginf.setText("最后读取的图片：")
                    count = count + 1
                    self.imgSeqreadytosend = imgSeq
                    ratio = wid_y / len_x
                    self.ui.label_PreImgOpen.setGeometry(
                        QtCore.QRect(155, 97, 200, int(200 * ratio))
                    )
                    imgi_dis = cv2.cvtColor(imgi_dis, cv2.COLOR_GRAY2RGB)
                    frame = QImage(
                        imgi_dis.data, len_x, wid_y, len_x * 3, QImage.Format_RGB888
                    )
                    pix = QPixmap(frame)
                    self.ui.label_PreImgOpen.setPixmap(pix)
                    self.ui.label_PreImgOpen.setScaledContents(True)
                    self.ui.label_ImgOpeninf.setText("正在读取" + name)
            self.imgSeqready = True
            self.ImgSeqOpenRunning = False
            imgnum = np.size(imgSeq) // self.resolution
            self.imgSeqreadytosendnum = imgnum
            self.ui.label_ImgOpeninf.setText("读取完成，共读取" + str(imgnum) + "张")
            self.ui.label_Seqloadinf.setText(
                "当前序列：" + str(imgnum) + "张 " + str(len_x) + " X " + str(wid_y)
            )
        self.UpdateUI()
        end = time.perf_counter()

    """ 点击ZoomOut"""


    def SetNumofGeneImgSeq(self):
        return self.ui.spinBox_NumofGeneImgSeq.value()

    def SetSavePathofGeneImgSeq(self):
        return self.ui.spinBox_NumofGeneImgSeq.value()

    def SetisLineEditDistheSavePathofImgSeqGeneratetextChanged(self):
        if self.ui.LineEditDistheSavePathofImgSeqGenerate.text() != "":
            self.isLineEditDistheSavePathofImgSeqGeneratetextChanged = True

    def SetisLineEditDistheOpenPathofImgSeqGeneratetextChanged(self):
        if self.ui.LineEditDistheOpenPathofImgSeqGenerate.text() != "":
            self.isLineEditDistheOpenPathofImgSeqGeneratetextChanged = True

    def SetisLineEditDistheSavePathofCamImgtextChanged(self):
        if self.ui.LineEditDistheSavePathofCamImg.text() != "":
            self.isLineEditDistheSavePathofCamImgtextChanged = True
    def SetisLineEditDistheSavePathofCamImgtextChanged1(self):
        if self.ui.LineEditDistheSavePathofCamImg1.text() != "":
            self.isLineEditDistheSavePathofCamImgtextChanged1 = True

class childWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child=Ui_Dialog()
        self.child.setupUI(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    child = childWindow()

    window.show()

    sys.exit(app.exec_())
