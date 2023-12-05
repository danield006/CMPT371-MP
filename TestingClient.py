from socket import *

# Init test client and connection
serverName = 'localhost'
serverPort = 13000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

request = """GET /test.html HTTP/1.1
Host: localhost:13000
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0
Accept: text/html
Connection: keep-alive
Content-Length: 0
If-Modified-Since: Sun, 10 Jan 2024 02:01:00 GMT"""

clientSocket.send(request.encode('utf-8'))


response = clientSocket.recv(1024)
print ('From Server:', response.decode('utf-8'))


#input("...")
clientSocket.close()
