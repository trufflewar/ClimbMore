import tkinter as tk
import accountsBackend as backend
import membershipsBackend as memberships
import datetime
from dateutil import relativedelta
from tkinter import messagebox
import tkcalendar
from tkinter import ttk
import re


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
    

def changeEmail(customerID, staff):
    popUp = tk.Toplevel()
    popUp.title("Change Email")
    
    popUp.grid_columnconfigure(0, weight=4)
    popUp.grid_columnconfigure(1, weight = 7)

    titleLabel = tk.Label(master = popUp, text = 'Change Email', font = ('Arial Bold', 20))
    titleLabel.grid(row = 0, column = 0, columnspan=2, sticky='W', pady=5, padx= 10)

    emailLabel = tk.Label(master = popUp, text = 'Enter Email:')
    emailLabel.grid(row = 1, column = 0, sticky='W', pady=5, padx= 10)

    confirmLabel = tk.Label(master = popUp, text = 'Confirm Email:')
    confirmLabel.grid(row = 2, column = 0, sticky='W', pady=5, padx= 10)

    email = tk.StringVar()
    emailBox = tk.Entry(master = popUp, textvariable=email)
    emailBox.grid(row = 1, column = 1, padx= 10)

    confirm = tk.StringVar()
    confirmBox = tk.Entry(master = popUp, textvariable=confirm)
    confirmBox.grid(row = 2, column = 1, padx= 10)

    #verify the emails match, then check with verification subroutine
    def changeBtnAction():
        if emailBox.get() == confirmBox.get():
            if backend.verifyEmail(email=emailBox.get()):
                backend.editCustomer(customerID=customerID, email=emailBox.get())
                messagebox.showinfo("Success", "Email changed successfully!")
                popUp.destroy()
                popUp.update()
            else:
                messagebox.showerror("Invalid Email", "Email is invalid")
        else:
            messagebox.showerror("Invalid Email", "Email addresses do not match")
    changeBtn = tk.Button(master = popUp, text = "Change", command=changeBtnAction)
    changeBtn.grid(row = 3, column = 0, columnspan = 2)

    popUp.protocol("WM_DELETE_WINDOW", lambda: popUp.destroy())

    popUp.mainloop()



def changePassword(accountID, staff):
    username = backend.getUsername(accountID)
    
    popUp = tk.Toplevel()
    popUp.title("Change Password")
    
    popUp.grid_columnconfigure(0, weight=4)
    popUp.grid_columnconfigure(1, weight = 7)

    titleLabel = tk.Label(master = popUp, text = 'Change Password', font = ('Arial Bold', 20))
    titleLabel.grid(row = 0, column = 0, columnspan=2, sticky='W', pady=5, padx= 10)

    if staff != True:
        oldPasswordLabel = tk.Label(master = popUp, text = 'Enter Old Password:')
        oldPasswordLabel.grid(row = 1, column = 0, sticky='W', pady=5, padx= 10)

    passwordLabel = tk.Label(master = popUp, text = 'Enter New Password:')
    passwordLabel.grid(row = 2, column = 0, sticky='W', pady=5, padx= 10)

    confirmLabel = tk.Label(master = popUp, text = 'Confirm New Password:')
    confirmLabel.grid(row = 3, column = 0, sticky='W', pady=5, padx= 10)

    if staff != True:
        oldPassword = tk.StringVar()
        oldPasswordBox = tk.Entry(master = popUp, textvariable=oldPassword, show='*')
        oldPasswordBox.grid(row = 1, column = 1, padx= 10)

    password = tk.StringVar()
    passwordBox = tk.Entry(master = popUp, textvariable=password, show='*')
    passwordBox.grid(row = 2, column = 1, padx= 10)

    confirm = tk.StringVar()
    confirmBox = tk.Entry(master = popUp, textvariable=confirm, show='*')
    confirmBox.grid(row = 3, column = 1, padx= 10)

    def changeBtnAction():
        if passwordBox.get() == confirmBox.get():
            if staff == True:
                backend.adminChangePassword(accountID, passwordBox.get())
                messagebox.showinfo("Success", "Password changed successfully!")
                popUp.destroy()
                popUp.update()
            else:
                if backend.changePassword(username, oldPasswordBox.get(), passwordBox.get()) == 'ChangedPassword':
                    messagebox.showinfo("Success", "Password changed successfully!")
                    popUp.destroy()
                    popUp.update()
                else:
                    messagebox.showerror("Invalid Password", "Old password is incorrect")
        else:
            messagebox.showerror("Invalid Password", "Passwords do not match")
    changeBtn = tk.Button(master = popUp, text = "Change", command=changeBtnAction)
    changeBtn.grid(row = 4, column = 0, columnspan = 2)

    popUp.protocol("WM_DELETE_WINDOW", lambda: popUp.destroy())

    popUp.mainloop()



