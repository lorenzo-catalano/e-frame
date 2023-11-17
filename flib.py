from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image, ImageDraw, ImageFont
from datetime import date,timezone,timedelta
import calendar
import itertools
import io
import requests
import time

today = date.today()
width=480
height=800
boxw=68
boxh=68

days=['L','M','M','G','V','S','D']
daysFull=['Lunedì','Martedì','Mercoledì','Giovedì','Venerdì','Sabato','Domenica']
months=['Gennaio','Febbraio','Marzo','Aprile','Maggio','Giugno','Luglio','Agosto','Settembre','Ottobre','Novembre','Dicembre']



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def getEventStartEnd(x):
    start=x.get('start')
    end=x.get('end')
    try:
        s=datetime.datetime.strptime(start.get('date',start.get('dateTime')),'%Y-%m-%dT%H:%M:%S%z').astimezone()
        e=datetime.datetime.strptime(end.get('date',end.get('dateTime')),'%Y-%m-%dT%H:%M:%S%z').astimezone()
    except ValueError:
        s=datetime.datetime.strptime(start.get('date',start.get('dateTime')),'%Y-%m-%d').astimezone()
        e=datetime.datetime.strptime(end.get('date',end.get('dateTime')),'%Y-%m-%d').astimezone()
    
    return (s,e)

def getEventDay(x):
    return(x.get('start').get('date',x.get('start').get('dateTime')))[0:10]
def getEventDayFull(x):
    return(x.get('start').get('date',x.get('start').get('dateTime')))[0:10]
def getEventMonth(x):
    return(x.get('start').get('date',x.get('start').get('dateTime')))[6:8]


def getEventStartEndFormatted(x):
    try:
        startend = getEventStartEnd(x)
        start = startend[0].strftime("%H:%M")
        end = startend[1].strftime("%H:%M")
        if(start == "00:00" and end == "00:00"):
            return ""
        else:
            return start + ' - ' + end
    except Exception as e: 
        return 'error'


