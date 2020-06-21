import os
import sys
import subprocess # 注意Python3.X 已经删除 commands
from PyQt5 import QtCore, QtWidgets, QtWidgets ,uic
from PyQt5.QtCore import Qt, QThread,pyqtSignal
from PyQt5.QtGui import QPalette, QBrush, QPixmap
import time
import datetime
import socket

runDirectory = sys.path[0] #py脚本运行目录
palette = QPalette()
picInt = 0
picCount = 0
#timeUpdate = 0


def get_cpu_temp():
    tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp)/1000
 
def get_gpu_temp():
    gpu_temp = subprocess.getoutput( '/opt/vc/bin/vcgencmd measure_temp' ).replace( 'temp=', '' ).replace( '\'C', '' )
    return  float(gpu_temp)

def get_host_ip():

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return str(ip)

def todayWeek(nowWeek):
    if nowWeek == "0":
        return"星期天"
    elif nowWeek =="1":
        return"星期一"
    elif nowWeek =="2":
        return"星期二"
    elif nowWeek =="3":
        return"星期三"
    elif nowWeek =="4":
        return"星期四"
    elif nowWeek =="5":
        return"星期五"
    elif nowWeek =="6":
        return"星期六"

class UpdateTime(QThread):
    signal = pyqtSignal(str,str,str)   #括号里填写信号传递的参数类型，调用TimeTick的函数要和这里对应

    def __init__(self):
        super().__init__()

    def __del__(self):
        self.wait()

    def run(self):
        global picInt
        global timeUpdate
        while True:
            timeUpdate = datetime.datetime.now() #每秒获取下时间
            strtime0 = timeUpdate.strftime('%S')

            strtime1 = timeUpdate.strftime('%H:%M:%S')
            strtime2 = timeUpdate.strftime('%w')
            strtime3 = timeUpdate.strftime('%m')
            strtime4 = timeUpdate.strftime('%d')

            self.signal.emit(strtime1,todayWeek(strtime2),str(strtime3+"月"+strtime4+"日"))    # 发射信号

            picInt = int(strtime0)
            time.sleep(1)


class UpdateBackground(QThread):
    signa2 = pyqtSignal(int,float,float,str)

    def __init__(self):
        super().__init__()

    def __del__(self):
        self.wait()

    def run(self):
        global picInt
        global picCount
        while True:
            if picInt == 59:
                cpuTemp = get_cpu_temp()
                gpuTemp = get_gpu_temp()
                ipTemp = get_host_ip()
                picCount += 1
                if picCount > 5: #我们就5 张图片不能大于5
                    picCount = 0
                self.signa2.emit(picCount,cpuTemp,gpuTemp,ipTemp)
            time.sleep(1)
 
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi(runDirectory + "/test.ui", self)


        self.thread = UpdateTime() # 创建一个线程
        self.thread.signal.connect(self.TimeTick) #绑定信号触法的函数
        self.thread.start()    # 启动线程

        self.thread2 = UpdateBackground() #创建第二个线程
        self.thread2.signa2.connect(self.setBackground) 
        self.thread2.start()  

        cpuTemp = get_cpu_temp()
        gpuTemp = get_gpu_temp()
        ipTemp = get_host_ip()
        self.label_Temp.setText("CPU温度:"+str(cpuTemp) +" GPU温度:"+ str(gpuTemp) )
        self.label_IP.setText("IP:"+ipTemp)
        self.show()

    def TimeTick(self,msg,msg2,msg3): #注意传参变量要写
        self.label.setText(msg) 
        self.label_2.setText(msg2)
        self.label_3.setText(msg3)

    def setBackground(self,intCount,cpuTemp,gpuTemp,ipTemp):
        palette = QPalette() #设置调色板
        palette.setBrush(QPalette.Background, QBrush(QPixmap(runDirectory+"/Background"+ str(intCount)+".png")))
        self.setPalette(palette)
        self.label_Temp.setText("CPU温度:"+str(cpuTemp) +" GPU温度:"+ str(gpuTemp))
        self.label_IP.setText("IP:"+ipTemp)
app = QtWidgets.QApplication(sys.argv)
window = Ui()

palette = QPalette() #启动时先设一个背景
palette.setBrush(QPalette.Background, QBrush(QPixmap(runDirectory+"/Background4.png")))

window.setPalette(palette)
window.showFullScreen() #全屏显示
app.exec_()