def showCustomer(Master, accountID, staff):
    #Create frame and get details
    resetGuiShell(Master)

    try:
        details = backend.getCustomer(accountID = accountID)[0]
    except IndexError:
        return 'CustomerDoesNotExist'

    #find age
    dob = datetime.datetime.strptime(details[5], '%Y-%m-%d').replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    now = datetime.datetime.now().replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    age = relativedelta.relativedelta(now, dob).years
    #print(age)

    shell.columnconfigure(0, weight = 2)

    nameLabel = tk.Label(master = shell, text = details[3]+", "+details[2]+", "+str(age)+"yrs", font = ('Arial Bold', 20))
    nameLabel.grid(row = 0, column = 0, columnspan=2, sticky='W', pady=5, padx= 10)

    emailLabel = tk.Label(master = shell, text = "Email: "+details[4], font = ('Arial', 16))
    emailLabel.grid(row = 1, column = 0, sticky = 'W', padx = 15)

    changeEmailBtn = tk.Button(master = shell, text = 'Change', command=lambda: changeEmail(customerID=details[0], staff = staff))
    changeEmailBtn.grid(row = 1, column = 1)

    currentMembership = memberships.getMembershipRecord(customerID=details[0], ACTIVE=True)
    try:
        membershipDetails = memberships.getMemberships(membershipID = currentMembership[1])[0]
    except IndexError:
        membershipDetails = [None, 'None']
    membershipLabel = tk.Label(master = shell, text = 'Membership: '+ membershipDetails[1], font = ('Arial', 16))
    membershipLabel.grid(row = 2, column = 0, columnspan=2, sticky = 'W', padx =15)

    changePasswordBtn = tk.Button(master = shell, text = 'Change Password', command = lambda: changePassword(accountID, staff))
    changePasswordBtn.grid(row = 3, column = 0, columnspan = 2, sticky = 'W', padx = 10)



def showInstructor(Master, accountID, admin):
    #Create frame and get details
    resetGuiShell(Master)

    try:
        details = backend.getInstructor(accountID = accountID)[0]
    except IndexError:
        return 'InstructorDoesNotExist'

    shell.grid_columnconfigure(0, weight = 2)

    nameLabel = tk.Label(master = shell, text = details[2], font = ('Arial Bold', 20))
    nameLabel.grid(row = 0, column = 0, columnspan=2, sticky='W', pady=5, padx= 10)

    emailLabel = tk.Label(master = shell, text = "Email: "+details[3], font = ('Arial', 16))
    emailLabel.grid(row = 1, column = 0, sticky = 'W', padx = 15)

    changeEmailBtn = tk.Button(master = shell, text = 'Change', command=lambda: changeEmail(customerID=details[0], staff = admin))
    changeEmailBtn.grid(row = 1, column = 1)

    currentPay = '£'+ str('%.2f' % details[4])
    payLabel = tk.Label(master = shell, text = 'Pay: '+ currentPay + '/hr', font = ('Arial', 16))
    payLabel.grid(row = 2, column = 0, columnspan=2, sticky = 'W', padx =15)

    changePasswordBtn = tk.Button(master = shell, text = 'Change Password', command = lambda: changePassword(accountID, admin))
    changePasswordBtn.grid(row = 3, column = 0, columnspan = 2, sticky = 'W', padx = 10)

    #TODO cahnge password and email
    #TODO deal with closing pop ups crashing program



