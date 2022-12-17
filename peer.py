from threading import Thread
from threadwithreturn import ThreadWithReturn as RetThread
import tkinter as tk
import socket
import json
import os

FORMAT = 'utf-8'


class Peer:
    peerSockets = []
    address = socket.gethostname()
    allThreads = []
    isLastThread = False
    fileName = ""
    peerPorts = []
    serverPort = 8000
    peerList = ""

    def __init__(self, name, port, text):
        self.port = port
        self.name = name
        self.text = text

    def handlePeer(self, connection, address):
        print("Connection from: " + str(address))
        while True:
            if (self.isLastThread == True):
                break
            try:
                data = connection.recv(1024).decode(FORMAT)
                if (not (data)):
                    return -1

                # get server data
                msg = json.loads(data)
                print("jsonMessage from server:" + str(msg))
                if (msg["type"] == "chat"):
                    self.text.configure(state='normal')
                    self.text.insert(
                        tk.END, "["+msg["name"] + "] : " + msg["message"] + "\n")
                    self.text.configure(state='disable')
                elif (msg["type"] == "file"):
                    self.fileName = msg["filename"]
                    self.text.configure(state='normal')
                    self.text.insert(
                        tk.END, "["+msg["name"] + "] : send you " + self.fileName + " check your folder\n")
                    self.text.configure(state='disable')
                elif (msg["type"] == "central"):
                    self.peerList = msg["peerList"]
            except:
                continue

    def handleReceiveFile(self, connection):
        while True:
            try:
                try:
                    os.mkdir(self.name)
                except:
                    pass
                f = open(self.name+"/"+self.fileName, 'wb')
                print('Start Receiving')
                while (True):
                    print("Receiving...")
                    l = connection.recv(1024)
                    if (not (l)):
                        break
                    f.write(l)
                f.close()
                print("Done Receiving")
                self.fileName = ""
            except:
                continue

    def accept_connection(self, connection, address):
        while True:
            if (self.isLastThread == True):
                break
            input_stream = RetThread(
                target=self.handlePeer, args=(connection, address))
            receiveFileStream = RetThread(
                target=self.handleReceiveFile, args=(connection,))
            receiveFileStream.start()
            input_stream.start()
            self.allThreads.append(input_stream)
            self.allThreads.append(receiveFileStream)
            val2 = receiveFileStream.join()
            val1 = input_stream.join()
            if (val2 == -1):
                return
            if (val1 == -1):
                return

    def registerPort(self, address, port):
        serverSocket = socket.socket()
        serverSocket.bind((address, port))
        serverSocket.listen()
        centralSocket = socket.socket()
        centralSocket.connect((self.address, self.serverPort))
        data = '{"name":"'+self.name+'", "port":"'+str(self.port)+'"}'
        centralSocket.send(data.encode(FORMAT))
        while (True):
            if (self.isLastThread == True):
                break
            conn, addr = serverSocket.accept()  # accept new connection
            acceptThread = Thread(
                target=self.accept_connection, args=(conn, addr))
            self.allThreads.append(acceptThread)
            acceptThread.start()

    def sendMessage(self, message):
        if (message.lower() == "showfriends"):
            print("client-listFriend: " + str(self.peerList))
            peers = self.peerList.split(";")
            self.text.configure(state='normal')
            self.text.insert(
                tk.END, "From Server send the online user list:\n")
            self.text.configure(state='disable')
            for i in range(0, len(peers) - 1):
                print("friend[" + peers[i])
                friend = peers[i].split(":")
                self.text.configure(state='normal')
                self.text.insert(
                    tk.END, "\t"+friend[0] + " : " + friend[1] + "\n")
                self.text.configure(state='disable')
            return
        self.text.configure(state='normal')
        # self.text.insert(tk.END, "["+self.name + "] : " + message + "\n")
        self.text.insert(tk.END, "[" + 'You' + "]: " + message + "\n")
        self.text.configure(state='disable')
        data = '{ "name":"'+self.name + \
            '", "type":"chat", "message":"'+message+'"}'
        for client in self.peerSockets:
            client.send(data.encode(FORMAT))

    def sendFile(self, filePath):
        filename = filePath.split('/')[-1]
        print("File name: ", filename)
        self.text.configure(state='normal')
        self.text.insert(tk.END, "[You] : send an " +
                         filename + " to your friend\n")
        self.text.configure(state='disable')
        data = '{ "name":"'+self.name + \
            '", "type":"file", "filename":"'+filename+'"}'
        for client in self.peerSockets:
            client.send(data.encode(FORMAT))
        for client in self.peerSockets:
            try:
                f = open(filePath, 'rb')
                print("Start sending file")
                while (True):
                    l = f.read(1024)
                    if (not (l)):
                        break
                    client.send(l)
                    print('Sending...')
                f.close()
                print("Done Sending")
                client.shutdown(socket.SHUT_WR)
            except:
                pass
        self.peerSockets = []
        for port in self.peerPorts:
            sender = Thread(target=self.handleSender,
                            args=(self.address, port))
            self.allThreads.append(sender)
            sender.start()

    def handleSender(self, address, port):
        # TODO: check existing socket
        clientSocket = socket.socket()
        print("clientSoket: ", clientSocket)
        clientSocket.connect((address, int(port)))
        self.peerSockets.append(clientSocket)
        print("Connect to " + str(port))

    def startServer(self):
        binder = Thread(target=self.registerPort,
                        args=(self.address, self.port))
        self.allThreads.append(binder)
        binder.start()

    def startClient(self, port):
        sender = Thread(target=self.handleSender,
                        args=(self.address, port))
        self.peerPorts.append(port)
        self.allThreads.append(sender)
        sender.start()

    def endSystem(self):
        print("End system call")
        for socket in self.peerSockets:
            socket.close()
            del socket
        for thread in self.allThreads:
            del thread
        self.isLastThread = True
