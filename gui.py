""" Include Modules """
from Tkinter import *           # GUI, StringVar, Entry
import time                     # Delay
import string                   # find, strip, et.c
import urllib2                  # Used by BeautifulSoup
from bs4 import BeautifulSoup   # Used to parse html 

# Returns num in binary representation as a string of 1's and 0'
def dec2bin(num):
    mid = []
    while True:
        if num == 0: break
        num, rem = divmod(num, 2)
        mid.append(rem)

    return '0' + ''.join([str(x) for x in mid[::-1]])

# Button definitions align to IR Remote buttons to convserve firware computation
IR_DEF_0 = dec2bin(0x57)
IR_DEF_1 = dec2bin(0x49)
IR_DEF_2 = dec2bin(0x51)
IR_DEF_3 = dec2bin(0x41)
IR_DEF_4 = dec2bin(0x4D)
IR_DEF_5 = dec2bin(0x55)
IR_DEF_6 = dec2bin(0x45)
IR_DEF_7 = dec2bin(0x4B)
IR_DEF_8 = dec2bin(0x53)
IR_DEF_9 = dec2bin(0x43)

IR_DEF_MENU = dec2bin(0x48)
IR_DEF_MUTE = dec2bin(0x4F)
IR_DEF_BUY = dec2bin(0x50)
IR_DEF_AB = dec2bin(0x56)
IR_DEF_ENTER = dec2bin(0x46)
PADDING = '11111111'

# Map for Digit-> equivalent IR Remote numpad number
IR_NUM_ARRAY = [IR_DEF_0, IR_DEF_1, IR_DEF_2, IR_DEF_3, IR_DEF_4, IR_DEF_5,
    IR_DEF_6, IR_DEF_7, IR_DEF_8, IR_DEF_9]


RECT_WIDTH = 640
RECT_HEIGHT = 480

DELAY = 0.08

"""
Define weather
"""
sunny = IR_DEF_1
cloudy = IR_DEF_2
rainy = IR_DEF_3

sunny_options = ['mostly fine', 'mostly sunny', 'sunny']
cloudy_options = ['cloudy', 'partly cloudy']
rainy_options = ['shower', 'light drizzle', 'early drizzle', 'storm']

"""
Define globals
"""

def print_bin_arr(array):

    for i in range(len(array)):
        
        sys.stdout.write( array[i] )

        if i % 8 == 7:
            sys.stdout.write( ',' )

    print


def binary_num(num):
    
    array = []

    # Assume Year Setting
    if num > 31:
        array +=  PADDING + IR_NUM_ARRAY[num/1000] + PADDING + IR_NUM_ARRAY[(num/100)%10]

    array += PADDING + IR_NUM_ARRAY[(num/10)%10] + PADDING + IR_NUM_ARRAY[num%10]

    return array


def valid_mins(mins):
    return (mins >= 0 and mins < 60)

def valid_hours(hours):
    return (hours >= 0 and hours < 24)

def valid_day(day):
    return (day > 0 and day <= 31)

def valid_month(month):
    return (month > 0 and month <= 12)

def valid_year(year):
    return (year >= 0 and year <= 9999)

def valid_date(day,month,year):
    
    if not valid_day(day) or not valid_month(month) or not valid_year(year):
        return False
   
    max_day_dict = { 1 : 31, 2 : (28,29)[year % 4 == 0] , 3:31, 4:30, 5:31, 6:30,
            7:31, 8:31, 9:30, 10:31, 11:30, 12:31 } 
    
    return day <= max_day_dict[month]


