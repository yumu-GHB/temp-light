from PyQt5 import Qt, QtGui, QtCore, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from ui_SerialPlot import Ui_Form
from pyqtgraph import DateAxisItem
import pyqtgraph as pg
import time
import datetime
import sys
import threading
import serial

class SerialPlot(Qt.QWidget):

#    newdata = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # 修改窗口样式
        self.setWindowTitle('串口绘图工具')
        #self.setFixedSize(500, 320)
        self.t = []
        self.temp = []
        self.light = []
        self.history = 3600  # 历史保存数据的数量

        # 定义串口对象
        self.COM = QSerialPort()
        self.port_list = QSerialPortInfo.availablePorts()

        # 读取串口信息
        for com_port in self.port_list:
            self.ui.comport_comboBox.addItem(com_port.portName())
        self.COM.setPortName(self.port_list[0].portName())

        # 设置回调函数
        self.ui.comport_comboBox.activated[str].connect(self.on_comport_changed)
        self.ui.baudrate_comboBox.activated[str].connect(self.on_baudrare_changed)

        # 其他变量与回调函数
        self.open_status = 'closed'
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(50)
        self.ui.pushButton.clicked.connect(self.on_pushbutton)
#        self.data_label = QtWidgets.QLabel("Data")
#        self.newdata.connect(self.updatePlot)

        # 绘图相关变量与回调函数
        self.pw_temp = pg.PlotWidget(self, background='w')
        self.pw_light = pg.PlotWidget(self, background='w')
        # setup pyqtgraph
        self.init_pg_temp()  # 温度
        self.init_pg_light()  # 湿度

    def init_pg_temp(self):
        # 设置图表标题
        self.pw_temp.setTitle("温度变化趋势")
        self.pw_temp.setGeometry(QtCore.QRect(10, 10, 480, 270))
        # 设置上下左右的label
        self.pw_temp.setLabel("left", "气温(摄氏度)")
        self.pw_temp.setLabel("bottom", "时间")
        # 设置Y轴 刻度 范围
        # self.pw_temp.setYRange(min=10,max=50)  # 最大值
        # 显示表格线
        self.pw_temp.showGrid(x=True, y=True)
        # 背景色改为白色
        self.pw_temp.setBackground('w')
        # 居中显示 PlotWidget
        # self.setCentralWidget(self.pw_temp)
        axis = DateAxisItem()  # 设置时间轴，主要此时x的数据为时间戳time.time()
        self.pw_temp.setAxisItems({'bottom': axis})
        self.curve_temp = self.pw_temp.getPlotItem().plot(
            pen=pg.mkPen('r', width=2)
        )

    def init_pg_light(self):

        # 设置图表标题
        self.pw_light.setTitle("光强变化趋势")
        self.pw_light.setGeometry(QtCore.QRect(510, 10, 480, 270))
        # 设置上下左右的label
        self.pw_light.setLabel("left", "光强")
        self.pw_light.setLabel("bottom", "时间")
        # 设置Y轴 刻度 范围
        # self.pw_light.setYRange(min=10, max=100)  # 最大值
        # 显示表格线
        self.pw_light.showGrid(x=True, y=True)
        # 背景色改为白色
        self.pw_light.setBackground('w')
        # 居中显示 PlotWidget
        # self.setCentralWidget(self.pw_light)
        # 实时显示应该获取 plotItem， 调用setData，
        # 这样只重新plot该曲线，性能更高
        axis = DateAxisItem()
        self.pw_light.setAxisItems({'bottom': axis})
        self.curve_light = self.pw_light.getPlotItem().plot(
            pen=pg.mkPen('b', width=2)
        )


    def on_comport_changed(self, com_port):
        self.COM.setPortName(com_port)

    def on_baudrare_changed(self, baud_item):
        baud_rate = int(baud_item.split(' ')[0])
        self.COM.setBaudRate(baud_rate)

    def on_pushbutton(self):
        if self.open_status == 'closed':
            if not self.COM.open(QSerialPort.ReadWrite):
                return
            self.t = []
            self.temp = []
            self.light = []
            self.curve_temp.clear()
            self.curve_light.clear()
            self.ui.pushButton.setText('STOP')
            self.ui.pushButton.setStyleSheet(
               '#pushButton{background: #cb5050; color: white;}'
            )
            self.open_status = 'opened'
        else:
            self.COM.close()
            self.ui.pushButton.setText('START')
            self.ui.pushButton.setStyleSheet(
               '#pushButton{background: #cdcdcd; color: white;}'
            )
            self.open_status = 'closed'

    def on_timeout(self):
        # 检测串口端口信息
        if len(QSerialPortInfo.availablePorts()) != len(self.port_list):
            self.port_list = QSerialPortInfo.availablePorts()
            self.ui.comport_comboBox.clear()
            for com_port in self.port_list:
                self.ui.comport_comboBox.addItem(self.icon, com_port.portName())
            self.COM.setPortName(self.port_list[0].portName())

        # 判断接收数据个数，更新绘图
        if self.COM.bytesAvailable() >= 2:
            rcv_data = self.COM.readAll()
            rcv_data_str = str(rcv_data, encoding='utf-8')
            if rcv_data_str:
                self.process_data(rcv_data_str)  # 处理数据

            self.curve_temp.getViewBox().enableAutoRange()
            self.curve_temp.getViewBox().setAutoVisible()
            self.curve_temp.setData(self.t, self.temp)

            self.curve_light.getViewBox().enableAutoRange()
            self.curve_light.getViewBox().setAutoVisible()
            self.curve_light.setData(self.t, self.light)

    def process_data(self, data: str):
        ''''处理数据，注意原来通过串口发送的数据格式'''

        if len(self.t) >= self.history:  # 保证存储数量为设定的历史长度数量
            self.t.pop(0)
            self.temp.pop(0)
            self.light.pop(0)

        if data.startswith('Temp'):
            try:
                # ['Temperature:28.00\r', 'Humidity:28.00']
                data = data.strip().replace(' ', '').replace('\r', '').split('\n')
                print(data)
                self.ui.label.setText('Time:' + str(datetime.datetime.now()) + ', ' +
                                        data[0] + ', ' + data[1])
                self.t.append(time.time())
                self.temp.append(float(data[0].split(':')[1].strip()))
                self.light.append(float(data[1].split(':')[1].strip()))
            except:
                print('No valid data')

            signal = (self.t, (self.temp, self.light))
#            self.newdata.emit(signal)
        else:
            print('数据格式错误，接收到的数据为：', data)



    def closeEvent(self, event):
        super().closeEvent(event)
        self.COM.close()
        self.timer.stop()


    def writeData(self, data: str):
        if self.COM.isOpen():
            print("COM is open,send_data=", data)
            self.COM.write(data.encode("utf8"))
        else:
            print("COM is not open")

# 神经网络1s输出一个数据，增加一个线程
def test():
    t = 1
    while True:
        if t > 50:
            t = 1
            # print(t)
        else:
            # print(t)
            t = t + 1
        time.sleep(1)
        window.writeData(str(t)+'\r\n')

if __name__ == "__main__":
    thread1 = threading.Thread(target=test, daemon=True)
    app = QtWidgets.QApplication(sys.argv)
    window = SerialPlot()
    thread1.start()
    window.show()
    sys.exit(app.exec_())
