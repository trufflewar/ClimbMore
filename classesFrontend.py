import tkinter as tk
import classesBackend as backend
import datetime
from tkinter import messagebox
import tkcalendar
from tkinter import ttk
import accountsBackend as accounts
import re


#standard gui reset as described in accountsFrontend
def resetGuiShell(Master):
    global shell
    for child in Master.winfo_children():
        child.pack_forget()
    try:
        if shell is not None:
            shell.destroy()
    except NameError:
        pass
    except tk.TclError:
        pass
    shell= tk.Frame(master = Master)
    shell.pack(expand=True, fill = 'both')
    

#show class information
def viewClass(Master, accountID, classID):
    resetGuiShell(Master)

    #get user permissions
    permissions = accounts.getPermissions(accountID)
    if permissions ==1:
        customerID = accounts.getCustomer(accountID=accountID)[0][0]

    #get class details
    classDetails = backend.getClass(classID = classID)[0]
    classTypeDetails = backend.getClassType(classTypeID=classDetails[1])[0]
    classDateTime = datetime.datetime.strptime(classDetails[3], '%Y-%m-%d %H:%M:%S')
    #print(type(classDetails[2]))
    if classDetails[2] != None:
        titleText = classDetails[2]
    else:
        titleText = classTypeDetails[1]

    #config gui
    shell.grid_rowconfigure(0, weight = 1)
    shell.grid_rowconfigure(1, weight = 2)
    shell.grid_rowconfigure(2, weight = 2)

    shell.grid_columnconfigure(0, weight = 4)
    shell.grid_columnconfigure(1, weight = 2)

    #addd info widgtes
    title = tk.Label(master = shell, text = titleText, font = ('Arial Bold', 20))
    title.grid(row = 0, column = 0, columnspan=2, sticky='W', pady=5, padx= 10)

    dateSubtitle = tk.Label(master = shell, text = classDateTime.strftime('%d/%m/%Y - %H:%M'), font = ('Arial', 16))
    dateSubtitle.grid(row = 1, column = 0, columnspan=2, sticky = 'NSW')

    description = tk.Label(master = shell, text = classTypeDetails[2], font = ('Arial', 12))
    description.grid(row = 2, column = 0, columnspan=2, sticky = 'NSW', pady = (15,0))

    #check if booked and give option to boook/cancel if customer is logged in
    if permissions ==1:
        shell.grid_rowconfigure(4, weight = 2)
        #customer stuff
        if len(backend.getBookings(classID = classID, customerID = customerID)) == 0:

            booking = tk.Label(master=shell, text = 'You are not booked onto this class', font = ('Arial', 16))
            booking.grid(row = 4, column = 0, sticky = 'NSW', pady = (15,0))

            def bookClassAction():
                if bool(messagebox.askokcancel('Booking Class', 'Are you sure you want to book this class?'))==True:
                    if classTypeDetails[5]==None or len(backend.getBookings(classID=classID)) < classTypeDetails[5]:
                        backend.addBooking(classID=classID, customerID=customerID)
                        viewClass(Master, accountID, classID)
                    else:
                        messagebox.showerror('Booking Error', 'This class is fully booked')
                else:
                    return
            bookBtn = tk.Button(master = shell, text = 'Book Class', command = bookClassAction)
            bookBtn.grid(row = 4, column = 1, sticky = 'NSEW', pady = (15,0))

        else:
            booking = tk.Label(master=shell, text = 'You are booked onto this class', font = ('Arial', 16))
            booking.grid(row = 4, column = 0, sticky = 'NSW', pady = (15,0))

            def cancelClassAction():
                if bool(messagebox.askokcancel('Cancel Booking', 'Are you sure you want to cancel this booking?'))==True:
                    bookingIDs = backend.getBookings(classID = classID, customerID = customerID)
                    for bookingID in bookingIDs:
                        backend.removeBooking(bookingID[0])
                        viewClass(Master, accountID, classID)
                    return
                else:
                    return
            bookBtn = tk.Button(master = shell, text = 'Cancel Class', command = cancelClassAction)
            bookBtn.grid(row = 4, column = 1, sticky = 'NSEW', pady = (15,0))
    
    
    shell.grid_rowconfigure(5, weight = 2)


    #show assigned instructors
    if len(backend.getAssignment(classID = classID))!=0:

        instructorsSubtitle = tk.Label(master = shell, text = 'Instructors', font = ('Arial Bold', 16))
        instructorsSubtitle.grid(row = 5, column = 0, columnspan=2, sticky = 'NSW', pady = (15,3))
    
        nextRow = 6

        for assignment in backend.getAssignment(classID = classID):
            instructor = accounts.getInstructor(instructorID=assignment[2])
            shell.grid_rowconfigure(nextRow, weight = 2)

            instructorLabel = tk.Label(master = shell, text = ' - '+instructor[0][2], font = ('Arial', 14))
            instructorLabel.grid(row = nextRow, column = 0, sticky = 'NSW', padx = (15, 5))
            nextRow+=1

    if permissions ==3:
        pass
        



