from PyQt5 import Qt, QtGui, QtCore, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from ui_SerialPlot import Ui_Form
import pyqtgraph as pg


class SerialPlot(Qt.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # 修改窗口样式
        self.setWindowTitle('串口绘图工具')
        #self.setFixedSize(500, 320)

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

        # 绘图相关变量与回调函数
        self.time = 0
        self.xdata = []
        self.ydata = []
        self.plotwidget = pg.PlotWidget(self, background='w')
        self.plotwidget.setGeometry(QtCore.QRect(10, 10, 480, 270))
        #self.plotwidget.setAspectLocked()  # 坐标轴等比例缩放
        self.plotwidget.setMouseEnabled(x=False, y=False)  # 关闭鼠标操作
        self.plotwidget.setXRange(1, 12)  # 设置X轴范围
        #self.plotwidget.setYRange(0, 6)  # 设置Y轴范围
        self.pen = pg.mkPen(color='#bd4001', width=2)
        self.curve = self.plotwidget.plot(self.xdata, self.ydata, pen=self.pen)

    def on_comport_changed(self, com_port):
        self.COM.setPortName(com_port)

    def on_baudrare_changed(self, baud_item):
        baud_rate = int(baud_item.split(' ')[0])
        self.COM.setBaudRate(baud_rate)

    def on_pushbutton(self):
        if self.open_status == 'closed':
            if not self.COM.open(QSerialPort.ReadWrite):
                return
            self.time = 0
            self.xdata = []
            self.ydata = []
            self.curve.clear()
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
            value = int.from_bytes(bytes(rcv_data[0:2]), 'little')
            self.xdata.append(self.time * 0.100)
            self.ydata.append(value)
            #self.ydata.append(np.abs(np.random.normal())+1)
            self.time += 1
            self.curve.setData(self.xdata, self.ydata)
            # 设置X轴范围
            if self.time * 0.100 < 12:
                self.plotwidget.setXRange(0, 12)
            else:
                self.plotwidget.setXRange(self.time*0.100-12, self.time*0.100)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.COM.close()
        self.timer.stop()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = SerialPlot()
    window.show()
    sys.exit(app.exec_())
