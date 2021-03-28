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

from threading import ThreadError
import threading
from PyQt5 import QtWidgets,QtCore,QtGui
import os,sys,socket,re
from datetime import datetime
from DatabaseManager import sqliteData
from ServerChatApp import Ui_MainWindow
from threading import Thread


class chatServer(QtWidgets.QMainWindow):
    def __init__(self):
        super(chatServer,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ChatServer()
        self.ui.pushButton_3.clicked.connect(self.CreateServer)
        self.ui.pushButton_2.clicked.connect(self.CreateSocket)
        self.ui.pushButton.clicked.connect(self.serverClosed)
        self.ui.pushButton_4.clicked.connect(self.DeleteServer)



    def CreateServer(self):
        ip = self.ui.lineEdit.text()
        port = self.ui.lineEdit_2.text()
        if ip == "" and port == "":
            QtWidgets.QMessageBox.warning(self,"Hata","Server Bilgileri Girilmemiş.")
        else :
            name,ok = QtWidgets.QInputDialog.getText(self,"Server Created","Server Name :")
            if name and ok :
                try:
                    sqliteData("ServerInformation").Add(name,ip,int(port),False)
                    self.ChatServer()
                    self.ui.lineEdit.clear()
                    self.ui.lineEdit_2.clear()               
                except Exception as Err:
                    QtWidgets.QMessageBox.warning(self,"Hata","Oluşturmaya Çalıştığınız Port no daha Önce Kullanıldı.")


    def ChatServer(self):
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


    def ipPort(self):
        try:
            data = self.ui.listView.currentIndex().data() 
            x = data.split("\n")
            hostip = x[1].split()
            ip = hostip[3]
            port = hostip[7]
            return ip,port
        except Exception as err:
            QtWidgets.QMessageBox.warning(self,"Hata","Server Seçmediniz.")
            

    def CreateSocket(self):
        global client_sockets,separator_token,s
        try:
            SERVER_HOST = self.ipPort()[0]
            SERVER_PORT = int(self.ipPort()[1])
            separator_token = "<SEP>" 
            client_sockets = []
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((SERVER_HOST, SERVER_PORT))
            s.listen(15)
            text = f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}\n"
            self.ui.textBrowser.setText(text)
            sqliteData("ServerInformation").UpdateStatus(True,SERVER_PORT)
            self.ChatServer()
            self.TheadStart()
        except :
            pass


    def DeleteServer(self):
        sqliteData("ServerInformation").Delete(self.ipPort()[1])
        self.ChatServer()


    def TheadStart(self):
        self.worker = ThreadWorker()
        self.worker.start()
        self.worker.login.connect(self.LoginText)
        self.worker.message.connect(self.MessageText)


    def LoginText(self,login):
        text = self.ui.textBrowser.toPlainText()
        text+=login+"\n"
        self.ui.textBrowser.setText(text)

    def MessageText(self,message):
        text = self.ui.textBrowser.toPlainText()
        text+=message+"\n"
        self.ui.textBrowser.setText(text)



    def serverClosed(self):
        try :
            sqliteData("ServerInformation").UpdateStatus(False,int(self.ipPort()[1]))
            s.close()
            self.worker.finished.connect(self.finish)
            self.ChatServer()
            self.ui.textBrowser.clear()
            client_sockets.clear()
        except Exception as err :
            self.ChatServer()

        
    def finish(self):
        print("finished")


class ThreadWorker(QtCore.QThread):
    login = QtCore.pyqtSignal(str)
    message = QtCore.pyqtSignal(str)
    def listen_for_client(self,cs):
        while True:
            try:
                msg = cs.recv(1024).decode("UTF-8")
                self.message.emit(msg)
                if not msg :
                    pass
            except Exception as Err :
                print("Bağlantı Kapatıldı")
                if client_sockets == []:
                    pass
                else :
                    client_sockets.remove(cs)
                    break
            except ConnectionResetError:
                print("Bağlantı Kapatıldı.")
                if client_sockets == []:
                    pass
                else :
                    client_sockets.remove(cs)
            else:
                msg = msg.replace(separator_token, ": ")
            for client_socket in client_sockets:
                client_socket.send(msg.encode())
    
    def run(self):
        while True:
            try:
                client_socket, client_address = s.accept()
                log = f"[+] {client_address} connected."
                print(log)
                self.login.emit(log)
                client_sockets.append(client_socket)
                t = Thread(target=self.listen_for_client, args=(client_socket,))
                t.daemon = True
                t.start()
            except Exception as err:
                print("Run Error : "+ str(err))
                break




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = chatServer()
    main.show()
    app.setStyle("Fusion")
    app.exit(app.exec_())