class Controller:

    def __init__(self,master):

        #The fllowing two variables are used for input of alarm setting
        self.timeMinutes = StringVar(value='00')
        self.timeHours = StringVar(value='00')
        self.alarmMinutes = StringVar(value='00')
        self.alarmHours = StringVar(value='00')
        self.dateDay = StringVar(value='01')
        self.dateMonth = StringVar(value='01')
        self.dateYear = StringVar(value='0000')

        #init the GUI
        self.initGUI(master)

    def initGUI(self, master):
        #Time setting frame
        timeFrame = Frame(master)
        lbl_timeFrame = Label(timeFrame, text = "Time setting")
        lbl_hour = Label(timeFrame, text = "Hour: ")
        entry_hour = Entry(timeFrame, textvariable = self.timeHours)
        lbl_minutes = Label(timeFrame, text = "Minutes: ")
        entry_minutes = Entry(timeFrame, textvariable = self.timeMinutes)
        btn_time = Button(timeFrame, text = "Click", command = self.timeClick)
        lbl_timeFrame.pack()
        lbl_hour.pack(side = LEFT)
        entry_hour.pack(side = LEFT)
        lbl_minutes.pack(side = LEFT)
        entry_minutes.pack(side = LEFT)
        btn_time.pack(side = LEFT)
        timeFrame.pack()

        #Date setting frame
        dateFrame = Frame(master)
        lbl_dateFrame = Label(dateFrame, text = "Date setting")
        lbl_day = Label(dateFrame, text = "Day: ")
        entry_day = Entry(dateFrame, textvariable = self.dateDay)
        lbl_month = Label(dateFrame, text = "Month: ")
        entry_month = Entry(dateFrame, textvariable = self.dateMonth)
        lbl_year = Label(dateFrame, text = "Year:")
        entry_year = Entry(dateFrame, textvariable = self.dateYear)
        btn_date = Button(dateFrame, text = "Click", command = self.dateClick)
        lbl_dateFrame.pack()
        lbl_day.pack(side = LEFT)
        entry_day.pack(side = LEFT)
        lbl_month.pack(side = LEFT)
        entry_month.pack(side = LEFT)
        lbl_year.pack(side = LEFT)
        entry_year.pack(side = LEFT)
        btn_date.pack(side = LEFT)
        dateFrame.pack()

        #Alarm setting frame
        alarmFrame = Frame(master)
        lbl_alarmFrame = Label(alarmFrame, text = "Alarm setting")
        lbl_alarmHours = Label(alarmFrame, text = "Hour :")
        entry_alarmHours = Entry(alarmFrame, textvariable = self.alarmHours)
        lbl_alarmMinutes = Label(alarmFrame, text = "Minutes: ")
        entry_alarmMinutes = Entry(alarmFrame, textvariable = self.alarmMinutes)
        btn_alarm = Button(alarmFrame, text = "Click", 
                command = self.alarmClick)
        lbl_alarmFrame.pack()
        lbl_alarmHours.pack(side = LEFT)
        entry_alarmHours.pack(side = LEFT)
        lbl_alarmMinutes.pack(side = LEFT)
        entry_alarmMinutes.pack(side = LEFT)
        btn_alarm.pack(side = LEFT)
        alarmFrame.pack()

        #Weather retrieving frame
        weatherFrame = Frame(master)
        lbl_weatherFrame = Label(weatherFrame, text = 'Weather')
        btn_weather = Button(weatherFrame, text = 'Get', command = self.weatherGet)
        lbl_weatherFrame.pack()
        btn_weather.pack()
        weatherFrame.pack()
        
        #Flashing box
        self.window = Canvas(master, width = RECT_WIDTH, height = RECT_HEIGHT)
        self.window.pack()
        self.rect = self.window.create_rectangle(0, 0, RECT_WIDTH, RECT_HEIGHT, fill = "white")


    def flicker(self,string):
         
        print_bin_arr(string)
        for i in range(len(string)):
            if(string[i] == '0'):
                self.window.itemconfig(self.rect, fill = "black")
            else:
                self.window.itemconfig(self.rect, fill = "white")
            time.sleep(DELAY)
            self.window.update()

    """
    Use IR_DEF_MUTE to indicate alarm setting
    The alarm button click event.
    get the current minutes and hours in the entry
    flash the box
    
    Important: there is not check on the input type.
    You may implement this by checking the input is number or not 
    """
    def alarmClick(self):

        #Get user input
        hours = int(self.alarmHours.get().strip())
        mins = int(self.alarmMinutes.get().strip())

        if valid_hours(hours) and valid_mins(mins):

            bit_sequence = list(IR_DEF_MUTE)
            bit_sequence += binary_num(hours)
            bit_sequence += binary_num(mins)
            bit_sequence += PADDING + IR_DEF_ENTER + '1'

            self.flicker(bit_sequence)

    """
    Use IR_DEF_MENU to indicate the time setting
    """
    def timeClick(self):

        #Get user input
        hours = int(self.timeHours.get().strip())
        mins = int(self.timeMinutes.get().strip())

        if valid_hours(hours) and valid_mins(mins):
            
            bit_sequence = list(IR_DEF_MENU)
            bit_sequence += binary_num(hours)
            bit_sequence += binary_num(mins)
            bit_sequence += PADDING + IR_DEF_ENTER + '1'
            
            self.flicker(bit_sequence)

    """
    Use IR_DEF_BUY to indicate the date setting
    """
    def dateClick(self):

        #Get user input
        day = int(self.dateDay.get().strip())
        month = int(self.dateMonth.get().strip())
        year = int(self.dateYear.get().strip())

        if valid_date(day,month,year):

            bit_sequence = list(IR_DEF_BUY)
            bit_sequence += binary_num(day)
            bit_sequence += binary_num(month)
            bit_sequence += binary_num(year)
            bit_sequence += PADDING + IR_DEF_ENTER + '1'

            self.flicker(bit_sequence)

    """
    Gets the weather from the BoM website. Sends byte based on sunny, cloudy
    or rainy. Use IR_DEF_AB to indicate weather setting
    """
    def weatherGet(self):
    
        bit_sequence = list(IR_DEF_AB + PADDING)

        soup = BeautifulSoup(urllib2.urlopen('http://www.bom.gov.au/qld/forecasts/brisbane.shtml').read())

        weather = soup.findAll('dd', attrs = {'class' : 'summary'})

        weather = weather[1].string.lower().replace('\n', ' ')
      
        for options in sunny_options:
            if weather.find(options) >= 0 :
                print 'sunny'
                bit_sequence += sunny
                break
        else:
            for options in rainy_options:
                if weather.find(options) >= 0 :
                    print 'rainy'
                    bit_sequence += rainy
                    break
            else:
                for options in cloudy_options:
                    if weather.find(options) >= 0 :
                        print 'cloudy'
                        bit_sequence += cloudy
                        break
                else:
                    print 'sunny [default]'
                    bit_sequence += sunny

        bit_sequence +=  PADDING + IR_DEF_ENTER + '1'
                
        self.flicker(bit_sequence)
    

def main():
    root = Tk()
    controller = Controller(root)
    root.mainloop()

if __name__ == '__main__':
    main()