def addCustomer(Master, accountID):
    resetGuiShell(Master)

    shell.grid_columnconfigure(0, weight=3)
    shell.grid_columnconfigure(1, weight =7)

    titleLabel = tk.Label(master = shell, text = "Add Customer", font=("Arial Bold", 20))
    titleLabel.grid(row = 0, column = 0, columnspan = 2, sticky = 'W', padx = 10, pady = 5)

    fnameLabel = tk.Label(master = shell, text = "Firstname", font=("Arial", 16))
    fnameLabel.grid(row = 1, column = 0, sticky = 'W', padx = 15, pady = 5)
    fname = tk.StringVar()
    fnameEntry = tk.Entry(master = shell, textvariable=fname)
    fnameEntry.grid(row = 1, column=1)

    snameLabel = tk.Label(master = shell, text = "Surname", font=("Arial", 16))
    snameLabel.grid(row = 2, column = 0, sticky = 'W', padx = 15, pady = 5)
    sname = tk.StringVar()
    snameEntry = tk.Entry(master = shell, textvariable=sname)
    snameEntry.grid(row = 2, column=1)

    dobLabel = tk.Label(master = shell, text = "DOB", font=("Arial", 16))
    dobLabel.grid(row = 3, column = 0, sticky = 'W', padx = 15, pady = 5)
    dobDropDown = tkcalendar.DateEntry(master=shell, maxdate = datetime.date.today(), date_pattern = 'dd/mm/yyyy')
    dobDropDown.grid(row = 3, column = 1)

    emailLabel = tk.Label(master = shell, text = "Email", font=("Arial", 16))
    emailLabel.grid(row = 4, column = 0, sticky = 'W', padx = 15, pady = 5)
    email = tk.StringVar()
    emailEntry = tk.Entry(master = shell, textvariable=email)
    emailEntry.grid(row = 4, column=1)

    email2Label = tk.Label(master = shell, text = "Confirm Email", font=("Arial", 16))
    email2Label.grid(row = 5, column = 0, sticky = 'W', padx = 15, pady = 5)
    email2 = tk.StringVar()
    email2Entry = tk.Entry(master = shell, textvariable=email2)
    email2Entry.grid(row = 5, column=1)

    usernameLabel = tk.Label(master = shell, text = "Username", font=("Arial", 16))
    usernameLabel.grid(row = 6, column = 0, sticky = 'W', padx = 15, pady = 5)
    username = tk.StringVar()
    usernameEntry = tk.Entry(master = shell, textvariable=username)
    usernameEntry.grid(row = 6, column=1)

    passwordLabel = tk.Label(master = shell, text = 'Password', font=("Arial", 16))
    passwordLabel.grid(row = 7, column = 0, sticky='W', pady=5, padx= 15)
    password = tk.StringVar()
    passwordBox = tk.Entry(master = shell, textvariable=password, show='*')
    passwordBox.grid(row = 7, column = 1, padx= 10)

    #TODO show password button in column 3, add columnspan2 to the rest fo column 2 widgets except password

    password2Label = tk.Label(master = shell, text = 'Confirm Password', font=("Arial", 16))
    password2Label.grid(row = 8, column = 0, sticky='W', pady=5, padx= 15)
    password2 = tk.StringVar()
    password2Box = tk.Entry(master = shell, textvariable=password2, show='*')
    password2Box.grid(row = 8, column = 1, padx= 10)

    safetyBrief = tk.IntVar()
    safetyBriefBox = tk.Checkbutton(master = shell, text = 'Customer has completed safety briefing and signed waiver.', variable = safetyBrief, onvalue=1, offvalue=0, font=("Arial", 16))
    safetyBriefBox.grid(row = 9, column = 0, columnspan=2, sticky = 'W', padx = 15, pady = 5)

    def addCustomerAction():
        if fname.get() == '' or sname.get() == '':
            messagebox.showerror('Name Error', 'Name fields cannot be blank.')
            return
        elif email.get() != email2.get():
            messagebox.showerror('Email Error', 'Email fields must be the same.')
            return
        elif backend.verifyEmail(email.get()) == False or len(email.get())<1:
            messagebox.showerror('Email Error', 'Email address is invalid')
            return
        elif backend.checkGoodUsername(username = username.get())==False:
            messagebox.showerror('Username Error', 'Username is in use by another customer or is too short')
            return
        elif password.get() != password2.get():
            messagebox.showerror('Password Error', 'Passwords must match')
            return
        elif len(password.get()) <=7:
            messagebox.showerror('Password Error', 'Passwords must be at least 8 characters')
            return
        elif safetyBrief.get() != 1:
            messagebox.showerror('Account Error', 'Customer must complete safety brief')
            return
        else:
            backend.addNewCustomer(username.get(), password.get(), fname.get(), sname.get(), email.get(), dobDropDown.get_date())
            accountsMenu(Master=Master, accountID=accountID)

    addCustomerBtn = tk.Button(master = shell, text = 'Add Customer', command = addCustomerAction)
    addCustomerBtn.grid(row = 10, column = 0, columnspan=2, sticky = 'NSEW', pady = 10)


