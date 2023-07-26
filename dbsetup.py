import sqlite3
import os


def initdb(path="main.db"):

    conn = sqlite3.connect("main.db")
    c = conn.cursor()


    #Create accounts table
    #Check permissions in range 1-3
    #Autoincrementing accountID
    c.execute("""CREATE TABLE IF NOT EXISTS Accounts (
            accountID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(50) NOT NULL UNIQUE,
            permissions INTEGER NOT NULL DEFAULT 1
                            CHECK(permissions >=1)
                            CHECK(permissions <=3)
            )""")


    #Create instructors table
    #Check email is in correct format (very rudimentary - should improve in application)
    #(% is any no of chars, _ is a single char)
    #pay field is a floating point integer checked to 2 dp
    #accountID references Accounts table
    c.execute("""CREATE TABLE IF NOT EXISTS Instructors (
            instructorID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            accountID INTEGER NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(254) NOT NULL UNIQUE
                            CHECK(email LIKE '%_@__%.__%'),
            pay REAL NOT NULL
                            CHECK(pay = ROUND(pay,2)),
            DBSChecked INTEGER NOT NULL
                            CHECK(DBSChecked IS 0 OR
                                  DBSChecked IS 1),

            FOREIGN KEY (accountID) REFERENCES Accounts(accountID)
            )""")


    #Create customer table
    #Same rudimentary email checking as in Instructors table
    #Rudimentary error check for DOB even tho datetime.date SHOULD manage it
    c.execute("""CREATE TABLE IF NOT EXISTS Customers (
            customerID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            accountID INTEGER NOT NULL UNIQUE,
            fname VARCHAR(50) NOT NULL,
            sname VARCHAR(50) NOT NULL,
            email VARCHAR(254) NOT NULL,
            DOB VARCHAR(10) NOT NULL
                            CHECK(DOB LIKE '____-__-__'),

            FOREIGN KEY (accountID) REFERENCES Accounts(accountID)
            )""")


    #Create class types table
    #Check that upper  age limit is greater than lower age limit, or one is NULL
    #Check length is less than 24 hrs in minutes
    c.execute("""CREATE TABLE IF NOT EXISTS ClassTypes (
            classTypeID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            lowerAge INTEGER,
            upperAge INTEGER
                            CHECK(upperAge >= lowerAge OR
                                  upperAge IS NULL OR
                                  lowerAge IS NULL),
            description VARCHAR(500),
            capacity INTEGER,
            length INTEGER
                            CHECK(length <= 1440)

            )""")


    #Create classes table
    #rudimentary error checking for datetime field format
    c.execute("""CREATE TABLE IF NOT EXISTS Classes (
            classID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            classTypeID INTEGER NOT NULL,
            customName VARCHAR(50),
            dateTime VARCHAR(19)
                            CHECK(dateTime LIKE '____-__-__ __:__:__'),
                            
            FOREIGN KEY (classTypeID) REFERENCES ClassTypes(classTypeID)
            )""")


    #Create bookings table
    c.execute("""CREATE TABLE IF NOT EXISTS Bookings (
            bookingID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            classID INTEGER NOT NULL,
            customerID INTEGER NOT NULL,

            FOREIGN KEY (classID) REFERENCES Classes(classID),
            FOREIGN KEY (customerID) REFERENCES Customers(customerID)
            )""")


    #Create instructor allocation table
    c.execute("""CREATE TABLE IF NOT EXISTS InstructorAllocations (
            allocationID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            classID INTEGER NOT NULL,
            instructorID INTEGER NOT NULL,

            FOREIGN KEY (classID) REFERENCES Classes(classID),
            FOREIGN KEY (instructorID) REFERENCES Instructors(instructorID)
            )""")


    #Create memberships table
    #Free equip hire and allow peak are integers being used as booleans
    #duration (days) is less than a year
    #price must be 2dp
    c.execute("""CREATE TABLE IF NOT EXISTS Memberships (
            membershipID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            description VARCHAR(50) NOT NULL UNIQUE,
            noAdults INTEGER NOT NULL
                            CHECK(noAdults <=2),
            noKids INTEGER NOT NULL
                            CHECK(noKids <=4),
            allowPeak INTEGER NOT NULL
                            CHECK(allowPeak IS 1 OR allowPeak IS 0),
            freeEquipHire INTEGER NOT NULL
                            CHECK(freeEquipHire IS 1 or freeEquipHire IS 0),
            duration INTEGER NOT NULL
                            CHECK(duration <= 365),
            price REAL NOT NULL
                            CHECK(price = ROUND(price,2))            
            )""")


    #Create membership purchases table
    #Six slots for possible customers for family membership
    #Will use application to see how many can be filled
    c.execute("""CREATE TABLE IF NOT EXISTS MembershipPurchases (
            purchaseID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            membershipID INTEGER NOT NULL,
            startDate VARCHAR(10) NOT NULL
                            CHECK(startDate LIKE '____-__-__'),
            person1 INTEGER NOT NULL,
            person2 INTEGER,
            person3 INTEGER,
            person4 INTEGER,
            person5 INTEGER,
            person6 INTEGER,
            
            FOREIGN KEY (membershipID) REFERENCES Memberships(membershipID),
            FOREIGN KEY (person1) REFERENCES Customers(customerID),
            FOREIGN KEY (person2) REFERENCES Customers(customerID),
            FOREIGN KEY (person3) REFERENCES Customers(customerID),
            FOREIGN KEY (person4) REFERENCES Customers(customerID),
            FOREIGN KEY (person5) REFERENCES Customers(customerID),
            FOREIGN KEY (person6) REFERENCES Customers(customerID)
            )""")


    #Create EquipmentTypes table
    #hire price to 2dp
    c.execute("""CREATE TABLE IF NOT EXISTS EquipmentTypes (
            equipmentTypeID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL,
            lifetime INTEGER,
            hirePrice REAL NOT NULL
                            CHECK(hirePrice = ROUND(hirePrice,2))
            )""")

    
    #Create Equipment table
    c.execute("""CREATE TABLE IF NOT EXISTS Equipment (
            equipmentItemID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            equipmentTypeID INTEGER NOT NULL,
            size VARCHAR(16),
            currentCustomer INTEGER,
            hoursUsed INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (equipmentTypeID) REFERENCES EquipmentTypes(equipmentTypeID),
            FOREIGN KEY (currentCustomer) REFERENCES Customers(customerID)
            )""")
        
    
    conn.commit()
    conn.close()
    print("Created database successfully!")



def removedb(path="main.db"):
    try:
        os.remove(path)
        print("Deleted file at '" + path + "'")
    except FileNotFoundError:
        print("No database to delete")



def demodb():
    removedb()
    initdb()

    conn = sqlite3.connect("main.db")
    c = conn.cursor()

    #Fill accounts data
    c.execute("""INSERT INTO Accounts (username, password, permissions) VALUES
                ('Thercull', 'Joophong3', 1),
                ('Yousiolind03', 'Uu7aiPhoovo', 1)
                """)

    #Fill customers data
    c.execute("""INSERT INTO Customers (accountID, fname, sname, email, DOB) VALUES
                (1, 'Andre', 'Kerstetter', 'AndreSKerstetter@dayrep.com', '2001-03-21'),
                (2, 'Declan', 'Gray', 'DeclanGray@rhyta.com', '2003-08-13')
                """)
    
    conn.commit()
    conn.close()

    print("Added demo data")


demodb()
