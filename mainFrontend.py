import tkinter as tk
import classesFrontend as classesUI
import accountsFrontend as accountsUI
import accountsBackend as accounts
from tkinter import ttk
from tkinter import messagebox


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
    


def guiMain(accountID):
    window = tk.Tk()
    window.title("Boulders Climbing Centre")

    window.grid_rowconfigure(0, weight = 1)
    window.grid_rowconfigure(1, weight = 5)

    window.grid_columnconfigure(0, weight =1 )

    style = ttk.Style(window)
    style.theme_use('alt') 

    window.minsize(350, 425)

    menuBar = tk.Frame(master = window, background = 'Red', relief='raised', borderwidth=3)
    menuBar.grid(row = 0, column = 0, sticky = 'NSEW')

    menuBar.grid_columnconfigure(0, weight = 1)
    menuBar.grid_columnconfigure(1, weight = 3)
    menuBar.grid_columnconfigure(2, weight = 1)
    menuBar.grid_rowconfigure(0, weight = 1)

    title = tk.Label(master = menuBar, text = 'Boulders', font = ('Arial Bold', 50), background='Red', foreground='white')
    title.grid(row = 0, column = 1)

    home = tk.PhotoImage(file = 'home.png')
    homeSmall = home.subsample(12,12)
    homeButton = tk.Button(master = menuBar, image = homeSmall, command = lambda: mainMenu(body, accountID))
    homeButton.grid(row = 0, column = 0, padx = 5)

    exitImg = tk.PhotoImage(file = 'exit.png')
    exitImgSmall = exitImg.subsample(7,7)
    exitButton = tk.Button(master = menuBar, image = exitImgSmall, command = exit)
    exitButton.grid(row = 0, column = 2, padx = 5)

    body = tk.Frame(master= window)
    body.grid(row = 1, column = 0, sticky = 'nsew')

    mainMenu(body, accountID)

    window.mainloop()




def mainMenu(Master, accountID):
    resetGuiShell(Master)

    shell.grid_rowconfigure(0, weight = 1)
    shell.grid_rowconfigure(1, weight = 1)
    shell.grid_rowconfigure(2, weight = 1)
    shell.grid_columnconfigure(0, weight = 1)

    classesBtn = tk.Button(master=shell, text='Classes', command = lambda: classesUI.classesMenu(Master, accountID))
    classesBtn.grid(row = 0, column = 0, sticky = 'NSEW', padx = 5, pady = 5)

    accountsTxt = 'My Account' if accounts.getPermissions(accountID)==1 else 'Accounts'
    accountsBtn = tk.Button(master = shell, text = accountsTxt, command = lambda: accountsUI.accountsMenu(Master, accountID))
    accountsBtn.grid(row = 1, column = 0, sticky = 'NSEW', padx = 5, pady = 5)

    signOutBtn = tk.Button(master = shell, text = 'Log Out', command = lambda: login(Master=Master))
    signOutBtn.grid(row = 2, column = 0, sticky = 'NSEW', padx = 5, pady = 5)




def login(Master = None):
    if Master!=None:
        Master.master.destroy()

    
    loginWindow = tk.Tk()
    loginWindow.title('Boulders Login')

    loginWindow.grid_rowconfigure(0, weight = 3)
    loginWindow.grid_rowconfigure(1, weight = 2)
    loginWindow.grid_rowconfigure(2, weight = 2)
    loginWindow.grid_rowconfigure(3, weight = 3)

    loginWindow.grid_columnconfigure(0, weight = 5)
    loginWindow.grid_columnconfigure(1, weight = 7)

    titleLabel = tk.Label(master = loginWindow, text = 'Login', font = ('Arial Bold', 20))
    titleLabel.grid(row = 0, column = 0, columnspan=2, sticky = 'NSW', padx = 15, pady = 5)

    usernameLabel = tk.Label(master = loginWindow, text = 'Username', font = ('Arial', 14))
    usernameLabel.grid(row = 1, column = 0, sticky='W', pady=5, padx= 10)
    username = tk.StringVar()
    usernameBox = tk.Entry(master = loginWindow, textvariable=username)
    usernameBox.grid(row = 1, column = 1, padx= 10)

    passwordLabel = tk.Label(master = loginWindow, text = 'Password', font = ('Arial', 14))
    passwordLabel.grid(row = 2, column = 0, sticky='W', pady=5, padx= 10)
    password = tk.StringVar()
    passwordBox = tk.Entry(master = loginWindow, textvariable=password, show='*')
    passwordBox.grid(row = 2, column = 1, padx= 10)

    def tryLogin():
        login = accounts.login(username.get(), password.get())
        if login[:8]=='LoggedIn':
            loginWindow.destroy()
            guiMain(accountID = int(login[8:]))
        else:
            messagebox.showerror('Login Error', 'Username or Password is incorrect')
            return

    loginBtn = tk.Button(master = loginWindow, text = "Login", command=tryLogin)
    loginBtn.grid(row = 3, column = 0, columnspan = 2, sticky = 'NSEW', padx = 5, pady = 5)

    
    loginWindow.mainloop()



login()