def addStaff(Master, accountID):
    resetGuiShell(Master)

    shell.grid_columnconfigure(0, weight=3)
    shell.grid_columnconfigure(1, weight =7)

    titleLabel = tk.Label(master = shell, text = "Add Instructor", font=("Arial Bold", 20))
    titleLabel.grid(row = 0, column = 0, columnspan = 2, sticky = 'W', padx = 10, pady = 5)

    nameLabel = tk.Label(master = shell, text = "Name", font=("Arial", 16))
    nameLabel.grid(row = 1, column = 0, sticky = 'W', padx = 15, pady = 5)
    name = tk.StringVar()
    nameEntry = tk.Entry(master = shell, textvariable=name)
    nameEntry.grid(row = 1, column=1)

    payLabel = tk.Label(master = shell, text = "Pay (£/hr)", font=("Arial", 16))
    payLabel.grid(row = 2, column = 0, sticky = 'W', padx = 15, pady = 5)
    pay = tk.StringVar()
    payEntry = tk.Entry(master = shell, textvariable=pay)
    payEntry.grid(row = 2, column=1)

    emailLabel = tk.Label(master = shell, text = "Email", font=("Arial", 16))
    emailLabel.grid(row = 3, column = 0, sticky = 'W', padx = 15, pady = 5)
    email = tk.StringVar()
    emailEntry = tk.Entry(master = shell, textvariable=email)
    emailEntry.grid(row = 3, column=1)

    email2Label = tk.Label(master = shell, text = "Confirm Email", font=("Arial", 16))
    email2Label.grid(row = 4, column = 0, sticky = 'W', padx = 15, pady = 5)
    email2 = tk.StringVar()
    email2Entry = tk.Entry(master = shell, textvariable=email2)
    email2Entry.grid(row = 4, column=1)

    usernameLabel = tk.Label(master = shell, text = "Username", font=("Arial", 16))
    usernameLabel.grid(row = 5, column = 0, sticky = 'W', padx = 15, pady = 5)
    username = tk.StringVar()
    usernameEntry = tk.Entry(master = shell, textvariable=username)
    usernameEntry.grid(row = 5, column=1)

    passwordLabel = tk.Label(master = shell, text = 'Password', font=("Arial", 16))
    passwordLabel.grid(row = 6, column = 0, sticky='W', pady=5, padx= 15)
    password = tk.StringVar()
    passwordBox = tk.Entry(master = shell, textvariable=password, show='*')
    passwordBox.grid(row = 6, column = 1, padx= 10)

    #TODO show password button in column 3, add columnspan2 to the rest fo column 2 widgets except password

    password2Label = tk.Label(master = shell, text = 'Confirm Password', font=("Arial", 16))
    password2Label.grid(row = 7, column = 0, sticky='W', pady=5, padx= 15)
    password2 = tk.StringVar()
    password2Box = tk.Entry(master = shell, textvariable=password2, show='*')
    password2Box.grid(row = 7, column = 1, padx= 10)

    admin = tk.IntVar()
    adminBox = tk.Checkbutton(master = shell, text = 'Instructor is admin', variable = admin, onvalue=1, offvalue=0, font=("Arial", 16))
    adminBox.grid(row = 8, column = 0, columnspan=2, sticky = 'W', padx = 15, pady = 5)

    def addStaffAction():
        if name.get() == '':
            messagebox.showerror('Name Error', 'Name field cannot be blank.')
            return
        elif bool(re.match(r'^\d+(\.\d{1,2})?$', pay.get()))==False:
            messagebox.showerror('Pay error', 'Pay must be a decimal rounded to 2 decimal places')
            return
        elif email.get() != email2.get():
            messagebox.showerror('Email Error', 'Email fields must be the same.')
            return
        elif backend.verifyEmail(email.get()) == False or len(email.get())<1:
            messagebox.showerror('Email Error', 'Email address is invalid')
            return
        elif backend.checkGoodUsername(username = username.get())==False:
            messagebox.showerror('Username Error', 'Username is in use by another person or is too short')
            return
        elif password.get() != password2.get():
            messagebox.showerror('Password Error', 'Passwords must match')
            return
        elif len(password.get()) <=7:
            messagebox.showerror('Password Error', 'Passwords must be at least 8 characters')
            return
        else:
            backend.addNewStaff(username.get(), password.get(), name.get(), float(pay.get()), email.get(), certs=[], admin = adminBox.get())

    addStaffBtn = tk.Button(master = shell, text = 'Add Instructor', command = addStaffAction)
    addStaffBtn.grid(row = 9, column = 0, columnspan=2, sticky = 'NSEW', pady = 10)





