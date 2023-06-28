from __future__ import print_function
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'eframe/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5b_V2
import flib

epd = epd7in5b_V2.EPD()

def main():
    (black,red) = flib.generate()
    epd.init()
    epd.Clear()
    epd.display(epd.getbuffer(black), epd.getbuffer(red))

if __name__ == '__main__':
    main()
