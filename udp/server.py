import socket
import time
import logging

# Laver User Datagram Protocol (UDP) socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Knytter socket til port
server_address = ('localhost', 13000)
print('Server: starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Start variable
count = 1
connection = False
timeout = False
timeoutStop = False
countdown = 0

# Logger til "server.log"
logging.basicConfig(level=logging.INFO, filename="server.log")

# Internet Protocol (IP) addresse
hostname = socket.gethostname()
serverIPAddresse = socket.gethostbyname(hostname)

BUFFER_SIZE = 4096
while True:

    if not connection:
        try:

            # Venter på 'syn'
            sock.setblocking(True)
            print("Server (ThreeWayHandshake): Waiting to recive Syn")
            synData, address = sock.recvfrom(BUFFER_SIZE)
            clientIp = address[0]

            logging.info(time.asctime() + " | Client with Ip: " + str(address[0]) + " | Port: " + str(
                address[1]) + " is trying to connect to server")

            print(f'Server (ThreeWayHandshake): Recevied {synData}')

            ip = synData[9:21]

            if synData[0:8] == b"C: com-0" and synData[9:21] == ip:
                # print("det her er syn data", synData)
                # print("Det her er ip", ip)

                logging.info(
                    time.asctime() + " | received Syn from" + "| Client : " + str(address[0]) + " | Port: " + str(
                        address[1]))

                print('Server (ThreeWayHandshake): Sending Syn-Ack to client')
                logging.info(time.asctime() + " | Server Sending Syn-Ack to " + str(address[0]))
                sent = sock.sendto(b"S: com-0 accept " + serverIPAddresse.encode('ASCII'), address)

                # Waiting for client accept
                ackData, address = sock.recvfrom(BUFFER_SIZE)
                print(f'Server (ThreeWayHandshake): Recevied {ackData}')

                if ackData[0:15] == b"C: com-0 accept" and ip == ackData[16:28]:
                    #print("det her er ackData", ackData)

                    logging.info(
                        time.asctime() + " | received Ack from " + "| Client : " + str(address[0]) + " | Port: " + str(
                            address[1]))

                    print("Server (ThreeWayHandshake): TCP socket connection is ESTABLISHED.")
                    connection = True
                    count = 1
                    print("--------------------------------------")
                    
                    logging.info(time.asctime() + " | Server and client Connected")
                    
            else:
                print("(ThreeWayHandshake) fejlede. Forbindelsen lukkes")
                connection = False
        except BlockingIOError:
            print("BlockingIOError in (ThreeWayHandshake)")

    if connection:
        if countdown < 10:
            time.sleep(0.1)
            countdown += 0.1

        if countdown > 9 and not timeoutStop:
            print("Timeout = True")
            timeout = True
            timeoutStop = True

        try:
            # Sørger for at data server ikke stopper når den skal modtage data

            # Timeout
            if timeout:
                try:
                    print("\nServer: Timeout started, sending timeout to client")
                    timeoutStop = False
                    sent = sock.sendto(b'con-res 0xFE', address)
                    sock.setblocking(True)
                    print("Server: Wating to recive timeout acknowledge form client")
                    data, address = sock.recvfrom(BUFFER_SIZE)
                    logging.info(
                        time.asctime() + " | Disconnected from  " + "| Client : " + str(address[0]) + " | Port: " + str(
                            address[1]))
                    if data.decode('ASCII') == 'con-res 0xFF':
                        print("Server: Resetting timeoutstopper.")
                        timeoutStop = False
                        print("Server: Client acknowledge received. \nServer: Connection set to False")
                        connection = False
                        timeout = False
                        countdown = 0
                        print("\n--------------------------------------")
                except BlockingIOError:
                    print("fejl kom")

            sock.setblocking(False)

            data, address = sock.recvfrom(BUFFER_SIZE)

            countdown = 0

            print('Server: received {} bytes from {}'.format(len(data.decode()), address))
            print('Server: Message From Client = ' + data.decode())

            dataAnalyse = data.decode("ASCII")
            substring = dataAnalyse[dataAnalyse.find("-") + len('-'):dataAnalyse.find("=")]
            number = substring

            if dataAnalyse == 'con-h 0x00':
                print('Server: Heartbeat received from client')
                print('Server: resetting countdown')
                print("\n--------------------------------------")
                countdown = 0

            # Internet Protocoller
            dataBreakdown = dataAnalyse.split("=")
            # print("datanalyse", dataBreakdown)

            if data.decode('ASCII').startswith('C: msg-'):
                print("\nServer: Preparing response")
                if int(number) + 1 == count:

                    if dataBreakdown[1] == "Hello":
                        message = b"Hello there"

                        msg = (b"S: res-" + str(count).encode("ASCII") + b"=" + message)
                        print(f'Server: Sending {msg}')

                        sent = sock.sendto(msg, address)

                    elif dataBreakdown[1] == "test":
                        message = b"testing 1..2..3 testing"

                        msg = (b"S: res-" + str(count).encode("ASCII") + b"=" + message)
                        print(f'Server: Sending {msg}')

                        sent = sock.sendto(msg, address)
                        print("Test done")
                    else:
                        message = dataBreakdown[1].encode("ASCII")
                        msg = (b"S: res-" + str(count).encode("ASCII") + b"=" + message)

                        print(f'Server: Sending {msg}')
                        sent = sock.sendto(msg, address)

                    count += 2
                    print("Server: Count updated to: " + str(count))
                    print("\n--------------------------------------")
                    # print('ClientCount : ' + str(number) + ' ' + 'ServerCount ' + str(count))
                else:
                    print("Server: Number didnt match")
                    print('ClientCount : ' + str(number) + ' ' + 'ServerCount ' + str(count))
        except:
            continue
