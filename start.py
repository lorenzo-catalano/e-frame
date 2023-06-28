from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image, ImageDraw, ImageFont
from datetime import date
import calendar
import itertools

today = date.today()
width=480
height=800

boxw=68
boxh=68

days=['L','M','M','G','V','S','D']
daysFull=['Lunedì','Martedì','Mercoledì','Giovedì','Venerdì','Sabato','Domenica']


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def getEventStartEnd(x):
    return (x.get('start').get('date',x.get('start').get('dateTime')),x.get('end').get('date',x.get('end').get('dateTime')))
def getEventDay(x):
    return(x.get('start').get('date',x.get('start').get('dateTime')))[0:10]
def getEventMonth(x):
    return(x.get('start').get('date',x.get('start').get('dateTime')))[6:8]


def getEventStartEndFormatted(x):
    try:
        startend = getEventStartEnd(x)
        start = startend[0][11:16]
        end = startend[1][11:16]
        if(start == ""):
            return "(promemoria)"
        else:
            return start + ' - ' + end
    except:
        return 'error'


def drawPreview(draw,margin,maxheight):
    image_width = 200
    image_height = 200
    posx=margin
    posy=maxheight - image_height - margin
    # Set the dimensions of the image
    

    draw.rounded_rectangle((posx,posy, posx+image_width,posy+image_height), radius=5, fill=None, outline=None, width=1)


    # Set the font properties
    font_size = 20
    font = ImageFont.truetype('./fonts/Roboto-Regular.ttf', font_size)
    fontBold = ImageFont.truetype('./fonts/Roboto-Bold.ttf', font_size)

    # Get the number of days in the current month
    num_days = calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1]

    # Get the day of the week for the first day of the month
    first_day_weekday = datetime.date.today().replace(day=1).weekday()

    # Calculate the cell dimensions
    cell_width = image_width // 7
    cell_height = cell_width

    # Calculate the starting position for drawing the calendar
    start_x = posx
    start_y = posy + font_size + 5

    # Draw the calendar string

    # Draw the calendar cells
    today = datetime.date.today().day
    for day in range(0, 7):
        x = start_x + cell_width * day
        _, _, bw, bh = draw.textbbox((0,0), days[day],font=fontBold)
        draw.text((x+cell_width/2-bw/2, posy+cell_height/2-bh/2), days[day], fill='black', font=fontBold)
    for day in range(1, num_days + 1):
        # Calculate the cell position
        x = start_x + cell_width * ((first_day_weekday + day - 1) % 7)
        y = start_y + cell_height * ((first_day_weekday + day - 1) // 7)
        # Draw the day number
        _, _, bw, bh = draw.textbbox((0,0), str(day),font=font)
        if(today==day):
            draw.ellipse((x, y,x+cell_width, y+cell_height), fill=0, width=1)
            draw.text((x+cell_width/2-bw/2, y+cell_height/2-bh/2), str(day), fill='white', font=fontBold)
        else:
            draw.text((x+cell_width/2-bw/2, y+cell_height/2-bh/2), str(day), fill='black', font=font)


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting calendars')
        calendars = service.calendarList().list().execute()
        allevents = []

        black = Image.new("1", (width,height), color=255)
        blackDraw = ImageDraw.Draw(black)
        titlesize=40
        dayfont = ImageFont.truetype("./fonts/Roboto-Regular.ttf", size=titlesize)
        mex = daysFull[today.weekday()] + " "+ today.strftime("%d-%m-%Y")
        _, _, w, h = blackDraw.textbbox((0, 0), mex , font=dayfont)
        blackDraw.text(((width-w)/2, 10), mex, font=dayfont, fill=0)

        upMargin=10*2 + h
        margin=2
        c = 0
        
        months=['Gennaio','Febbraio','Marzo','Aprile','Maggio','Giugno','Luglio','Agosto','Settembre','Ottobre','Novembre','Dicembre']
        headfont = ImageFont.truetype("./fonts/Roboto-Regular.ttf", size=20)
        
        for c in filter(lambda cal: cal['id'].startswith("family"), calendars['items']):
            events_result = service.events().list(calendarId=c['id'],timeMin=now,maxResults=10, singleEvents=True,orderBy='startTime').execute()
            allevents = allevents + events_result.get('items', [])

        allevents = sorted(allevents,key = lambda x : (x.get('start').get('date',x.get('start').get('dateTime')))[0:10])[0:10]
        
        hmargin = 10
        margin = 5
        margin10 = 10
        boxw = width-hmargin
        
        day = ""
        month = ""
        currenty=titlesize + 20
        

        

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
                blackDraw.line((hmargin,currenty,width-hmargin,currenty), fill=None, width=1, joint=None)
                m = months[int(ed[5:7])-1]
                _, _, bw, bh = blackDraw.textbbox((0,0), m,font = font)
                blackDraw.rectangle((width/2 - margin - bw/2,currenty, width/2 - bw/2 + bw + margin ,currenty+bh), fill=1)
                blackDraw.text((width/2 - bw/2,currenty - bh/2), m , fill=0,font = font)

                currenty = currenty+margin10
            if(day!=ed):
                day=ed
                #on red
                blackDraw.ellipse((circleMargin,currenty,circleMargin+circleDiameter,currenty+circleDiameter), fill=None, width=1)
                _, _, bw, bh = blackDraw.textbbox((0,0), ed[8:10],font = font)
                blackDraw.text((circleMargin + circleDiameter/2- bw/2,currenty + circleDiameter/2 - bh/2), ed[8:10] , fill=0,font = font)
            blackDraw.rounded_rectangle((leftmarginbox,currenty, boxw,currenty +boxh), radius=5, fill=None, outline=None, width=1)
            blackDraw.text((leftmarginbox + hmargin, currenty + margin), event.get('summary')+" "+getEventStartEndFormatted(event), fill=0,font = font)
            
            currenty = currenty+margin+boxh


        drawPreview(blackDraw,margin,height)

        black.save("black.bmp")
        

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
