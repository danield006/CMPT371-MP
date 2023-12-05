from socket import *
import threading
from datetime import *

proxyPort = 13000
serverPort = 12000

# Dictionary to store cached responses
cache = {}

def getDate(date): 
     #parse request date and create datetime object for comparison
     months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
     
     fields = date.split(' ')
     time = fields[4].split(':')
     
     month = 1
     for i in months:
          if(i == fields[2]): #month text to numeric month val
               break
          month = month + 1
               
     requestDate = datetime(int(fields[3]), month, int(fields[1]), int(time[0]), int(time[1]), int(time[2]))
     
     return requestDate

def handleClient(clientConnection):
    # Recieve request from client
    requestData = clientConnection.recv(1024)
    print('Request received from client:')
    print(requestData.decode('utf-8'))

    # Parse "If-Modified-Since" header from the client request
    if_modified_since = None
    lines = requestData.decode('utf-8').split("\n")
    for line in lines:
        if 'If-Modified-Since' in line:
            date = line.split(': ')[1]
            if_modified_since = getDate(date)
            break

    # Check if the request is in the cache and can be used
    if requestData in cache and if_modified_since:
        date = cache.get(requestData).get('last_modified_date', None)
        last_modified_date = getDate(date)

        if last_modified_date and last_modified_date >= if_modified_since:
            print('Cache hit! Sending cached response to client.')
            responseData = 'HTTP/1.1 304 Not Modified\r\nContent-Type: text/html\r\n\r\n<h1>304 Not Modified</h1>' #else, send 304 to simulate client loading site from cache
     
            clientConnection.sendall(responseData.encode('utf-8'))
            clientConnection.close()
            
            #clientConnection.sendall(cache[requestData]['response'])
            #print(cache[requestData]['response'].decode('utf-8'))
            #clientConnection.close()
            return

    # If not in cache or "If-Modified-Since" check failed, fetch from the web server
    webServerSocket = socket(AF_INET, SOCK_STREAM)
    webServerSocket.connect(('localhost', serverPort))

    webServerSocket.sendall(requestData)

    responseData = webServerSocket.recv(1024)
    print('Response received from web server:')
    print(responseData.decode('utf-8'))

    # Store the response in the cache
    cache[requestData] = {'response': responseData, 'last_modified_date': if_modified_since}

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