def searchCustomers(Master, accountID):
    resetGuiShell(Master)

    titleLabel = tk.Label(master = shell, text = "Search Customers", font=("Arial Bold", 20))
    titleLabel.grid(row = 0, column = 0, columnspan = 2, sticky = 'W', padx = 10, pady = 5)

    fnameLabel = tk.Label(master = shell, text = "Firstname", font=("Arial", 16))
    fnameLabel.grid(row = 1, column = 0, sticky = 'W', padx = 15, pady = 5)
    fname = tk.StringVar()
    fnameEntry = tk.Entry(master = shell, textvariable=fname)
    fnameEntry.grid(row = 1, column=1)

    snameLabel = tk.Label(master = shell, text = "Surname", font=("Arial", 16))
    snameLabel.grid(row = 2, column = 0, sticky = 'W', padx = 15, pady = 5)
    sname = tk.StringVar()
    snameEntry = tk.Entry(master = shell, textvariable=sname)
    snameEntry.grid(row = 2, column=1)

    emailLabel = tk.Label(master = shell, text = "Email", font=("Arial", 16))
    emailLabel.grid(row = 4, column = 0, sticky = 'W', padx = 15, pady = 5)
    email = tk.StringVar()
    emailEntry = tk.Entry(master = shell, textvariable=email)
    emailEntry.grid(row = 4, column=1)

    def searchCustomersAction():
        fnameSearch = fname.get() if fname.get()!='' else None
        snameSearch = sname.get() if sname.get()!='' else None
        emailSearch = email.get() if email.get()!='' else None
        results = backend.getCustomer(fname = fnameSearch, sname = snameSearch, email = emailSearch)
        if len(results)!=0:
            viewCustomers(Master, results, True, accountID)
        else:
            messagebox.showinfo("Customer Search", "No customers were found matching those parameters")
    searchBtn = tk.Button(master = shell, text = 'Search', command = searchCustomersAction)
    searchBtn.grid(row= 5, column = 0, columnspan = 2)



def viewCustomers(Master, customerList, search, accountID):
    resetGuiShell(Master)

    if search:
        title = 'Customer Search Results'
    else:
        title = 'All Customers'

    shell.grid_columnconfigure(0, weight=2)
    shell.grid_columnconfigure(1, weight = 1)

    titleLabel = tk.Label(master = shell, text = title, font=("Arial Bold", 20))
    titleLabel.grid(row = 0, column = 0, columnspan = 2, sticky = 'W', padx = 10, pady = 5)

    options = [customer[3]+', '+customer[2] for customer in customerList]
    optionsVar = tk.StringVar(value = options)
    customerListbox = tk.Listbox(master=shell, listvariable=optionsVar, selectmode='single')
    customerListbox.grid(row = 1, rowspan=3, column = 0, padx = 10, pady = 10)

    addButton = tk.Button(master = shell, text = "Add Customer", command = lambda: addCustomer(Master = Master, accountID=accountID))
    addButton.grid(row = 1, column = 1)

    viewButton = tk.Button(master = shell, text = "View Customer", command = lambda: showCustomer(Master, customerList[customerListbox.curselection()[0]][1], staff = True))
    viewButton.grid(row = 2, column = 1)

    def deleteAction():
        if messagebox.askokcancel("Customer Deletion", "Please confirm customer deletion"):
            index = customerListbox.curselection()[0]
            customerID = customerList[index][0]
            backend.removeCustomer(customerID=customerID)
            accountsMenu(Master, accountID)
        else:
            return
    delButton = tk.Button(master = shell, text = "Delete Customer", command = deleteAction)
    delButton.grid(row = 3, column = 1)



