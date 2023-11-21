from __future__ import print_function

import flib

def sendImagePixels(socket,image,color):
    datas = image.getdata()
    x=-1
    y=0
    paramsCount=0
    params=""
    for item in datas:
        x=x+1
        if(x==800):
            x=0
            y=y+1
        if item != 255 :
            paramsCount=paramsCount+1
            params=params+color+":"+str(x)+":"+str(y)+";"
            if(paramsCount==10):
                socket.sendall(str.encode(params))
                paramsCount=0
                params=""
                if y == 2:
                    return
    if params:
        socket.sendall(str.encode(params))

def sendCommand(s,message):
    s.send(str.encode(message))

if __name__ == '__main__':
    (black,red) = flib.getMergedImages()
    black.save('black.png')
    red.save('red.png')

    import socket

    HOST = "0.0.0.0"
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            print('listening')
            conn, addr = s.accept()
            with conn:
                try:
                    (black,red) = flib.getMergedImages()
                    print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    print("clearing")
                    sendCommand(conn,'c;')
                    print("black")
                    sendImagePixels(conn,black.rotate(-90,expand=1),'b')
                    print("red")
                    sendImagePixels(conn,red.rotate(-90,expand=1),'r')
                    print("display")
                    sendCommand(conn,'d;')
                except:
                    conn.close()

