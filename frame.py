from __future__ import print_function
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'eframe/lib')
print(libdir)
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V2
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

epd = epd7in5b_V2.EPD()



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def getEventStartEnd(x):
    return (x.get('start').get('date',x.get('start').get('dateTime')),(x.get('start').get('date',x.get('end').get('endTime'))))
def getEventDay(x):
    return(x.get('start').get('date',x.get('start').get('dateTime')))[0:10]
def getEventMonth(x):
    return(x.get('start').get('date',x.get('start').get('dateTime')))[6:8]


def getEventStartEndFormatted(x):
    try:
        startend = getEventStartEnd(x)
        start = startend[0][11:15]
        end = startend[1][11:15]
        return start + ' - ' + end
    except:
        return 'error'


def drawPreview(draw,position):
    posx=position[0]
    posy=position[1]
    # Set the dimensions of the image
    image_width = 200
    image_height = 200

    draw.rounded_rectangle((posx,posy, posx+image_width,posy+image_height), radius=5, fill=None, outline=None, width=1)


    # Set the font properties
    font_size = 20
    font = ImageFont.truetype('Quattrocento-Regular.ttf', font_size)

    # Get the current month
    current_month = datetime.date.today().strftime('%B')

    # Create a calendar string
    calendar_string = f"{current_month}\nL M M G V S D\n"

    # Get the number of days in the current month
    num_days = calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1]

    # Get the day of the week for the first day of the month
    first_day_weekday = 6#datetime.date.today().replace(day=1).weekday()

    # Calculate the cell dimensions
    cell_width = image_width // 7
    cell_height = cell_width

    # Calculate the starting position for drawing the calendar
    start_x = posx
    start_y = posy + font_size + 5

    # Draw the calendar string

    # Draw the calendar cells
    days = ["L","M","M","G","V","S","D"]
    today = 1#datetime.date.today().day
    for day in range(0, 7):
        x = start_x + cell_width * day
        _, _, bw, bh = draw.textbbox((0,0), days[day],font=font)
        draw.text((x+cell_width/2-bw/2, posy+cell_height/2-bh/2), days[day], fill='black', font=font)
    for day in range(1, num_days + 1):
        # Calculate the cell position
        x = start_x + cell_width * ((first_day_weekday + day - 1) % 7)
        y = start_y + cell_height * ((first_day_weekday + day - 1) // 7)
        # Draw the day number
        _, _, bw, bh = draw.textbbox((0,0), str(day),font=font)
        if(today==day):
            draw.arc((x, y,x+cell_width, y+cell_height), 0, 360, fill=None, width=1)
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
        dayfont = ImageFont.truetype("Quattrocento-Bold.ttf", size=titlesize)
        mex = today.strftime("%d %B, %Y")
        _, _, w, h = blackDraw.textbbox((0, 0), mex , font=dayfont)
        blackDraw.text(((width-w)/2, 10), mex, font=dayfont, fill=0)

        upMargin=10*2 + h
        margin=2
        c = 0
        days=['L','M','M','G','V','S','D']
        months=['Gennaio','Febbraio','Marzo','Aprile','Maggio','Giugno','Luglio','Agosto','Settembre','Ottobre','Novembre','Dicembre']
        headfont = ImageFont.truetype("Quattrocento-Bold.ttf", size=20)
        
        #for x in range(7):
        #    _, _, bw, bh = blackDraw.textbbox((0, 0), days[x],font=headfont)
        #    blackDraw.text((margin + x*boxw + boxw/2 - bw/2, upMargin + 10), days[x], fill=0,font=headfont)
        #
        #upMargin = upMargin+30
#
        #cal = calendar.Calendar(firstweekday=0)
        #dom = cal.itermonthdays2(2023, 6)
        #for x in range(7):
        #    for y in range(6):
        #        c = c+1
        #        if(c>31):
        #            c=1
        #        shape=[(margin + x*boxw, upMargin + y*boxh), (margin + x*boxw+boxw, upMargin + y*boxh+boxh)]
        #        blackDraw.rectangle(shape, outline ="black")
        #        _, _, bw, bh = blackDraw.textbbox((0, 0), str(c))
        #        blackDraw.text((margin + x*boxw + boxw/2 - bw/2, upMargin + y*boxh + 10), str(dom[c]), fill=0)

        for c in calendars['items']: #filter(lambda cal: cal['id'].startswith("family"), calendars['items']):
            events_result = service.events().list(calendarId=c['id'],timeMin=now,maxResults=10, singleEvents=True,orderBy='startTime').execute()
            allevents = allevents + events_result.get('items', [])

        allevents = sorted(allevents,key = lambda x : (x.get('start').get('date',x.get('start').get('dateTime')))[0:10])[0:10]
        
        hmargin = 10
        margin = 5
        margin10 = 10
        boxw = width-hmargin
        boxh = 40
        day = ""
        month = ""
        currenty=titlesize + 20
        leftmarginbox = 60

        circleMargin=10
        circleDiameter=40
        

        for event in allevents:
            mo = getEventMonth(event)
            ed = getEventDay(event)
            if(mo!=month):
                month = mo
                blackDraw.line((hmargin,currenty,width-hmargin,currenty), fill=None, width=1, joint=None)
                m = months[int(ed[5:7])-1]
                _, _, bw, bh = blackDraw.textbbox((0,0), m)
                blackDraw.rectangle((width/2 - margin - bw/2,currenty, width/2 - bw/2 + bw + margin ,currenty+bh), fill=1)
                blackDraw.text((width/2 - bw/2,currenty - bh/2), m , fill=0)

                currenty = currenty+margin10
            if(day!=ed):
                day=ed
                blackDraw.arc((circleMargin,currenty,circleMargin+circleDiameter,currenty+circleDiameter), 0, 360, fill=None, width=1)
                _, _, bw, bh = blackDraw.textbbox((0,0), ed[8:10])
                blackDraw.text((circleMargin + circleDiameter/2- bw/2,currenty + circleDiameter/2 - bh/2), ed[8:10] , fill=0)
            #start = event['start'].get('dateTime', event['start'].get('date'))
            blackDraw.rounded_rectangle((leftmarginbox,currenty, boxw,currenty +boxh), radius=5, fill=None, outline=None, width=1)

            blackDraw.text((leftmarginbox + hmargin, currenty + margin), event.get('summary')+getEventStartEndFormatted(event), fill=0)
            
            currenty = currenty+margin+boxh


        drawPreview(blackDraw,(hmargin,currenty+20))

        black.save("black.bmp")
        
        epd.init()
        epd.Clear()
        epd.display(epd.getbuffer(black), epd.getbuffer(black))

        

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
