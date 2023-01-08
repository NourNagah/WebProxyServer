from socket import *
import sys
# Check that a server IP was passed as an argument
if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')

portNum = 5078
# Create a server socket, bind it to a port and start listening
tcp_Ser_Sock = socket(AF_INET, SOCK_STREAM)
tcp_Ser_Sock.bind(('', portNum))
tcp_Ser_Sock.listen(1)

try:
    while 1:
        # Start receiving data from the client
        print('\nReady to serve...')
        tcp_Cli_Sock, addr = tcp_Ser_Sock.accept()
        print('Received a connection from:', addr)
        message = tcp_Cli_Sock.recv(2048)
        print(message)

        if message == b'':
            print("No connection")
            sys.exit("0")
            break

        if message != b'':
            # Extract the filename, hostname, and URL from the given message
            filename = message.split()[1].decode("utf-8").rpartition("/")[2]
            hostn = message.split()[4].decode("utf-8")
            URL = message.split()[1].decode("utf-8")

        print("Filename: " + filename)
        print("Hostname: " + hostn)
        print("URL is: " + URL)

        # cache the file
        fileExist = "false"
        fileToUse = './cache' + filename
        print(fileToUse)

        # check if file is blocked or not in the list of blocked urls of the server
        getout = 1
        with open('blockedURL.txt') as f:
            for line in f:
                if URL in line:
                    print("BLOCKED")
                    getout = 0
                    break
                else:
                    getout = 1
        if getout == 0:
            break

        try:
            # Check whether the file exist in the cache
            f = open(fileToUse[1:], "rb")
            output_Data = f.readlines()
            fileExist = "true"

            # ProxyServer finds a cache hit and generates a response message
            tcp_Cli_Sock.send(b"HTTP/1.0 200 OK\r\n")
            tcp_Cli_Sock.send(b"Content-Type:text/html\r\n")
            for i in range(0, len(output_Data)):
                tcp_Cli_Sock.send(output_Data[i])
            f.close()

        # Error handling for file not found in cache
        except IOError:
            try:
                if fileExist == "false":
                    # Create a socket on the proxyserver
                    c = socket(AF_INET, SOCK_STREAM)
                    print(hostn)
                    c.connect((hostn, 80))
                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                    f_obj_write = c.makefile('w', None)
                    f_obj_write.write("GET " + message.split()[1].decode("utf-8") + " HTTP/1.0\n\n")
                    f_obj_write.close()
                    # read response
                    File_Obj = c.makefile('rb', None)
                    buffer = File_Obj.readlines()
                    # Create a new file in the cache for the requested file.
                    # Also send the response in the buffer to client socket and the corresponding file in the cache
                    File = open('./cache/' + filename, "wb+")
                    # Fill in start.
                    for line in buffer:
                        File.write(line)
                        tcp_Cli_Sock.send(line)
                    File.close()
                    c.close()

            except:
                print("Illegal request")
    else:
        # HTTP response message for file not found
        tcp_Cli_Sock.send("HTTP/1.0 404 sendError\r\n")
        tcp_Cli_Sock.send("Content-Type:text/html\r\n")
        # Close the client and the server sockets
        tcp_Cli_Sock.close()
        print("socket closed")
        sys.exit("System done, file not found")

except:
    print('connection blocked')
    tcp_Cli_Sock.close()
    sys.exit("System done, no message")
