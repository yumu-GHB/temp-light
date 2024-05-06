import sys
from ui_serialPort import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets, QtSerialPort


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.serial = QtSerialPort.QSerialPort(self)
        self.ui.pushButton_send.setEnabled(False)
        self.ui.comboBox_baud.setCurrentIndex(1)

        self.slot_init()

    def slot_init(self):
        self.ui.pushButton_serial.clicked.connect(self.pushButton_serial_clicked)
        self.ui.pushButton_search.clicked.connect(self.pushButton_search_clicked)
        self.ui.pushButton_send.clicked.connect(self.pushButton_send_clicked)
        self.ui.pushButton_clear.clicked.connect(self.pushButton_clear_clicked)
        self.serial.readyRead.connect(self.serialPort_readyRead)

    def serialPort_readyRead(self):
        buffer = self.serial.read(1)
        print(buffer)

        buffer = str(buffer, encoding='utf-8')
        recStr = self.ui.textEdit_rece.toPlainText()
        recStr += buffer
        self.ui.textEdit_rece.clear()
        self.ui.textEdit_rece.append(recStr)

    def pushButton_send_clicked(self):
        data = bytes(self.ui.textEdit_send.toPlainText(), encoding='utf-8')
        data = QtCore.QByteArray(data)
        self.serial.write(data)

    def pushButton_clear_clicked(self):
        self.ui.textEdit_rece.clear()

    def pushButton_search_clicked(self):
        self.ui.comboBox_port.clear()

        for i in QtSerialPort.QSerialPortInfo.availablePorts():  # 静态函数
            self.ui.comboBox_port.addItem(i.portName())

    def pushButton_serial_clicked(self):
        if self.ui.pushButton_serial.text() == str("打开串口"):
            self.serial.setPortName(self.ui.comboBox_port.currentText())
            self.serial.setBaudRate(QtSerialPort.QSerialPort.Baud115200)
            self.serial.setDataBits(QtSerialPort.QSerialPort.Data8)
            self.serial.setParity(QtSerialPort.QSerialPort.NoParity)
            self.serial.setStopBits(QtSerialPort.QSerialPort.OneStop)
            self.serial.setFlowControl(QtSerialPort.QSerialPort.NoFlowControl)

            self.ui.pushButton_serial.setText("关闭串口")
            if not self.serial.open(QtCore.QIODevice.ReadWrite):
                QtWidgets.QMessageBox.about(self,"提示","无法打开串口!")
                return

            self.ui.comboBox_baud.setEnabled(False)
            self.ui.comboBox_data.setEnabled(False)
            self.ui.comboBox_port.setEnabled(False)
            self.ui.comboBox_stop.setEnabled(False)
            self.ui.comboBox_test.setEnabled(False)

            self.ui.pushButton_send.setEnabled(True)
        elif self.ui.pushButton_serial.text() == str("关闭串口"):
            self.serial.close()
            self.ui.pushButton_serial.setText("打开串口")

            self.ui.comboBox_baud.setEnabled(True)
            self.ui.comboBox_data.setEnabled(True)
            self.ui.comboBox_port.setEnabled(True)
            self.ui.comboBox_stop.setEnabled(True)
            self.ui.comboBox_test.setEnabled(True)

            self.ui.pushButton_send.setEnabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
