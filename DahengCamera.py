import gxipy as gx
import time
import threading

rawImageUpdateList = []
rawImageUpdate = None
num = 0
rawImageUpdateList1 = []
rawImageUpdate1 = None
num1 = 0


def capture_callback(raw_image):
    if raw_image.get_status() == gx.GxFrameStatusList.INCOMPLETE:
        print("incomplete frame")
    else:
        global rawImageUpdateList, num, rawImageUpdate
        rawImageUpdate = raw_image.get_numpy_array()
        if len(rawImageUpdateList) == 0:
            rawImageUpdateList.append(rawImageUpdate)
        else:
            rawImageUpdateList.pop()
            rawImageUpdateList.append(rawImageUpdate)
        num += 1
def capture_callback1(raw_image):
    if raw_image.get_status() == gx.GxFrameStatusList.INCOMPLETE:
        print("incomplete frame")
    else:
        global rawImageUpdateList1, num1, rawImageUpdate1
        rawImageUpdate1 = raw_image.get_numpy_array()
        if len(rawImageUpdateList1) == 0:
            rawImageUpdateList1.append(rawImageUpdate1)
        else:
            rawImageUpdateList1.pop()
            rawImageUpdateList1.append(rawImageUpdate1)
        num1 += 1


class DahengCamera:
    def __init__(self):
        self.cam = None  # 相机对象
        self.cam1 = None  # 相机对象
        self.dev_num = None
        self.dev_info_list = None
        self.device_manager = gx.DeviceManager()
        self.device_manager1 = gx.DeviceManager()
        self.AcquisitionThread = None
        self.AcquisitionThreadNeedBeStop = False
        self.IsCameraOpened = False
        self.IsCameraStartAcq = False

        self.AcquisitionThread1 = None
        self.AcquisitionThreadNeedBeStop1 = False
        self.IsCameraOpened1 = False
        self.IsCameraStartAcq1 = False

    def UpdateCameraList(self):
        self.dev_num, self.dev_info_list = self.device_manager.update_device_list()
        if self.dev_num == 0:
            return False, '0'
        else:
            CameraNameList = []
            for info in self.dev_info_list:
                name = info['model_name']
                CameraNameList.append(name)
            return True, CameraNameList

    def OpenCamera(self, Index):
        if self.dev_num == 0:
            return False
        elif self.IsCameraOpened:
            return True
        else:
            self.cam = self.device_manager.open_device_by_index(Index)

        self.AcquisitionThread = threading.Thread(target=self.AcquisitionThreadFunc_CallBack, args=(), daemon=True)
        self.AcquisitionThread.start()
        self.IsCameraOpened = True
        self.AcquisitionThreadNeedBeStop = False

        return True

    def OpenCamera1(self, Index):
        if self.dev_num == 0:
            return False
        elif self.IsCameraOpened1:
            return True
        else:
            self.cam1 = self.device_manager1.open_device_by_index(Index)

        self.AcquisitionThread1 = threading.Thread(target=self.AcquisitionThreadFunc_CallBack1, args=(), daemon=True)
        self.AcquisitionThread1.start()
        self.IsCameraOpened1 = True
        self.AcquisitionThreadNeedBeStop1 = False

        return True

    def AcquisitionThreadFunc_CallBack(self):
        self.cam.data_stream[0].register_capture_callback(capture_callback)

        while not self.AcquisitionThreadNeedBeStop:
            time.sleep(1)

    def AcquisitionThreadFunc_CallBack1(self):
        self.cam1.data_stream[0].register_capture_callback(capture_callback1)

        while not self.AcquisitionThreadNeedBeStop1:
            time.sleep(1)

    def CloseCamera(self, Index):
        if not self.IsCameraOpened:
            return

        self.AcquisitionThreadNeedBeStop = True
        self.StopAcquisition()
        time.sleep(1)
        self.cam.data_stream[0].unregister_capture_callback()
        self.cam.close_device()

        self.IsCameraOpened = False

    def CloseCamera1(self, Index):
        if not self.IsCameraOpened1:
            return

        self.AcquisitionThreadNeedBeStop1 = True
        self.StopAcquisition1()
        time.sleep(1)
        self.cam1.data_stream[0].unregister_capture_callback()
        self.cam1.close_device()

        self.IsCameraOpened1 = False

    def StartAcquisition(self):
        if self.IsCameraOpened and not self.IsCameraStartAcq:
            self.cam.stream_on()
            self.IsCameraStartAcq = True
        else:
            return

    def StartAcquisition1(self):
        if self.IsCameraOpened1 and not self.IsCameraStartAcq1:
            self.cam1.stream_on()
            self.IsCameraStartAcq1 = True
        else:
            return

    def StopAcquisition(self):
        if self.IsCameraOpened and self.IsCameraStartAcq:
            self.cam.stream_off()
            self.IsCameraStartAcq = False
        else:
            return

    def StopAcquisition1(self):
        if self.IsCameraOpened1 and self.IsCameraStartAcq1:
            self.cam1.stream_off()
            self.IsCameraStartAcq1 = False
        else:
            return

    def GetFPS(self):
        return self.cam.CurrentAcquisitionFrameRate.get()

    def GetExposureModeRange(self):
        return self.cam.ExposureMode.get_range()

    def GetExposureMode(self):
        return self.cam.ExposureMode.get()

    def GetExposureAutoRange(self):
        return self.cam.ExposureAuto.get_range()

    def GetExposureAuto(self):
        return self.cam.ExposureAuto.get()

    def SetExposureAuto(self, ExposureAuto):
        self.cam.ExposureAuto.set(eval('gx.GxAutoEntry.' + ExposureAuto.upper()))
        # self.cam.ExposureAuto.set(Index)

    def GetExposureTime(self):
        return self.cam.ExposureTime.get()

    def SetExposureTime(self, ExposureTime):
        self.cam.ExposureTime.set(ExposureTime)

    def GetTriggerAutoRange(self):
        return self.cam.TriggerMode.get_range()

    def SetTriggerAuto(self, TriggerAuto):
        self.cam.TriggerMode.set(eval('gx.GxSwitchEntry.' + TriggerAuto.upper()))

    def GetTriggerAuto(self):
        return self.cam.TriggerMode.get()

    def GetTriggerSourceRange(self):
        return self.cam.TriggerSource.get_range()

    def SetTriggerSource(self, TriggerSource):
        self.cam.TriggerSource.set(eval('gx.GxTriggerSourceEntry.' + TriggerSource.upper()))

    def GetTriggerSource(self):
        return self.cam.TriggerSource.get()

    def SendSoftWareCommand(self):
        self.cam.TriggerSoftware.send_command()

    def GetGainAutoRange(self):
        return self.cam.GainAuto.get_range()

    def GetGainAuto(self):
        return self.cam.GainAuto.get()

    def GetGainValue(self):
        return self.cam.Gain.get()

    def SetGainAuto(self, GainAuto):
        self.cam.GainAuto.set(eval('gx.GxAutoEntry.' + GainAuto.upper()))

    def SetGainValue(self, GainValue):
        self.cam.Gain.set(GainValue)

    def GetFPS1(self):
        return self.cam1.CurrentAcquisitionFrameRate.get()

    def GetExposureModeRange1(self):
        return self.cam1.ExposureMode.get_range()

    def GetExposureMode1(self):
        return self.cam1.ExposureMode.get()

    def GetExposureAutoRange1(self):
        return self.cam1.ExposureAuto.get_range()

    def GetExposureAuto1(self):
        return self.cam1.ExposureAuto.get()

    def SetExposureAuto1(self, ExposureAuto):
        self.cam1.ExposureAuto.set(eval('gx.GxAutoEntry.' + ExposureAuto.upper()))
        # self.cam.ExposureAuto.set(Index)

    def GetExposureTime1(self):
        return self.cam1.ExposureTime.get()

    def SetExposureTime1(self, ExposureTime):
        self.cam1.ExposureTime.set(ExposureTime)

    def GetTriggerAutoRange1(self):
        return self.cam1.TriggerMode.get_range()

    def SetTriggerAuto1(self, TriggerAuto):
        self.cam1.TriggerMode.set(eval('gx.GxSwitchEntry.' + TriggerAuto.upper()))

    def GetTriggerAuto1(self):
        return self.cam1.TriggerMode.get()

    def GetTriggerSourceRange1(self):
        return self.cam1.TriggerSource.get_range()

    def SetTriggerSource1(self, TriggerSource):
        self.cam1.TriggerSource.set(eval('gx.GxTriggerSourceEntry.' + TriggerSource.upper()))

    def GetTriggerSource1(self):
        return self.cam1.TriggerSource.get()

    def SendSoftWareCommand1(self):
        self.cam1.TriggerSoftware.send_command()

    def GetGainAutoRange1(self):
        return self.cam1.GainAuto.get_range()

    def GetGainAuto1(self):
        return self.cam1.GainAuto.get()

    def GetGainValue1(self):
        return self.cam1.Gain.get()

    def SetGainAuto1(self, GainAuto):
        self.cam1.GainAuto.set(eval('gx.GxAutoEntry.' + GainAuto.upper()))

    def SetGainValue1(self, GainValue):
        self.cam1.Gain.set(GainValue)