from socket import *
import threading

proxyPort = 13000
serverPort = 12000

def handleClient(clientConnection):
    # Recieve request from client
    requestData = clientConnection.recv(1024)
    print('Request received from client:')
    print(requestData.decode('utf-8'))
    
    webServerSocket = socket(AF_INET, SOCK_STREAM)
    webServerSocket.connect(('localhost', serverPort))

    webServerSocket.sendall(requestData)
    
    
    responseData = webServerSocket.recv(1024)
    print('Response received from web server:')
    print(responseData.decode('utf-8'))

    clientConnection.sendall(responseData)
    clientConnection.close()



proxySocket = socket(AF_INET,SOCK_STREAM)
proxySocket.bind(('localhost',proxyPort))

proxySocket.listen(1)
print(f'Proxy server listening on port {proxyPort}...')

while True:
    connectionSocket, addr = proxySocket.accept()
    print(f'Successfully connected to client address {addr}')
    
    #create a thread that calls handleClient()
    clientHandler = threading.Thread(target=handleClient, args=(connectionSocket,))
    clientHandler.start()