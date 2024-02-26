import tkinter as tk
import accountsBackend as backend
import membershipsBackend as memberships
import datetime
from dateutil import relativedelta
from tkinter import messagebox
import tkcalendar
from tkinter import ttk


def changeEmail(customerID, staff):
    popUp = tk.Toplevel()
    popUp.title("Change Email")
    
    popUp.columnconfigure(0, weight=4)
    popUp.columnconfigure(1, weight = 7)

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


    popUp.mainloop()



def changePassword(accountID, staff):
    username = backend.getUsername(accountID)
    
    popUp = tk.Toplevel()
    popUp.title("Change Password")
    
    popUp.columnconfigure(0, weight=4)
    popUp.columnconfigure(1, weight = 7)

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


    popUp.mainloop()



def showCustomer(Master, accountID, staff):
    #Create frame and get details
    global shell
    #shell.destroy()
    shell = tk.Frame(master = Master)
    shell.pack(expand=True, fill='both')

    try:
        details = backend.getCustomer(accountID = accountID)[0]
    except IndexError:
        return 'CustomerDoesNotExist'

    #find age
    dob = datetime.datetime.strptime(details[5], '%Y-%m-%d').replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    now = datetime.datetime.now().replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    age = relativedelta.relativedelta(now, dob).years
    print(age)

    shell.columnconfigure(0, weight = 2)

    nameLabel = tk.Label(master = shell, text = details[3]+", "+details[2]+", "+str(age)+"yrs", font = ('Arial Bold', 20))
    nameLabel.grid(row = 0, column = 0, columnspan=2, sticky='W', pady=5, padx= 10)

    emailLabel = tk.Label(master = shell, text = "Email: "+details[4], font = ('Arial', 16))
    emailLabel.grid(row = 1, column = 0, sticky = 'W', padx = 15)

    changeEmailBtn = tk.Button(master = shell, text = 'Change', command=lambda: changeEmail(customerID=details[0], staff = staff))
    changeEmailBtn.grid(row = 1, column = 1)
    #TODO - pop up box for email change

    currentMembership = memberships.getMembershipRecord(customerID=details[0], ACTIVE=True)
    try:
        membershipDetails = memberships.getMemberships(membershipID = currentMembership[1])[0]
    except IndexError:
        membershipDetails = [None, 'None']
    membershipLabel = tk.Label(master = shell, text = 'Membership: '+ membershipDetails[1], font = ('Arial', 16))
    membershipLabel.grid(row = 2, column = 0, columnspan=2, sticky = 'W', padx =15)

    changePasswordBtn = tk.Button(master = shell, text = 'Change Password', command = lambda: changePassword(accountID, staff))
    changePasswordBtn.grid(row = 3, column = 0, columnspan = 2, sticky = 'W', padx = 10)



def addCustomer(Master):
    global shell
    shell.destroy()
    shell = tk.Frame(master = Master)
    shell.pack(expand=True, fill='both')

    shell.columnconfigure(0, weight=3)
    shell.columnconfigure(1, weight =7)

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
    dobDropDown = tkcalendar.DateEntry(master=shell, maxdate = datetime.date.today())
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

    password2Label = tk.Label(master = shell, text = 'Confirm Password', font=("Arial", 16))
    password2Label.grid(row = 8, column = 0, sticky='W', pady=5, padx= 15)
    password2 = tk.StringVar()
    password2Box = tk.Entry(master = shell, textvariable=password2, show='*')
    password2Box.grid(row = 8, column = 1, padx= 10)

    safetyBrief = tk.IntVar()
    safetyBriefBox = tk.Checkbutton(master = shell, text = 'Customer has completed safety briefing and signed waiver.', variable = safetyBrief, onvalue=1, offvalue=0, font=("Arial", 16))
    safetyBriefBox.grid(row = 9, column = 0, columnspan=2, sticky = 'W', padx = 15, pady = 5)

    def addCustomerAction():
        if fname.get() != '' and sname.get() != '':
            pass
        #NEED tp add this function, fix invisible date box, make entry boxes expand

    addCustomerBtn = tk.Button(master = shell, text = 'Add Customer', command = addCustomerAction)
    addCustomerBtn.grid(row = 10, column = 0, columnspan=2, sticky = 'NSEW', pady = 10)


#MAIN MENU for CUSTOMER MANAGEMENT
def customerMenu(Master, accountID):
    if backend.getPermissions(accountID) == 1:
        showCustomer(Master, backend.getCustomer(accountID=accountID)[0][1], False)

    else:
        global shell
        shell.destroy()
        shell = tk.Frame(master = Master)
        shell.pack(expand=True, fill='both')

        accountsTitle = tk.Label(master = shell, text = "Accounts", font=("Arial Bold", 20))
        accountsTitle.grid(row = 0)
        
        addCustomerBtn = tk.Button(master = shell, text = "Add Customer", command= lambda: addCustomer(Master=Master))
        addCustomerBtn.grid(row = 1)

        searchCustomerBtn = tk.Button(master = shell, text = "Search Customers")
        searchCustomerBtn.grid(row=2)

        viewCustomerBtn = tk.Button(master = shell, text = "View Customers")
        viewCustomerBtn.grid(row =3 )

        if backend.getPermissions(accountID) == 1:
            pass

        else:
            myAccountBtn = tk.Label()




#TEST CODE -style code should be implemented sta start of main script so all code runs correctly (specifcally the calendar UI)
window = tk.Tk()
shell = tk.Frame()
style = ttk.Style(window)
style.theme_use('alt')
#customerMenu(window, 1)
customerMenu(window, 15)
window.mainloop()
