import socket
import threading
import time
import os

# Laver User Datagram Protocol (UDP) socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


server_address = ('localhost', 13000)

# Klient Internet protokol (IP)
hostname = socket.gethostname()
IPaddresse = socket.gethostbyname(hostname)

# Start variable
connection = False
Heartbeat = False
maxpackage = 0
count = 0
BUFFER_SIZE = 4096


def heartBeat(self):
    timer = 0

    while True:
        time.sleep(0.1)
        timer += 0.1
        if timer > 3:
            print("\nSending con-h 0x00 to server")
            sock.sendto(b'con-h 0x00', server_address)
            timer = 0


def sendMsg():
    # Send data
    global count
    time.sleep(1 / int(maxpackage))

    print("Client: Preparing to send data")
    message = input("Client: Write your message here -> ")

    msg = ("C: msg-" + str(count) + "=" + message)
    sock.sendto(msg.encode(), server_address)
    print(f'Client: Sending {msg}')


def reciveMsg(self):
    # Receive Response

    global count
    print('\nClient: Wating for response')
    sock.setblocking(True)
    data, server = sock.recvfrom(BUFFER_SIZE)

    if data.decode('ASCII') == 'con-res 0xFE':
        print("\nClient: received con-res 0xFE")
        print("Client: Sending con-res 0xFF")
        sent = sock.sendto(b'con-res 0xFF', server_address)
        print("Client: Server closed connection")

        os._exit(0)

    dataAnalyse = data.decode('ASCII')

    substring = dataAnalyse[dataAnalyse.find("-") + len('-'):dataAnalyse.find("=")]
    number = substring

    print(f'\nClient: Recevied {data.decode()}')

    if int(number) - count == 1:
        count += 2
        print("Client: Count updated to: " + str(count))
        print("\n--------------------------------------")
    else:
        print("Count didnt match .. closing con")
        os._exit(0)


file = open("options.conf", "r")

if file.mode == 'r':
    contents = file.readlines()

heartBeatChecker = contents[0]
maxPackageChecker = contents[1]

if heartBeatChecker.startswith("KeepALive"):

    if heartBeatChecker.split(":")[1].rstrip("\n") == " True":
        # print("Heartbeat set to True")
        Heartbeat = True

    if heartBeatChecker.split(":")[1].rstrip("\n") == " False":
        # print("Heartbeat set to False")
        Heartbeat = False

if maxPackageChecker.startswith("MaxPackage"):
    maxpackage = maxPackageChecker.split(":")[1]

print("Hearbeat is set to: " + str(Heartbeat))
print("MaxPackage is set to: " + str(maxpackage))
print("")

try:
    while not connection:

        print('Client (ThreeWayHandshake): Trying to establish connection')

        # sender SYN
        sock.sendto(b"C: com-0 " + IPaddresse.encode('ASCII'), server_address)

        synData, server = sock.recvfrom(BUFFER_SIZE)
        print(f'Client (ThreeWayHandshake): Recevied {synData}')
        ip = synData[16:28]
        # print("det her er syn data", synData)
        # print("Det her er server", server)
        if synData[0:15] == b"S: com-0 accept" and ip == synData[16:28]:
            print("Client (ThreeWayHandshake): Sending Ack")
            sock.sendto(b"C: com-0 accept " + IPaddresse.encode('ASCII'), server_address)
            print("Client (ThreeWayHandshake): Connection established")
            connection = True
            break
        else:
            connection = False
        print("Client (ThreeWayHandshake): received data didnt match.. closing connection")
        break

    print("--------------------------------------")

    if Heartbeat:
        heartbeatThread = threading.Thread(target=heartBeat, args=(0,))
        heartbeatThread.start()
    while connection:
        reciveMsgThread = threading.Thread(target=reciveMsg, args=(1,))
        reciveMsgThread.start()

        sendMsgThread = threading.Thread(target=sendMsg(), args=(2,))
        sendMsgThread.start()

finally:
    print('Client: closing socket')
    sock.close()