def preview(blackDraw,redDraw,currenty,margin,allevents):

    titlesize=40
    titleFont = ImageFont.truetype("./fonts/Gidole-Regular.ttf", size=titlesize)
    mex = months[today.month -1] +" "+ str(today.year)
    _, _, tw, th = redDraw.textbbox((0, 0), mex , font=titleFont)
    redDraw.text(((width-tw)/2, 10), mex, font=titleFont, fill=0)

    font_size = 20
    image_height = font_size*10
    image_width = image_height
    
    # Set the dimensions of the image

     # Calculate the cell dimensions
    cell_width = 60
    cell_height = 40
    image_width = cell_width*7
    image_height = (height / 2) - margin

    posx=(width-image_width) / 2
    posy=margin*2+th+5


    # Set the font properties
    
    font = ImageFont.truetype('./fonts/Roboto-Regular.ttf', font_size)
    fontBold = ImageFont.truetype('./fonts/Roboto-Bold.ttf', font_size)

    num_days = calendar.monthrange(today.year, today.month)[1]
    first_day_weekday = today.replace(day=1).weekday()
    start_x = posx
    start_y = posy + font_size + 5
    
    for day in range(0, 7):
        x = start_x + cell_width * day
        _, _, bw, bh = blackDraw.textbbox((0,0), days[day],font=fontBold)
        blackDraw.text((x+cell_width/2-bw/2, posy), days[day], fill='black', font=fontBold)

    startDay = datetime.date.today().replace(day=1) - datetime.timedelta(days=first_day_weekday)
    currentmonth = datetime.date.today().month
    for count in range(1, 43):
        day=startDay.day
        eventsInDay = len(list(filter(lambda e: getEventDay(e)== startDay.strftime("%Y-%m-%d") ,allevents)))
        # Calculate the cell position
        x = start_x + cell_width * ((count-1) % 7)
        y = start_y + cell_height * ((count-1) // 7)
        # Draw the day number
        _, _, bw, bh = blackDraw.textbbox((0,0), str(day),font=font)
        
        if(today==startDay):
            redDraw.rounded_rectangle((x+1, y+1,x+cell_width-1, y+cell_height-1),radius=10,width=1, fill=0)
            redDraw.text((x+cell_width/2-bw/2, y+cell_height/2-bh/2-1), str(day), fill='white', font=fontBold)
            for n in range(0,eventsInDay):
                redDraw.ellipse((5*n+x+5+(n)*5,y+cell_height-10,5*n+ x+5+(n+1)*5, y+cell_height-5),fill='white')
        else:
            blackDraw.text((x+cell_width/2-bw/2, y+cell_height/2-bh/2-1), str(day), fill='black', font=fontBold)
            for n in range(0,eventsInDay):
                redDraw.ellipse((5*n+x+5+(n)*5,y+cell_height-10,5*n+ x+5+(n+1)*5, y+cell_height-5),fill=1)
        if(currentmonth != startDay.month):
            for i in range(0,cell_width//3):
                blackDraw.line((x+1, y+i*3,x+cell_width-1, y+i*3), fill='white', width=1)
                blackDraw.line((x+i*3, y,x+i*3, y+cell_height), fill='white', width=1)

        
        blackDraw.rounded_rectangle((x,y,x+cell_width,y+cell_height),radius=10,width=1)
        startDay=startDay + datetime.timedelta(days=1)

def getEvents():
    creds = None
    if os.path.exists('../token.json'):
        creds = Credentials.from_authorized_user_file('../token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('calendar', 'v3', credentials=creds)
        now = (datetime.datetime.utcnow()).isoformat() + 'Z'
        print('Getting calendars')
        allevents = []
        calendars = service.calendarList().list().execute()
        for c in filter(lambda cal: cal['id'].startswith("family"), calendars['items']):
        #for c in calendars['items']:
            events_result = service.events().list(calendarId=c['id'],timeMin=now,maxResults=10, singleEvents=True,orderBy='startTime').execute()
            allevents = allevents + events_result.get('items', [])

        allevents = sorted(allevents,key = lambda x : (x.get('start').get('date',x.get('start').get('dateTime')))[0:10])[0:15]
        return allevents
    except HttpError as error:
        print('An error occurred: %s' % error)
        return []

def generate():
    
    black = Image.new("1", (width,height), color=255)
    red = Image.new("1", (width,height), color=255)
    blackDraw = ImageDraw.Draw(black)
    redDraw = ImageDraw.Draw(red)
    
    margin=2
    c = 0
    headfont = ImageFont.truetype("./fonts/Roboto-Regular.ttf", size=20)
    
    allevents = getEvents()
    
    preview(blackDraw,redDraw,0,margin,allevents)

    hmargin = 10
    margin = 5
    margin10 = 10
    boxw = width-hmargin
    
    day = ""
    month = ""
    currenty=350

    baseFontSize=20
    font = ImageFont.truetype("./fonts/Roboto-Medium.ttf", size=baseFontSize)
    
    boxh = baseFontSize+margin*2

    circleMargin=10
    circleDiameter=baseFontSize+margin*2
    leftmarginbox = circleDiameter+margin*3

    for event in allevents:
        mo = getEventMonth(event)
        ed = getEventDay(event)
        if(mo!=month):
            currenty = currenty+margin
            month = mo
            m = months[int(ed[5:7])-1]
            _, _, bw, bh = blackDraw.textbbox((0,0), m,font = font)
            blackDraw.text((margin,currenty), m , fill=0,font = font)
            redDraw.line((margin*2+bw,currenty+bh/2,width-hmargin,currenty+bh/2), fill=None, width=1, joint=None)

            currenty = currenty+baseFontSize+margin
        if(day!=ed):
            day=ed
            #on red
            _, _, bw, bh = redDraw.textbbox((0,0), ed[8:10],font = font)
            if(day==today.strftime("%Y-%m-%d")):
                redDraw.ellipse((circleMargin,currenty,circleMargin+circleDiameter,currenty+circleDiameter), fill=0, width=1)
                redDraw.text((circleMargin + circleDiameter/2- bw/2,currenty + circleDiameter/2 - bh/2 -1), ed[8:10] , fill='white',font = font)
            else:
                redDraw.ellipse((circleMargin,currenty,circleMargin+circleDiameter,currenty+circleDiameter), fill=None, width=1)
                blackDraw.text((circleMargin + circleDiameter/2- bw/2,currenty + circleDiameter/2 - bh/2 -1), ed[8:10] , fill=0,font = font)
        #blackDraw.rounded_rectangle((leftmarginbox,currenty, boxw,currenty +boxh), radius=5, fill=None, outline=None, width=1)
        blackDraw.text((leftmarginbox + hmargin, currenty + margin), event.get('summary')+" "+getEventStartEndFormatted(event), fill=0,font = font)
        
        currenty = currenty+margin+boxh

    return (black,red)

def sendImagePixels(image,color):
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
            if(paramsCount==75):
                print('calling',len(params))
                r = requests.post("http://192.168.1.204/",data=params)
                print('done',r)
                paramsCount=0
                params=""
    if params:
        print('calling',color)
        r = requests.post("http://192.168.1.204/",data=params)
        print('done',r)


def send(black,red):
    red.save("red.png")
    black.save("black.png")

    red = red.rotate(-90,expand=1)
    black = black.rotate(-90,expand=1)

    #requests.post("http://192.168.1.204/",data="AAAAAAAAAAAAAAAAAAAAAAAAA")
    #time.sleep(5)

    #sendImagePixels(black,'b')
    #sendImagePixels(red,'r')
    #time.sleep(5)
    #requests.post("http://192.168.1.204/",data="d")
def merge(black,red):
    
    merged = black.convert(mode='RGBA')
    print(merged)
    datas = red.getdata()
    
    x=-1
    y=0
    paramsCount=0
    params=""
    
    for item in datas:
        x=x+1
        if(x==480):
            x=0
            y=y+1
        if item != 255 :
            merged.putpixel((x,y),(255,0,0,255))

    merged.save('merged.png')

def getMergedImages():
    (black,red) = generate()
    merge(black,red)