#shows list of classes to slect from
def viewClasses(Master, accountID, classesList, titleText):
    resetGuiShell(Master)

    #configure grid
    shell.grid_rowconfigure(0, weight =1)
    shell.grid_rowconfigure(1, weight = 6)
    shell.grid_rowconfigure(2, weight = 1)

    shell.grid_columnconfigure(0,weight=1)


    #show title
    titleLabel = tk.Label(master = shell, text = titleText, font = ('Arial Bold', 20))
    titleLabel.grid(row = 0, column = 0, sticky = 'NSEW', padx = 10, pady = 10)

    #get names and dates of each class
    dates = [datetime.datetime.strptime(classSelect[3], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y') for classSelect in classesList]
    names = [backend.getClassType(classTypeID=classSelect[1])[0][1] for classSelect in classesList]

    #nicely fomratted names
    options = []
    for index in range(len(names)):
        options.append(names[index] + ' - ' + dates[index])
    optionsVar = tk.StringVar(value=options)

    #listbox
    classesBox = tk.Listbox(master = shell, listvariable=optionsVar, selectmode='single')
    classesBox.grid(row = 1, column=0, sticky='NSEW', padx = 10)

    selectBtn = tk.Button(master = shell, text = 'View Class', command = lambda: viewClass(Master, accountID, classesList[classesBox.curselection()[0]][0]))
    selectBtn.grid(row = 2, column = 0, sticky = 'NSEW', padx = 5, pady = 5)


#show list of class types to slect from
def classTypesMenu(Master, accountID):
    resetGuiShell(Master)

    #configure grid
    shell.grid_rowconfigure(0, weight =1)
    shell.grid_rowconfigure(1, weight = 6)
    shell.grid_rowconfigure(2, weight = 1)

    shell.grid_columnconfigure(0,weight=1)

    #get classtypes from db
    classTypes = backend.getClassType()
    options = [classType[1] for classType in classTypes]
    optionsVar = tk.StringVar(value= options)

    titleLabel = tk.Label(master = shell, text = 'Class Types', font = ('Arial Bold', 20))
    titleLabel.grid(row = 0, column = 0)

    choicesBox = tk.Listbox(master = shell, listvariable=optionsVar, selectmode='single')
    choicesBox.grid(row = 1, column = 0, sticky = 'NSEW', padx = 5, pady = 5)

    #create slectt option
    def chooseAction():
        classTypesIndex = choicesBox.curselection()[0]
        classTypeID = classTypes[classTypesIndex][0]
        classesList = backend.getClass(classTypeID=classTypeID)
        titleText = classTypes[classTypesIndex][1] + ' Classes'
        viewClasses(Master, accountID, classesList, titleText)
    chooseBtn = tk.Button(master = shell, text = 'Select Class Type', command = chooseAction)
    chooseBtn.grid(row = 2, column = 0, sticky = 'NSEW', padx = 5, pady = 5)


#view classes by caledar
def viewCalendar(Master, accountID):
    resetGuiShell(Master)

    #grid config
    shell.grid_rowconfigure(0, weight = 1)
    shell.grid_rowconfigure(1, weight = 4)
    shell.grid_rowconfigure(1, weight = 4)
    shell.grid_rowconfigure(3, weight = 1)

    shell.grid_columnconfigure(0, weight = 1)

    global selectedDayClasses
    selectedDayClasses = tk.StringVar(value = [])

    #title
    titleLabel = tk.Label(master = shell, text = 'Calendar', font = ('Arial Bold', 20))
    titleLabel.grid(row = 0, column = 0, sticky='NSEW')

    #get today configure calendar
    today = datetime.datetime.today()
    cal = tkcalendar.Calendar(shell, selectmode="day",
                          year=today.year,
                          month=today.month,
                          day=today.day)
    cal.config(background="white", 
               foreground="red", 
               selectbackground = "orange")
    cal.grid(row = 1, column = 0, sticky = 'NSEW', padx = 5, pady = 5)

    #create class for classes
    class Class:
        def __init__(self, time, name, classID):
            self.time = time
            self.name = name
            self.ID = classID

        def checkFull():
            return True
            #TODO future program will include this method to check if the class is full adn then add colour formatting

    classes = []

    #create subroutine to populates classes 2D list with class objects for each class on each day in that month
    def updateMonth(event):
        global classes
        date = cal.get_date()
        date = datetime.datetime.strptime(date, '%m/%d/%y')
        month = date.strftime('%m')

        classes = [[] for x in range(32)]

        allClasses = backend.getClass()
        for classSelect in allClasses:
            if classSelect[3][5:7] == month:

                if classSelect[2] != None:
                    name = classSelect[2]
                else:
                    name = backend.getClassType(classTypeID=classSelect[1])[0][1]
                
                classes[int(classSelect[3][8:10])-1].append(Class(classSelect[3][11:16], name, classSelect[0]))

        #print(classes)

    cal.bind("CalendarMonthChanged", updateMonth)


    #TODO - workaround as curretnyl using 2 gllobal variables whihc is NOTG ideal

    #Add subroutine binded to date change event to change classes in listbox (updatein stringvar) - show name and time
    def updateOptions(event):
        global selectedDayClasses
        global classes

        date = cal.get_date()
        date = datetime.datetime.strptime(date, '%m/%d/%y')
        day = int(date.strftime('%d'))

        choices = []

        #format nicely fot litbox
        options = classes[day]
        for option in options:
            choices.append(option.time + ' - ' + option.name)
    
        #update variable
        selectedDayClasses.set(choices)
            
    cal.bind('<<CalendarSelected>>', updateOptions)



    #create listbox to show class options for that day
    classesBox = tk.Listbox(shell, listvariable = selectedDayClasses, selectmode = 'browse')
    classesBox.grid(row = 2, column = 0, sticky = 'NSEW', padx = 5, pady = 5)

    #select button
    def selectClassFunc():
        date = cal.get_date()
        date = datetime.datetime.strptime(date, '%m/%d/%y')
        day = int(date.strftime('%d'))

        classChoice = classesBox.curselection()

        global classes
        classID = classes[day][classChoice[0]].ID

        #print('classID is', classID)
        viewClass(Master, accountID, classID)
    
    selectClass = tk.Button(shell, text = "Select", command = selectClassFunc)
    selectClass.grid(row = 3, column = 0, sticky = 'NSEW', padx = 5, pady = 5)

    updateMonth('<>')
    updateOptions('<>')




#UNUSED - future development to inlcude this option to search classes by name
def searchClassesMenu(Master, accountID):
    resetGuiShell(Master)

    #TODO Maybe finish maybe not

    shell.grid_columnconfigure(0, weight=3)
    shell.grid_columnconfigure(1, weight =7)

    shell.grid_rowconfigure(0, weight = 3)
    shell.grid_rowconfigure(1, weight = 2)
    shell.grid_rowconfigure(2, weight = 2)
    shell.grid_rowconfigure(3, weight = 2)

    titleLabel = tk.Label(master = shell, text = "Search Classes", font=("Arial Bold", 20))
    titleLabel.grid(row = 0, column = 0, columnspan = 2, sticky = 'W', padx = 10, pady = 5)

    classTypeLabel = tk.Label(master = shell, text = "Firstname", font=("Arial", 16))
    classTypeLabel.grid(row = 1, column = 0, sticky = 'W', padx = 15, pady = 5)
    classTypeSelect = tk.StringVar()
    classTypeSelect.set('Select')
    classTypes = []
    for classType in backend.getClassType():
        classTypes.append(classType[1])
    classTypeDropdown = tk.OptionMenu(shell, classTypeSelect, *classTypes)
    classTypeDropdown.grid(row = 1, column=1, sticky = 'NSEW')



    searchBtn = tk.Button(master = shell, text = 'Search', command = None)
    searchBtn.grid(row= 5, column = 0, columnspan = 2)





#menu for all options to sreach classes by
def findClassesMenu(Master, accountID):
    resetGuiShell(Master)
    
    #grid configure
    shell.grid_rowconfigure(0, weight = 1)
    shell.grid_rowconfigure(1, weight = 3)
    shell.grid_rowconfigure(2, weight = 3)

    shell.grid_columnconfigure(0, weight = 1)
    shell.grid_columnconfigure(1, weight = 1)

    #add widgtes
    findClassesTitle = tk.Label(master = shell, text = 'Find Classes', font = ('Arial Bold', 20))
    findClassesTitle.grid(row = 0, column = 0, columnspan = 2, sticky = 'NSEW', padx = 10, pady = 10)

    viewCalendarBtn = tk.Button(master = shell, text = 'View Calendar', command = lambda: viewCalendar(Master, accountID))
    viewCalendarBtn.grid(row = 1, column = 0, columnspan = 2, sticky = 'NSEW', padx = 5, pady = 5)

    #searchClassesBtn = tk.Button(master = shell, text = 'Search Classes', command = lambda: searchClassesMenu(Master, accountID))
    #searchClassesBtn.grid(row = 1, column = 1, sticky = 'NSEW', padx = 5, pady = 5)
    #MAYBE FINISH THIS...

    viewClassTypesBtn = tk.Button(master = shell, text = 'View Class Types', command = lambda: classTypesMenu(Master, accountID), wraplength = 60)
    viewClassTypesBtn.grid(row = 2, column = 0, sticky = 'NSEW', padx = 5, pady = 5)

    viewAllBtn = tk.Button(master = shell, text = 'View All', command = lambda: viewClasses(Master, accountID, backend.getClass(), 'All Classes'))
    viewAllBtn.grid(row = 2, column = 1, sticky='NSEW', padx = 5, pady = 5)




#menu to add instructors after a class creation
def addInstructors(Master, accountID, classID):
    noInstructors = backend.getClassType(classTypeID=backend.getClass(classID)[0][1])[0][6]
    noInstructors = 0 if noInstructors==None else noInstructors

    #retunr to menu if no instructos required for class
    if noInstructors == 0:
        classesMenu(Master, accountID)
    else:
    
        resetGuiShell(Master)
        
        #configure
        shell.grid_rowconfigure(0, weight =2 )
        titleLabel = tk.Label(master = shell, text = 'Assign Instructor', font = ('Arial Bold', 20))
        titleLabel.grid(row = 0, column = 0, sticky='W', pady=5, padx= 10)

        #gte info
        allInstructors = [instructor[0] for instructor in accounts.getInstructor()]
#        assigned = [assignment[2] for assignment in backend.getAssignment(classID)]
#        unassigned = [instructor for instructor in allInstructors if instructor not in assigned]
        options = [accounts.getInstructor(instructorID=ID) for ID in allInstructors]
        options = [str(instructor[0][0]) + ' - ' + instructor[0][2] for instructor in options]


        instructors = []
        chosen = []


        #create dropdown boxes based on num of instructors required
        for i in range(noInstructors):
            shell.grid_rowconfigure(i+1, weight =2 )
            chosen.append(tk.StringVar(value = options[0]))
            instructors.append(tk.OptionMenu(shell, chosen[i], *options))
            instructors[i].grid(row = i+1, column = 0, sticky = 'NSEW', padx = 10)

        #add instructor button checksfor suplicates instructors and raises messagebox to inform user if so
        shell.grid_rowconfigure(noInstructors+2, weight =2 )
        def addBtnAction(Master, accountID):
           chosenGot = [chosenOne.get() for chosenOne in chosen]
           if len(set(chosenGot))!=len(chosenGot):
               messagebox.showerror('Class Error', 'Cannot have duplicate instructors.')
               return
           for instructor in chosenGot:
               index = chosenGot.index(instructor)
               instructorID = allInstructors[index]
               backend.addAssignment(classID = classID, instructorID=instructorID)
               print(instructorID)
           classesMenu(Master, accountID)
        changeBtn = tk.Button(master = shell, text = "Add Instructor", command= lambda: addBtnAction(Master, accountID))
        changeBtn.grid(row = noInstructors+2, column = 0)


    #classesMenu(Master, accountID)





#Add class instamce
def addClass(Master, accountID):
    resetGuiShell(Master)

    #grid configure
    shell.grid_rowconfigure(0, weight = 2)
    shell.grid_rowconfigure(1, weight = 2)
    shell.grid_rowconfigure(2, weight = 2)
    shell.grid_rowconfigure(3, weight = 2)
    shell.grid_rowconfigure(4, weight = 2)
    shell.grid_rowconfigure(5, weight = 2)

    shell.grid_columnconfigure(0, weight = 1)
    shell.grid_columnconfigure(1, weight = 1)

    #add title, entry boxes, dropdowns etc
    titleLabel = tk.Label(shell, text = 'Schedule Class', font = ('Arial Bold', 20))
    titleLabel.grid(row = 0, column = 0, columnspan=2, sticky = 'NSEW')

    classTypeLabel = tk.Label(master = shell, text = "Class Type", font=("Arial", 16))
    classTypeLabel.grid(row = 1, column = 0, columnspan=2, sticky = 'W', padx = 15, pady = 5)
    classTypeSelect = tk.StringVar()
    classTypeSelect.set('')
    classTypes = []
    for classType in backend.getClassType():
        classTypes.append(classType[1])
    classTypeSelect.set(classTypes[0])
    classTypeDropdown = tk.OptionMenu(shell, classTypeSelect, *classTypes)
    classTypeDropdown.grid(row = 1, column=1, sticky = 'NSEW', padx = 5)

    classTypeAddBtn = tk.Button(master = shell, text = 'Add Class Type', command = lambda: addClassType(Master, accountID))
    classTypeAddBtn.grid(row = 2, column = 0, columnspan = 2, sticky='NSEW', padx = 5)

    dateLabel = tk.Label(master = shell, text = "Date", font=("Arial", 16))
    dateLabel.grid(row = 3, column = 0, sticky = 'W', padx = 15, pady = 5)
    dateDropDown = tkcalendar.DateEntry(master=shell, mindate = datetime.date.today(), date_pattern = 'dd/mm/yyyy')
    dateDropDown.grid(row = 3, column = 1)

    timeLabel = tk.Label(master = shell, text = 'Time', font = ('Arial', 16))
    timeLabel.grid(row = 4, column = 0, sticky = 'W', padx = 15, pady = 5)
    timePicker = tk.Frame(shell)
    timePicker.grid(row = 4, column = 1)

    timePicker.grid_columnconfigure(0, weight = 3)
    timePicker.grid_columnconfigure(1, weight = 1)
    timePicker.grid_columnconfigure(2, weight = 3)

    timePicker.grid_rowconfigure(0, weight = 1)

    hours = tk.StringVar()
    hoursBox = tk.Spinbox(master = timePicker, from_=0, to= 23, textvariable=hours, width=2, format="%02.0f")
    hoursBox.grid(row = 0, column = 0)
    colon = tk.Label(master = timePicker, text = ':')
    colon.grid(row = 0, column = 1)
    minutes = tk.StringVar()
    minutesBox = tk.Spinbox(master = timePicker, from_ = 00, to = 59, textvariable=minutes, width=2, format="%02.0f")
    minutesBox.grid(row =0, column = 2)

    nameBoxLabel = tk.Label(master = shell, text = 'Enter Alternative Name', font = ('Arial', 14))
    nameBoxLabel.grid(row=5, column = 0, sticky = 'NSEW', padx = 5, pady = 5)
    customName = tk.StringVar()
    nameBox = tk.Entry(master = shell, textvariable=customName)
    nameBox.grid(row = 5, column = 1, padx = 5)

    def addClassAction():
        customNameWrite = customName.get() if customName.get != '' else None
        date = (str(dateDropDown.get_date()) + " "+ hours.get()+":"+minutes.get()+":00")
        classIndex = classTypes.index(classTypeSelect.get())
        classTypeID = backend.getClassType()[classIndex][0]

        classID = backend.addClassNoInstuctors(classTypeID, date, customNameWrite)
        addInstructors(Master= Master, accountID=accountID, classID=classID)
    
    classCreateBtn = tk.Button(master = shell, text = 'Create Class', command = addClassAction)
    classCreateBtn.grid(row = 6, column = 0, columnspan = 2, sticky='NSEW', padx = 5)   





def addClassType(Master, accountID):
    resetGuiShell(Master)

    shell.grid_columnconfigure(0, weight=6)
    shell.grid_columnconfigure(1, weight =6)
    shell.grid_columnconfigure(2, weight =1)

    titleLabel = tk.Label(master = shell, text = "Add Class Type", font=("Arial Bold", 20))
    titleLabel.grid(row = 0, column = 0, columnspan = 3, sticky = 'W', padx = 10, pady = 5)

    nameLabel = tk.Label(master = shell, text = "Class Name", font=("Arial", 16))
    nameLabel.grid(row = 1, column = 0, sticky = 'W', padx = 15, pady = 5)
    name = tk.StringVar()
    nameEntry = tk.Entry(master = shell, textvariable=name)
    nameEntry.grid(row = 1, column=1, columnspan = 2)


    descriptionLabel = tk.Label(master = shell, text = "Description", font=("Arial", 16))
    descriptionLabel.grid(row = 2, column = 0, sticky = 'W', padx = 15, pady = 5)
    descriptionEntry = tk.Text(master = shell, width = 30, height = 5)
    descriptionEntry.grid(row = 2, column=1, columnspan = 2, sticky = 'N')


    lowerAgeLabel = tk.Label(master = shell, text = "Lower Age Limit", font=("Arial", 16))
    lowerAgeLabel.grid(row = 3, column = 0, padx  = 5, sticky = 'W')
    lowerAge = tk.StringVar()
    lowerAgeBox = tk.Spinbox(master = shell, from_ = 0, to = 100, textvariable=lowerAge, width=2)
    lowerAgeBox.grid(row = 3, column =1, padx = 5)
    lowerAgeBool = tk.IntVar()
    lowerAgeTickbox = tk.Checkbutton(master = shell, variable = lowerAgeBool, onvalue=1, offvalue=0)
    lowerAgeTickbox.grid(row = 3, column = 2)


    upperAgeLabel = tk.Label(master = shell, text = "Upper Age Limit", font=("Arial", 16))
    upperAgeLabel.grid(row = 4, column = 0, padx  = 5, sticky = 'W')
    upperAge = tk.StringVar()
    upperAgeBox = tk.Spinbox(master = shell, from_ = 0, to = 100, textvariable=upperAge, width=2)
    upperAgeBox.grid(row = 4, column =1, padx = 5)
    upperAgeBool = tk.IntVar()
    upperAgeTickbox = tk.Checkbutton(master = shell, variable = upperAgeBool, onvalue=1, offvalue=0)
    upperAgeTickbox.grid(row = 4, column = 2)


    capacityLimitLabel = tk.Label(master = shell, text = "Customer Limit", font=("Arial", 16))
    capacityLimitLabel.grid(row = 5, column = 0, padx  = 5, sticky = 'W')
    capacityLimit = tk.StringVar()
    capacityLimitBox = tk.Spinbox(master = shell, from_ = 0, to = 100, textvariable=capacityLimit, width=2)
    capacityLimitBox.grid(row = 5, column =1, padx = 5)
    capacityLimitBool = tk.IntVar()
    capacityLimitTickbox = tk.Checkbutton(master = shell, variable = capacityLimitBool, onvalue=1, offvalue=0)
    capacityLimitTickbox.grid(row = 5, column = 2)


    instructorReqLabel = tk.Label(master = shell, text = "Instructors Required", font=("Arial", 16))
    instructorReqLabel.grid(row = 6, column = 0, padx  = 5, sticky = 'W')
    instructorReq = tk.StringVar()
    instructorReqBox = tk.Spinbox(master = shell, from_ = 0, to = 100, textvariable=instructorReq, width=2)
    instructorReqBox.grid(row = 6, column =1, padx = 5)
    instructorReqBool = tk.IntVar()
    instructorReqTickbox = tk.Checkbutton(master = shell, variable = instructorReqBool, onvalue=1, offvalue=0)
    instructorReqTickbox.grid(row = 6, column = 2)


    lengthLabel = tk.Label(master = shell, text = 'Length (hrs:mins)', font = ('Arial', 16))
    lengthLabel.grid(row = 7, column = 0, sticky = 'W', padx = 15, pady = 5)
    lengthPicker = tk.Frame(shell)
    lengthPicker.grid(row = 7, column = 1)

    lengthPicker.grid_columnconfigure(0, weight = 3)
    lengthPicker.grid_columnconfigure(1, weight = 1)
    lengthPicker.grid_columnconfigure(2, weight = 3)

    lengthPicker.grid_rowconfigure(0, weight = 1)

    hours = tk.StringVar()
    hoursBox = tk.Spinbox(master = lengthPicker, from_=0, to= 23, textvariable=hours, width=2, format="%02.0f")
    hoursBox.grid(row = 0, column = 0)
    colon = tk.Label(master = lengthPicker, text = ':')
    colon.grid(row = 0, column = 1)
    minutes = tk.StringVar()
    minutesBox = tk.Spinbox(master = lengthPicker, from_ = 00, to = 59, textvariable=minutes, width=2, format="%02.0f")
    minutesBox.grid(row =0, column = 2)

    priceLabel = tk.Label(master = shell, text = 'Price (£)', font = ('Arial', 16))
    priceLabel.grid(row = 8, column = 0, sticky = 'W', padx = 15, pady = 5)
    price = tk.StringVar()
    priceEntry = tk.Entry(master = shell, textvariable=price)
    priceEntry.grid(row = 8, column = 1, sticky = 'NSEW', pady = 5)



    def addClassTypeAction(Master, accountID):
        #Error checking
        if name.get() == '':
            messagebox.showerror('Class Type Error', 'Name field must be filled')
            return
        elif bool(re.match(r'^\d+(\.\d{1,2})?$', price.get()))==False:
            messagebox.showerror('Class Type Error', 'Price must be a decimal rounded to 2 decimal places')
            return
        elif int(lowerAge.get()) >= int(upperAge.get()) and upperAgeBool.get()==1 and lowerAgeBool.get()==1:
            messagebox.showerror('Class Type Error', 'Lower age must be less than upper age if both are in use')
            return
        elif int(hours.get())==0 and int(minutes.get())==0:
            messagebox.showerror('Class Type Error', 'Cannot have a class type with no length')
            return
        
        #add to db
        backend.addClassType(name = name.get(),
                             description= descriptionEntry.get('1.0', tk.END) if descriptionEntry.get('1.0', tk.END)!= '' and descriptionEntry.get('1.0', tk.END) != '\n' else None,
                             lowerAge = int(lowerAge.get()) if lowerAgeBool.get() ==1 else None,
                             upperAge = int(upperAge.get()) if upperAgeBool.get() ==1 else None,
                             capacity= int(capacityLimit.get()) if capacityLimitBool.get() ==1 else None,
                             noStaff= int(instructorReq.get()) if instructorReqBool.get() ==1 else None,
                             length = int(hours.get())*60+int(minutes.get()),
                             price = float(price.get()) if price.get() != '' else None)
        

        classesMenu(Master, accountID)

    addButton = tk.Button(master = shell, text = 'Add Class Type', command = lambda: addClassTypeAction(Master, accountID))
    addButton.grid(row = 9, column = 0, columnspan = 3, sticky = 'NSEW', pady = 5)


#main classes menu
def classesMenu(Master, accountID):
    resetGuiShell(Master)
    shell.grid_rowconfigure(0, weight = 1)
    shell.grid_rowconfigure(1, weight = 3)


    shell.grid_columnconfigure(0, weight = 1)

    classesTitle = tk.Label(master = shell, text = "Classes", font=("Arial Bold", 20))
    classesTitle.grid(row = 0, column = 0, sticky = 'NSEW')

    viewClassesBtn = tk.Button(master = shell, text = 'Find Classes', command = lambda: findClassesMenu(Master=Master, accountID=accountID))
    viewClassesBtn.grid(row = 1, column = 0, sticky = 'NSEW', padx = 10)
    
    #show booked classes for customer
    if accounts.getPermissions(accountID) == 1:
        shell.grid_rowconfigure(2, weight = 2)
        shell.grid_rowconfigure(3, weight = 10)
        shell.grid_rowconfigure(4, weight = 3)

        myBookingsTitle = tk.Label(master = shell, text = 'My Bookings', font=("Arial", 16))
        myBookingsTitle.grid(row = 2, pady=(10, 5), sticky= 'W', padx = 15)
        pass

        #using list comprehension to organise names and times of classes into nice format
        customerID = accounts.getCustomer(accountID)[0][0]
        bookings = backend.getBookings(customerID = customerID)
        classIDs = [booking[1] for booking in bookings]
        classesList = [backend.getClass(classID = classID) for classID in classIDs]
        #print(classes)
        dates = [datetime.datetime.strptime(classSelect[0][3], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y') for classSelect in classesList]
        names = [backend.getClassType(classTypeID=classSelect[0][1])[0][1] for classSelect in classesList]
        
        options = []
        for index in range(len(names)):
            options.append(names[index] + ' - ' + dates[index])
        optionsVar = tk.StringVar(value=options)
        
        bookingsBox = tk.Listbox(master = shell, listvariable=optionsVar, selectmode='single')
        bookingsBox.grid(row = 3, column=0, sticky='NSEW', padx = 10)

        def bookingsBoxBtnAction():
            bookingSelect = bookingsBox.curselection()[0]
            viewClass(Master = Master, accountID=accountID, classID= classesList[bookingSelect][0][0])
        bookingsBoxBtn = tk.Button(master = shell, text = 'View Booking', command = bookingsBoxBtnAction)
        bookingsBoxBtn.grid(row = 4, column=0, sticky = 'NSEW', padx = 10, pady = 10)
        

    #show assinged classes for instructors
    elif accounts.getPermissions(accountID) == 2 or accounts.getPermissions(accountID) == 3:
        shell.grid_rowconfigure(2, weight = 2)
        shell.grid_rowconfigure(3, weight = 10)
        shell.grid_rowconfigure(4, weight = 3)

        myAssignmentsTitle = tk.Label(master = shell, text = 'My Classes', font=("Arial", 16))
        myAssignmentsTitle.grid(row = 2, pady=(10, 5), sticky= 'W', padx = 15)
        pass

        #using list comprehension to organise names and times of classes into nice format - alll of this copied and pasted for instructors
        instructorID = accounts.getInstructor(accountID)[0][0]
        assignments = backend.getAssignment(instructorID= instructorID)
        classIDs = [assignment[1] for assignment in assignments]
        classesList = [backend.getClass(classID = classID) for classID in classIDs]
        #print(classes)
        dates = [datetime.datetime.strptime(classSelect[0][3], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y') for classSelect in classesList]
        names = [backend.getClassType(classTypeID=classSelect[0][1])[0][1] for classSelect in classesList]
        
        options = []
        for index in range(len(names)):
            options.append(names[index] + ' - ' + dates[index])
        optionsVar = tk.StringVar(value=options)
        
        assignmentsBox = tk.Listbox(master = shell, listvariable=optionsVar, selectmode='single')
        assignmentsBox.grid(row = 3, column=0, sticky='NSEW', padx = 10)

        def assignmentsBoxBtnAction():
            try:
                assignmentSelect = assignmentsBox.curselection()[0]
            except IndexError:
                return
            viewClass(Master = Master, accountID=accountID, classID= classesList[assignmentSelect][0][0])
        assignmentsBoxBtn = tk.Button(master = shell, text = 'View Class', command = assignmentsBoxBtnAction)
        assignmentsBoxBtn.grid(row = 4, column=0, sticky = 'NSEW', padx = 10, pady = 10)

        if accounts.getPermissions(accountID) == 3:
            #sort out admin level stuff adn do teh same in viewClass
            shell.grid_rowconfigure(5, weight = 3)
            shell.grid_rowconfigure(6, weight = 3)
            shell.grid_rowconfigure(7, weight = 3)

            addClassBtn = tk.Button(master = shell, text = 'Schedule Class', command = lambda: addClass(Master, accountID))
            addClassBtn.grid(row = 5, column = 0, sticky = 'NSEW', padx = 5, pady = 5)

            addClassTypeBtn = tk.Button(master = shell, text = 'Add Class Type', command = lambda: addClassType(Master, accountID))
            addClassTypeBtn.grid(row = 6, column = 0, sticky = 'NSEW', padx = 5, pady = 5)


#window = tk.Tk()
#window.minsize(300,300)
#shell = tk.Frame()
##style = ttk.Style(window)
#style.theme_use('alt')
#classesMenu(window, 1) #customer test
#classesMenu(window, 11) # non admin staff test
#classesMenu(window, 15) # admin test
#window.mainloop()