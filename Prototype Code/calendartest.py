import tkinter
from tkinter import ttk
import tkcalendar
import datetime

#Setup window and style
window = tkinter.Tk()
today = datetime.datetime.today()
style = ttk.Style(window)
style.theme_use('alt')
# Create calendar widget
cal = tkcalendar.Calendar(window, selectmode="day",
                          year=today.year,
                          month=today.month,
                          day=today.day)
#COLOURS
cal.config(background="white", foreground="red", selectbackground = "orange")
cal.pack(fill = 'both', expand = 1)



#create a class for Classes  - confusion xD
class Class:
    def __init__(self, time, name, classID):
        self.time = time
        self.name = name
        self.ID = classID
        
    def checkFull():
        return True
        #final program will include this method to check if the class is full



#function binded to month changes to load classes for that month
def updateMonth(event):
    date = cal.get_date()
    date = datetime.datetime.strptime(date, '%m/%d/%y')
    month = int(date.strftime('%m'))
    #retrieve this month classes, load into classes array
cal.bind("CalendarMonthChanged", updateMonth)



#classes array stores all classes for each day in separate subarray, with Class instance for each
classes = [[Class('08:00', 'Give it a go', 1000)],
           [],
           [],
           [Class('09:00', 'Learn to climb', 2000), Class('17:00', 'Give it a go', 1001)],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           []]



#Add subroutine binded to date change event to change classes in listbox (updatein stringvar) - show name and time
def updateOptions(event):
    global selectedDayClasses
    
    date = cal.get_date()
    date = datetime.datetime.strptime(date, '%m/%d/%y')
    day = int(date.strftime('%d'))

    choices = []

    #format nicely fot litbox
    options = classes[day-1]
    for option in options:
        choices.append(option.time + ' - ' + option.name)
    
    #update variable
    selectedDayClasses.set(choices)
            
cal.bind('<<CalendarSelected>>', updateOptions)



#create listbox to show class options for that day
selectedDayClasses = tkinter.StringVar(value = ["Class1", "Class2"])
classesBox = tkinter.Listbox(window, listvariable = selectedDayClasses, selectmode = 'browse')
classesBox.pack()


#create button binded to function to retrive class ID from respectuve Class instance, retunr it
def selectClassFunc():
    date = cal.get_date()
    date = datetime.datetime.strptime(date, '%m/%d/%y')
    day = int(date.strftime('%d'))

    classChoice = classesBox.curselection()

    classID = classes[day-1][classChoice[0]].ID

    print('classID is', classID)
    return classID
    
selectClass = tkinter.Button(window, text = "Select", command = selectClassFunc)
selectClass.pack()

updateMonth('<>')
updateOptions('<>')

window.mainloop()
