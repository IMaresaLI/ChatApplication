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
from DatabaseManager import *



class chatMain(QtWidgets.QMainWindow):
    global Kaynak,Hedef
    Kaynak = 'qazwsxedcrfvtgbyhnujmıköolçpşğiü1234567890'
    Hedef = 'fvtgby123xedcrhnu78şğ56jmq9çpköwsliaz0oüı4'
    def __init__(self):
        super(chatMain,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.label()
        self.serverStatusOK()
        self.ui.pushButton_2.clicked.connect(self.chatStart)
        self.ui.pushButton.clicked.connect(self.sendMessage)
        self.ui.pushButton_3.clicked.connect(self.exit)

        self.zamanlayıcı = QtCore.QTimer(self)
        self.zamanlayıcı.timeout.connect(self.startThread)

        self.zamanlayıcı2 = QtCore.QTimer(self)
        self.zamanlayıcı2.timeout.connect(self.serverStatusOK)
        self.zamanlayıcı2.start(5000)

    def serverStatusOK(self):
        global model
        model = QtGui.QStandardItemModel()
        self.ui.listView.setModel(model)
        confs = sqliteData("ServerInformation").getData()
        for conf in confs:
            if conf[4] == False :
                text= f"Server Name = {conf[1]}\nHost Ip = {conf[2]} Host Port = {conf[3]}\nServer Status = Kapalı"
            else :
                text= f"Server Name = {conf[1]}\nHost Ip = {conf[2]} Host Port = {conf[3]}\nServer Status = Açık"
            item = QtGui.QStandardItem(text)
            model.appendRow(item)

        
    def chatConnect(self,ip,port):
        global s,separator_token,serverStat
        serverStat = []
        SERVER_HOST = ip
        SERVER_PORT = port
        separator_token = "<SEP>" 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        text = f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}..."
        try:
            s.connect((SERVER_HOST, SERVER_PORT))
            self.ui.textBrowser.setText(text+"\n")
            self.startThread()
            self.zamanlayıcı.start(1000)
            self.ui.stackedWidget.setCurrentIndex(0)
            encryp = str.maketrans(Kaynak,Hedef)
            username = self.ui.lineEdit_2.text()
            to_send = (username + " Servera Giriş Yaptı.").translate(encryp)
            s.send(to_send.encode("utf-8"))
            serverStat.append(port)
        except Exception :
                QtWidgets.QMessageBox.warning(self,"Hata","Bağlanmak istediğiniz Server şuan Aktif değil.")

    def chatStart(self):
        username = self.ui.lineEdit_2.text()
        if username == "":
            QtWidgets.QMessageBox.warning(self,"Hata","Username Girilmedi")
        else :
            try :
                data = self.ui.listView.currentIndex().data()
                ip = data.split("=")[2].split(" ")[1]
                port = data.split("=")[3].split("\n")[0]
                print(ip,port)
                if data.split("=")[4] == " Açık":
                    self.chatConnect(ip,int(port))
                else :
                    QtWidgets.QMessageBox.warning(self,"Hata","Bağlanmak istediğiniz Server şuan Aktif değil.")
            except :
                self.ui.listView.setCurrentIndex(model.index(0,0))
                data = self.ui.listView.currentIndex().data()
                ip = data.split("=")[2].split(" ")[1]
                port = data.split("=")[3].split("\n")[0]
                print(ip,port)
                if data.split("=")[4] == " Açık":
                    self.chatConnect(ip,int(port))
                else :
                    QtWidgets.QMessageBox.warning(self,"Hata","Bağlanmak istediğiniz Server şuan Aktif değil.")

    def sendMessage(self):
        confs = sqliteData("ServerInformation").getData2(serverStat[0])
        if confs[4] == True:
            username = self.ui.lineEdit_2.text()
            msg = self.ui.lineEdit.text()
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            encryp = str.maketrans(Kaynak,Hedef)
            to_send = f"[{date_now}] {username} {separator_token} {msg}".translate(encryp)
            s.send(to_send.encode("utf-8"))
            self.ui.lineEdit.clear()
        else :
            QtWidgets.QMessageBox.warning(self,"Hata","Server şuan Aktif değil.")
            self.ui.lineEdit.clear()
            self.zamanlayıcı.stop()
            s.close()
            self.worker.finished.connect(self.finish)
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.textBrowser.clear()


    def startThread(self):
        self.worker = ThreadWorker()
        self.worker.start()
        self.worker.message.connect(self.chat)

    def chat(self,val):
        message = self.ui.textBrowser.toPlainText()
        message+= "\n"+val+"\n"
        self.ui.textBrowser.setText(message)

    def finish(self):
        print("finished")

    def exit(self):
        encryp = str.maketrans(Kaynak,Hedef)
        username = self.ui.lineEdit_2.text()
        to_send = (username + " Çıkış Yaptı.").translate(encryp)
        s.send(to_send.encode("utf-8"))
        self.ui.stackedWidget.setCurrentIndex(1)
        self.zamanlayıcı.stop()
        s.close()
        self.worker.finished.connect(self.finish)

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
                msg = s.recv(1024).decode("utf-8")
                encryp = str.maketrans(Hedef,Kaynak)
                self.message.emit(msg.translate(encryp))
        except:
            pass






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = chatMain()
    main.show()
    app.setStyle("Fusion")
    app.exit(app.exec_())
    

