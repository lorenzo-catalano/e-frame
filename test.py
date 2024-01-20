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
    (black,red) = flib.getImages()
    black.save('black.png')
    red.save('red.png')
    flib.merge(black,red)