def viewAllStaff(Master, accountID):
    resetGuiShell(Master)

    staffList = backend.getInstructor()

    shell.grid_columnconfigure(0, weight=2)
    shell.grid_columnconfigure(1, weight = 1)

    titleLabel = tk.Label(master = shell, text = 'All Staff', font=("Arial Bold", 20))
    titleLabel.grid(row = 0, column = 0, columnspan = 2, sticky = 'W', padx = 10, pady = 5)

    options = [instructor[2] for instructor in staffList]
    optionsVar = tk.StringVar(value = options)
    staffListbox = tk.Listbox(master=shell, listvariable=optionsVar, selectmode='single')
    staffListbox.grid(row = 1, rowspan=3, column = 0, padx = 10, pady = 10)

    addButton = tk.Button(master = shell, text = "Add Instructor", command = lambda: addStaff(Master = Master, accountID=accountID))
    addButton.grid(row = 1, column = 1)

    viewButton = tk.Button(master = shell, text = "View Instructor", command = lambda: showInstructor(Master, staffList[staffListbox.curselection()[0]][1], admin = True))
    viewButton.grid(row = 2, column = 1)

    def deleteAction():
        if messagebox.askokcancel("Customer Deletion", "Please confirm customer deletion"):
            index = staffListbox.curselection()[0]
            instructorID = staffList[index][0]
            backend.removeInstructor(instructorID=instructorID)
            accountsMenu(Master, accountID)
        else:
            return
    delButton = tk.Button(master = shell, text = "Delete Instructor", command = deleteAction)
    delButton.grid(row = 3, column = 1)



def viewAllCustomers(Master, accountID):
    customerList = backend.getCustomer()
    viewCustomers(Master, customerList, False, accountID)



#MAIN MENU for CUSTOMER MANAGEMENT
def accountsMenu(Master, accountID):
    if backend.getPermissions(accountID) == 1:
        showCustomer(Master, backend.getCustomer(accountID=accountID)[0][1], False)

    else:
        resetGuiShell(Master)

        #literally the only way to fix the weird formatting issues :/
        shell.grid_rowconfigure(0, weight=1)
        shell.grid_rowconfigure(1, weight=3)
        shell.grid_rowconfigure(2, weight=3)
        shell.grid_rowconfigure(3, weight=3)
        shell.grid_rowconfigure(6, weight=3)

        shell.grid_columnconfigure(0, weight = 1)

        accountsTitle = tk.Label(master = shell, text = "Accounts", font=("Arial Bold", 20))
        accountsTitle.grid(row = 0, column = 0, sticky = 'NSEW')
        
        addCustomerBtn = tk.Button(master = shell, text = "Add Customer", command= lambda: addCustomer(Master=Master, accountID = accountID))
        addCustomerBtn.grid(row = 1, column = 0, sticky = 'NSEW')

        searchCustomerBtn = tk.Button(master = shell, text = "Search Customers", command = lambda: searchCustomers(Master = Master,accountID=accountID))
        searchCustomerBtn.grid(row=2, column = 0, sticky = 'NSEW')

        viewCustomerBtn = tk.Button(master = shell, text = "View Customers", command = lambda: viewAllCustomers(Master = Master, accountID=accountID))
        viewCustomerBtn.grid(row =3 , column = 0, sticky = 'NSEW')

        if backend.getPermissions(accountID) == 3:
            shell.grid_rowconfigure(4, weight=3)
            shell.grid_rowconfigure(5, weight=3)
            
            addStaffBtn = tk.Button(master = shell, text = "Add Instructors", command= lambda: addStaff(Master=Master, accountID = accountID))
            addStaffBtn.grid(row = 4, column = 0, sticky = 'NSEW')

            viewStaffBtn = tk.Button(master = shell, text = "View Instructors", command = lambda: viewAllStaff(Master = Master, accountID=accountID))
            viewStaffBtn.grid(row =5 , column = 0, sticky = 'NSEW')
            
            #Admin level stuff here - add staff, view staff etc 
        

        myAccountBtn = tk.Button(master = shell, text = "My Account", command = lambda: showInstructor(Master=Master, accountID=accountID, admin = False))
        myAccountBtn.grid(row=6, column = 0, sticky = 'NSEW')




#TEST CODE -style code should be implemented sta start of main script so all code runs correctly (specifcally the calendar UI)
#window = tk.Tk()
#window.minsize(500,500)
#shell = tk.Frame()
##style = ttk.Style(window)
#style.theme_use('alt')
#showCustomer(shell, 1, False)
#accountsMenu(shell, 1) #customer test
#accountsMenu(window, 11) # non admin staff test
#accountsMenu(window, 15) # admin test
#window.mainloop()
