################################################
################################################
################################################
#########*******###*******####**********########
########**#####**#**#####**###**######**########
########**#####**#**#####**###**######**########
########**#####**#**#####**###**********########
########**#####**#**#####**###**################
########**#####**#**#####**###**################
########**######***######**###**################
########**###############**###**################
########**###############**###**################
################################################
########Copyright © Maresal Programming#########
################################################

from PyQt5 import QtWidgets,QtCore,QtGui
import os,sys,socket
from datetime import datetime
from ChatApp import Ui_MainWindow
from ping import ping_ip



class chatMain(QtWidgets.QMainWindow):
    def __init__(self):
        super(chatMain,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.label()
        self.ui.pushButton_2.clicked.connect(self.chatStart)
        self.ui.pushButton.clicked.connect(self.sendMessage)
        self.ui.pushButton_3.clicked.connect(self.exit)
        self.zamanlayıcı = QtCore.QTimer(self)
        self.zamanlayıcı.timeout.connect(self.startThread)

    def serverStatus(self):
        try:
            ip = "127.0.0.1"
            port = 1881
            ping_ip(ip+":"+str(port))
            print("Bağlantı Sağlıklı")
            baglanti = f"{ip}:{port} | Bağlantı Durumu : Açık"
            return baglanti
        except Exception as err :
            baglanti = f"{ip}:{port} | Bağlantı Durumu : Kapalı"
            return baglanti

    def serverStatusOK(self):
        global model
        model = QtGui.QStandardItemModel()
        self.ui.listView.setModel(model)
        item = QtGui.QStandardItem(self.serverStatus())
        model.appendRow(item)
        
    def chatConnect(self,ip,port):
        global s
        SERVER_HOST = ip
        SERVER_PORT = port
        separator_token = "<<MPRM>>" 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        text = f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}..."
        try:
            s.connect((SERVER_HOST, SERVER_PORT))
            self.ui.textBrowser.setText(text)
            self.startThread()
            self.zamanlayıcı.start(1000)
            self.ui.stackedWidget.setCurrentIndex(0)
        except Exception :
                QtWidgets.QMessageBox.warning(self,"Hata","Bağlanmak istediğiniz Server şuan Aktif değil.")

    def chatStart(self):
        username = self.ui.lineEdit_2.text()
        if username == "":
            QtWidgets.QMessageBox.warning(self,"Hata","Username Girilmedi")
        else :
            self.ui.listView.setCurrentIndex(model.index(0,0))
            data = self.ui.listView.currentIndex().data()
            ipPort = data.split("|")[0].split(":")
            print(data.split("|")[1].split(":")[1])
            if data.split("|")[1].split(":")[1] == " Açık":
                self.chatConnect(ipPort[0],int(ipPort[1]))
            else :
                QtWidgets.QMessageBox.warning(self,"Hata","Bağlanmak istediğiniz Server şuan Aktif değil.")

    def sendMessage(self):
        username = self.ui.lineEdit_2.text()
        msg = self.ui.lineEdit.text()
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        to_send = f"[{date_now}] {username} : {msg}"
        s.send(to_send.encode("utf-8"))
        self.ui.lineEdit.clear()

    def startThread(self):
        self.worker = ThreadWorker()
        self.worker.start()
        self.worker.finished.connect(self.finish)
        self.worker.message.connect(self.chat)

    
    def chat(self,val):
        message = self.ui.textBrowser.toPlainText()
        message+= "\n"+val+"\n"
        self.ui.textBrowser.setText(message)

    def finish(self):
        print("finishid")

    def exit(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.zamanlayıcı.stop()
        s.close()


    def label(self):
        self.ui.label.setStyleSheet(
            """
            #label{
            image:url("mplog.png");}
            """
        )

class ThreadWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)

    def run(self):
        try:
            for i in range(3):
                self.message.emit(s.recv(1024).decode("utf-8"))
        except:
            pass



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = chatMain()
    main.show()
    main.serverStatusOK()
    app.setStyle("Fusion")
    app.exit(app.exec_())


