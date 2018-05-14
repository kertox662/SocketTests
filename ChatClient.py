import socket
from tkinter import *
import threading
from queue import Queue
from time import sleep
import atexit
print("Start")
users = ["Users:"]
dUsers = []

queueMsg = []
displayMsg = []

#checkPort = Queue()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connected = False

def exitFunc():
    s.close()

atexit.register(exitFunc)

def getName(Event):
    askName.destroy()
    #print("Got name")
    global screenName
    screenName = screenName.get()

def askForName():
    global askName, screenName
    askName = Tk()
    screenName = StringVar()
    cvAN = Canvas(askName, width = 200, height = 200)
    cvAN.pack()
    cvAN.create_text(100, 20, text = "Enter your name:")
    entryAN = Entry(cvAN, textvariable = screenName, width = 12)
    entryAN.place(x = 50, y = 100)
    askName.bind("<Return>", getName)
    askName.mainloop()

while not connected:
    try:
        hostName = "misha.melnyk.family"
        hostIP = socket.gethostbyname(hostName)
        s.connect((hostIP,4545))
        connected = True
    except socket.error:
        print("Failed Connection")

print("Here")
askForName()
nameSend = "|User|{}".format(screenName)
s.send(nameSend.encode())

w = 800
h = 800

root = Tk()
cv = Canvas(root, width = w, height = h, bg = "lightblue")
cv.pack()
cv.create_rectangle(100,150, w - 100, h, fill = 'white')
cv.update()

maxMessages = 30

def displayTexts():
    while True:
        for i in dUsers:
            cv.delete(i)
        for i in users:
            dUsers.append(cv.create_text(w-50, 150+users.index(i) * 30, text = i))
        
        cv.update()
        
        for i in displayMsg:
            cv.delete(i)
        
        if len(queueMsg) >= maxMessages:
            msgToDisplay = queueMsg[maxMessages*-1:]
        else:
            msgToDisplay = queueMsg.copy()
        msgToDisplay.reverse()
        for i in range(len(msgToDisplay)):
            displayMsg.append(cv.create_text(w/2, h-40 - i * 20, text = msgToDisplay[i]))
        
        cv.update()
        sleep(0.03)

def recvLoop():
    while True:
        data = s.recv(4096)
        if not data:
            break
        msg = data.decode('utf-8')
        print(msg)
        if msg.startswith("|Users|"):
            global users
            userList = msg.split("|Users|")
            print(userList[1])
            newUList = eval(userList[1])
            if len(newUList) > len(users):
                queueMsg.append("{} has connected".format(newUList[-1]))
            users = newUList
            print(users)
            print("Got new user list")
            
        else:
            queueMsg.append(msg)

def sendMsg(Event):
    global sendmsg
    msg = sendmsg.get()
    msgSent = "{}:{}".format(screenName, msg)
    s.send(msgSent.encode())
    sendEntry.delete(0, "end")

def sendLoop():
    global sendmsg, sendEntry
    sendmsg = StringVar()
    sendEntry = Entry(cv, textvariable = sendmsg, width = 50)
    sendEntry.place(x=100, y=h-20)
    cv.update()
    root.bind("<Return>", sendMsg)

userThread = threading.Thread(target = displayTexts)
userThread.daemon = True
userThread.start()

recvThread = threading.Thread(target=recvLoop)
recvThread.daemon = True
recvThread.start()

sendLoop()
root.mainloop()