from socket import *
import threading
from datetime import *


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

# Status codes
def requestIsGood(request, socket):
     if(not request.startswith('GET /')):
          # Respond with a 400 Bad Request status code
          responseData = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n<html><body><h1>400 Bad Request</h1><p>Your request is invalid.</p></body></html>'
          
          socket.sendall(responseData.encode('utf-8'))
          socket.close()
          return False
     
     return True

def requestNotForbidden(path, socket):      
     if(path.startswith('/forbidden')):
          # Respond with a 403 Forbidden status code
          responseData = 'HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\n\r\n<html><body><h1>403 Forbidden</h1><p>Access to the requested resource is forbidden.</p></body></html>'
          
          socket.sendall(responseData.encode('utf-8'))
          socket.close()
          return False
     
     return True

def contentLengthDefined(request, socket):
     if 'Content-Length' not in request:
          # Respond with a 411 Length Required status code
          responseData = 'HTTP/1.1 411 Length Required\r\nContent-Type: text/html\r\n\r\n<html><body><h1>411 Length Required</h1><p>Content-Length header is required.</p>'
          
          socket.sendall(responseData.encode('utf-8'))
          socket.close()
          return False
     
     return True

def notFound(socket):
     # Respond with a 404 Not Found status code
     responseData = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1><p>Page not found.</p>'
     
     socket.sendall(responseData.encode('utf-8'))
     socket.close()
     
     
def modifiedSince(request, socket, lastModified):
     if 'If-Modified-Since' not in request:
          return True
     else:
          lines = request.split("\n")
          for line in lines:
               if('If-Modified-Since' in line):
                    date = line.split(': ')[1] #parse request to get date field
                    requestDate = getDate(date)
                    if(requestDate < lastModified): #if date modified since is older than last date the html was modified (hardcoded date), send current html
                         return True
                    else:
                         # Respond with a 304 Not Modified status code
                         responseData = 'HTTP/1.1 304 Not Modified\r\nContent-Type: text/html\r\n\r\n<h1>304 Not Modified</h1>' #else, send 304 to simulate client loading site from cache
     
                         socket.sendall(responseData.encode('utf-8'))
                         socket.close()
                         return False
     return True

def handleClient(connection):
     # Read from socket
     requestData = connection.recv(1024).decode('utf-8')
     print('Request recieved: ')
     print(requestData)
     if(requestIsGood(requestData, connection)):
          try:
               pathName = requestData.split(' ')[1]
               if pathName == '/':
                    pathName = '/index.html' # If no path, redirect to index page
               print(pathName)
               # Read the content of the requested file
               with open('.' + pathName, 'r') as file:
                    content = file.read()
               if(requestNotForbidden(pathName, connection) and contentLengthDefined(requestData, connection) and modifiedSince(requestData, connection, fileLastModified)):
                    

                    # Respond with a 200 OK status code
                    responseData = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{content}'
                    
                    connection.sendall(responseData.encode('utf-8'))
                    connection.close()
                    
          except FileNotFoundError:
               notFound(connection)
          except PermissionError:
               notFound(connection)


# Init server
serverPort = 12000

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('localhost',serverPort))


fileLastModified = datetime(2023, 11, 30)

serverSocket.listen(1)
print (f'Web server listening on port {serverPort}...')


# Listening loop
while True:
     connectionSocket, addr = serverSocket.accept()
     #create a thread that calls handleClient
     clientHandler = threading.Thread(target=handleClient, args=(connectionSocket,))
     clientHandler.start()