# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 23:36:50 2021

@author: LX
"""
import sys
import ctypes
import time
import pyqtgraph as pg
import threading
import serial
from collections import deque
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from pyqtgraph import DateAxisItem

__version__ = '1.0'


class MainWindow(QMainWindow):
    newdata = pyqtSignal(object)  # 创建信号

    def __init__(self, filename=None, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('温湿度数据采集')
#        self.setWindowIcon(QIcon(r"D:\Github\bouncescope\smile.ico"))

        self.t = []
        self.temp = []
        self.hum = []
        self.history = 3600  # 历史保存数据的数量

        # 定义串口对象
        self.connected = False
        self.port = 'COM4'
        self.baud = 115200

        # 启动线程
        # QTimer.singleShot(0, self.startThread)
        self.btn = QPushButton('点击运行！')
        font = QFont()
        font.setPointSize(16)
        self.label = QLabel("实时获取温湿度数据")
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.data_label = QLabel("Data")
        # self.data_label.setAlignment(Qt.AlignCenter)

        self.pw = pg.PlotWidget(
            # axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        self.pw_hum = pg.PlotWidget()
        # setup pyqtgraph
        self.init_pg_temp()  # 温度
        self.init_pg_hum()  # 湿度

        # 设置布局
        vb = QVBoxLayout()
        hb = QHBoxLayout()

        vb.addWidget(self.label)
        vb.addWidget(self.btn)

        hb.addWidget(self.pw)
        hb.addWidget(self.pw_hum)

        vb.addLayout(hb)
        vb.addWidget(self.data_label)

        self.cwidget = QWidget()
        self.cwidget.setLayout(vb)
        self.setCentralWidget(self.cwidget)

        self.btn.clicked.connect(self.startThread)
        self.newdata.connect(self.updatePlot)

    def init_pg_temp(self):
        # 设置图表标题
        self.pw.setTitle("温度变化趋势")
        # 设置上下左右的label
        self.pw.setLabel("left", "气温(摄氏度)")
        self.pw.setLabel("bottom", "时间")
        # 设置Y轴 刻度 范围
        # self.pw.setYRange(min=10,max=50)  # 最大值
        # 显示表格线
        self.pw.showGrid(x=True, y=True)
        # 背景色改为白色
        self.pw.setBackground('w')
        # 居中显示 PlotWidget
        # self.setCentralWidget(self.pw)
        axis = DateAxisItem()  # 设置时间轴，主要此时x的数据为时间戳time.time()
        self.pw.setAxisItems({'bottom': axis})
        self.curve_temp = self.pw.getPlotItem().plot(
            pen=pg.mkPen('r', width=2)
        )

    def init_pg_hum(self):

        # 设置图表标题
        self.pw_hum.setTitle("湿度度变化趋势")
        # 设置上下左右的label
        self.pw_hum.setLabel("left", "湿度")
        self.pw_hum.setLabel("bottom", "时间")
        # 设置Y轴 刻度 范围
        # self.pw_hum.setYRange(min=10, max=100)  # 最大值
        # 显示表格线
        self.pw_hum.showGrid(x=True, y=True)
        # 背景色改为白色
        self.pw_hum.setBackground('w')
        # 居中显示 PlotWidget
        # self.setCentralWidget(self.pw_hum)
        # 实时显示应该获取 plotItem， 调用setData，
        # 这样只重新plot该曲线，性能更高
        axis = DateAxisItem()
        self.pw_hum.setAxisItems({'bottom': axis})
        self.curve_hum = self.pw_hum.getPlotItem().plot(
            pen=pg.mkPen('b', width=2)
        )

    def startThread(self):
        '''
        这里使用python的threading.Thread构造线程，并将线程设置为守护线程，这样
        主线程退出后守护线程也会跟着销毁
        '''
        self.btn.setEnabled(False)
        print('Start lisnening to the COM-port')
        # timeout参数很重要！可以结合波特率和传输的数据量计算出数据发送所需的时间
        serial_port = serial.Serial(self.port, self.baud, timeout=0.1)
        thread = threading.Thread(target=self.read_from_port, args=(serial_port,))
        thread.setDaemon(True)  # 守护线程
        thread.start()  # 启动线程

    def updatePlot(self, signal):
        '''更新绘图'''
        self.curve_temp.getViewBox().enableAutoRange()
        self.curve_temp.getViewBox().setAutoVisible()
        self.curve_temp.setData(signal[0], signal[1][0])

        self.curve_hum.getViewBox().enableAutoRange()
        self.curve_hum.getViewBox().setAutoVisible()
        self.curve_hum.setData(signal[0], signal[1][1])

    def process_data(self, data: str):
        ''''处理数据，注意原来通过串口发送的数据格式'''

        if len(self.t) >= self.history:  # 保证存储数量为设定的历史长度数量
            self.t.pop(0)
            self.temp.pop(0)
            self.hum.pop(0)

        if data.startswith('Temp'):
            try:
                # ['Temperature:28.00\r', 'Humidity:28.00']
                data = data.strip().replace(' ', '').replace('\r', '').split('\n')
                print(data)
                self.data_label.setText('Time:' + str(datetime.datetime.now()) + ', ' +
                                        data[0] + ', ' + data[1])
                self.t.append(time.time())
                self.temp.append(float(data[0].split(':')[1].strip()))
                self.hum.append(float(data[1].split(':')[1].strip()))
            except:
                print('No valid data')

            signal = (self.t, (self.temp, self.hum))
            self.newdata.emit(signal)
        else:
            print('数据格式错误，接收到的数据为：', data)

    def read_all(self, port, chunk_size=200):
        """Read all characters on the serial port and return them.
        参考：https://stackoverflow.com/questions/19161768/pyserial-inwaiting-returns-incorrect-number-of-bytes
        """
        if not port.timeout:
            raise TypeError('Port needs to have a timeout set!')

        read_buffer = b''
        while True:
            # Read in chunks. Each chunk will wait as long as specified by
            # timeout. Increase chunk_size to fail quicker
            byte_chunk = port.read(size=chunk_size)
            read_buffer += byte_chunk
            if not len(byte_chunk) == chunk_size:
                break

        return read_buffer

    # 从串口读取数据
    def read_from_port(self, ser):
        while True:
            bytedata = self.read_all(ser)
            if bytedata:
                self.process_data(bytedata.decode())  # 处理数据

    def stopThread(self):
        print('Stop the thread...')

    def closeEvent(self, event):
        if self.okToContinue():
            event.accept()
            self.stopThread()
        else:
            event.ignore()

    def okToContinue(self):
        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()
    app.exec_()
