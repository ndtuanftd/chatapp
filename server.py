import socket
import json


FORMAT = 'utf-8'


class Server:
    PORT = 8000
    address = socket.gethostname()
    clientsData = ""
    ports = []

    def sendClientList(self):
        # global jsonDatas
        # global ports
        # global PORT
        # global address
        #data =  '{ "name":"Rey", "type":"chat", "message":"alo alo alo"}'
        data = '{ "name":"Rey", "type":"central", "peerList":"' + \
            self.clientsData+'"}'
        print("server: data> "+data)
        for port in self.ports:
            clientSocket = socket.socket()
            clientSocket.connect((self.address, int(port)))
            clientSocket.send(data.encode(FORMAT))
            print("Send success")

    def start(self):
        serverSocket = socket.socket()
        serverSocket.bind((self.address, self.PORT))
        serverSocket.listen()
        print('Server is listening on ...')
        while (True):
            # sendListUser()
            self.sendClientList()
            conn, addr = serverSocket.accept()
            if (conn):
                print("Have an user connnected")
                print(addr)
                try:
                    data = conn.recv(1024).decode(FORMAT)
                    print("server: data> " + data)
                    jsonData = json.loads(data)
                    self.ports.append(jsonData["port"])
                    rawData = jsonData["name"] + ":" + jsonData["port"]
                    self.clientsData += rawData
                    self.clientsData += ";"
                except:
                    continue


if __name__ == "__main__":
    server = Server()
    server.start()
