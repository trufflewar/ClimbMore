import sqlite3
import os
import datetime


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
    c.execute("""CREATE TABLE IF NOT EXISTS InstructorAssignments (
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
            description VARCHAR(50) NOT NULL,
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
    c.execute("""CREATE TABLE IF NOT EXISTS MembershipRecords (
            purchaseID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            membershipID INTEGER NOT NULL,
            startDate VARCHAR(10) NOT NULL
                            CHECK(startDate LIKE '____-__-__'),
            adult1 INTEGER,
            adult2 INTEGER,
            kid1 INTEGER,
            kid2 INTEGER,
            kid3 INTEGER,
            kid4 INTEGER,
            
            FOREIGN KEY (membershipID) REFERENCES Memberships(membershipID),
            FOREIGN KEY (adult1) REFERENCES Customers(customerID),
            FOREIGN KEY (adult2) REFERENCES Customers(customerID),
            FOREIGN KEY (kid1) REFERENCES Customers(customerID),
            FOREIGN KEY (kid2) REFERENCES Customers(customerID),
            FOREIGN KEY (kid3) REFERENCES Customers(customerID),
            FOREIGN KEY (kid4) REFERENCES Customers(customerID)
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
            
            FOREIGN KEY (equipmentTypeID) REFERENCES EquipmentTypes(equipmentTypeID)
            )""")


    #Create Rentals Table
    #start and end are datetime.datetime objects
    c.execute("""CREATE TABLE IF NOT EXISTS Rentals(
            rentalID INTEGER NOT NULL UNIQUE PRIMARY KEY,
            customerID INTEGER,
            equipmentItemID INTEGER,
            rentalStart VARCHAR(26),
            rentalEnd INTEGER,
            
            FOREIGN KEY(customerID) REFERENCES Customers(customer_id),
            FOREIGN KEY(equipmentItemID) REFERENCES Equipment(equipmentItemID))""")

    
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


    #Fill accounts table with demo data - have to use loop as SQLITE3 does not support adding multiple records in one go
    accounts = ["""('Thercull', 'Joophong3', 1)""",
                """('Yousiolind03', 'Uu7aiPhoovo', 1)""",
                """('Stilad', 'ou9ith9Eid', 1)""",
                """('Agrot1995', 'dooP1Looju', 1)""",
                """('Trugh1954', 'ienooZ1zo2ie', 1)""",
                """('Shime1983', 'ha3Nah2thah', 1)""",
                """('Lethemstes', 'ohwee2Du8ie', 1)""",
                """('Apocran', 'Doh9ootavoo', 1)""",
                """('Witicher', 'Vie8eechae', 1)""",
                """('Wastrid97', 'Aj7ahb6siet', 1)""",
                """('Illy1973', 'rai4edoVae', 2)""",
                """('Ladmis', 'oorasaBu4J', 2)""",
                """('Givell', 'Kahnoh8oh', 2)""",
                """('Evere1969', 'aiv7iSeeMae', 2)""",
                """('Dificen', 'koxah9Ci', 3)"""]
    for account in accounts:
        c.execute("""INSERT INTO Accounts (username, password, permissions) VALUES """ + account)
                

    #Fill customers table with demo data
    customers = ["""(1, 'Andre', 'Kerstetter', 'AndreSKerstetter@dayrep.com', '2001-03-21')""",
                """(2, 'Declan', 'Gray', 'DeclanGray@rhyta.com', '2003-08-13')""",
                """(3, 'Ewan', 'Chamberlain', 'EwanChamberlain@rhyta.com', '2013-02-27')""",
                """(4, 'Ryan', 'Bates', 'RyanBates@rhyta.com', '1976-05-25')""",
                """(5, 'Tegan', 'O''Connor', 'TeganOConnor@dayrep.com', '1972-05-18')""",
                """(6, 'Caitlin', 'Saunders', 'CaitlinSaunders@teleworm.us', '2009-12-14')""",
                """(7, 'Georgia', 'Humphreys', 'GeorgiaHumphreys@teleworm.us', '1988-06-04')""",
                """(8, 'Harrison', 'Barker', 'HarrisonBarker@jourrapide.com', '2008-01-29')""",
                """(9, 'Kiera', 'Burgess', 'KieraBurgess@armyspy.com', '1991-11-11')""",
                """(10, 'Lewis', 'Davis', 'LewisDavis@rhyta.com', '1961-03-26')"""]
    for customer in customers:
        c.execute("""INSERT INTO Customers (accountID, fname, sname, email, DOB) VALUES """ + customer)


    #Fill instructors table with demo data
    instructors = ["""(11, 'Alex Joyce', 'AlexJoyce@teleworm.us', 12.50, 1)""",
                   """(12, 'Morgan Mann', 'MorganMann@jourrapide.com', 10, 1)""",
                   """(13, 'Hayden Stewart', 'HaydenStewart@jourrapide.com', 8, 1)""",
                   """(14, 'Louis Heath', 'LouisHeath@rhyta.com', 8, 0)""",
                   """(15, 'Jessica Gregory', 'JessicaGregory@armyspy.com', 8, 0)"""]
    for instructor in instructors:
        c.execute("""INSERT INTO Instructors (accountID, name, email, pay, DBSChecked) VALUES """ + instructor)


    #Fill memberships table with demo data
    memberships = ["""('All-In-One (yearly)', 'This all-encompassing membership includes equipment hire and access at any time', 1, 0, 1, 1, 365, 450.00)""",
                   """('The Cheap One (monthly)', 'Our cheapest adult membership allows you off-peak access at a fraction of the cost of a full membership', 1, 0, 0, 0, 30, 30.00)""",
                   """('All-In-One (monthly)', 'This all-encompassing membership includes equipment hire and access at any time', 1, 0, 1, 1, 30, 50.00)""",
                   """('For the Normies', 'Just a standard monthly membership - no equipment hire included', 1, 0, 1, 0, 30, 40.00)""",
                   """('Basic Kids (yearly)', 'A basic kids membership with peak access and no equipment hire', 0, 1, 1, 0, 365, 35.00)""",
                   """('Family of Four (yearly)', '2 adults, 2 kids, peak access and equipment hire. Simple.', 2, 2, 1, 1, 365, 1400.00)"""]
    for membership in memberships:
        c.execute("""INSERT INTO Memberships (name, description, noAdults, noKids, allowPeak, freeEquipHire, duration, price) VALUES """ + membership)


    #Fill membershipspurchases table with demo data including randomised start dates
    today = datetime.datetime.now().date()
    purchases = [f"""(1, '{today - datetime.timedelta(days = 15)}', 1, NULL, NULL, NULL, NULL, NULL)""",
                 f"""(2, '{today - datetime.timedelta(days = 500)}', 1, NULL, NULL, NULL, NULL, NULL)""",
                 f"""(2, '{today - datetime.timedelta(days = 7)}', 2, NULL, NULL, NULL, NULL, NULL)""",
                 f"""(5, '{today - datetime.timedelta(days = 75)}', NULL, NULL, 3, NULL, NULL, NULL)""",
                 f"""(4, '{today - datetime.timedelta(days = 130)}', 4, NULL, NULL, NULL, NULL, NULL)""",
                 f"""(3, '{today - datetime.timedelta(days = 3)}', 5, NULL, NULL, NULL, NULL, NULL)""",
                 f"""(6, '{today - datetime.timedelta(days = 17)}', 7, 10, 6, 8 , NULL, NULL)"""]
    for purchase in purchases:
        c.execute("""INSERT INTO MembershipRecords (membershipID, startDate, adult1, adult2, kid1, kid2, kid3, kid4) VALUES """ + purchase)


    #Fill equipment types table
    types = ["""('Harness 1', 1800, 4.00)""",
             """('Harness 2', 2000, 5.50)""",
             """('Basic Shoes', NULL, 3.00)""",
             """('Pro Shoes', NULL, 5.00)""",
             """('60m Rope', 1500, 15.00)"""]
    for etype in types:
        c.execute("""INSERT INTO EquipmentTypes (name, lifetime, hirePrice) VALUES """ + etype)


    #Fill equipment
    equipment = ["""(1, 'Male')""",
                """(1, 'Male')""",
                """(1, 'Male')""",
                """(1, 'Female')""",
                """(1, 'Female')""",
                """(1, 'Female')""",
                """(2, NULL)""",
                """(2, NULL)""",
                """(2, NULL)""",
                """(2, NULL)""",
                """(2, NULL)""",
                """(3, '6')""",
                """(3, '6')""",
                """(3, '7')""",
                """(3, '7')""",
                """(3, '8')""",
                """(3, '8')""",
                """(3, '9')""",
                """(3, '9')""",
                """(3, '10')""",
                """(3, '10')""",
                """(3, '11')""",
                """(3, '12')""",
                """(3, '13')""",
                """(4, '7')""",
                """(4, '8')""",
                """(4, '9')""",
                """(4, '9')""",
                """(4, '10')""",
                """(4, '10')""",
                """(5, NULL)""",
                """(5, NULL)""",
                """(5, NULL)""",
                """(5, NULL)""",]
    for item in equipment:
        c.execute("""INSERT INTO Equipment (equipmentTypeID, size) VALUES """ + item)


    #Fill rentals
    now = datetime.datetime.now()
    rentals = [f"""(1, 21, '{now - datetime.timedelta(hours=3, minutes=37, seconds=48)}', '{now - datetime.timedelta(hours=1, minutes=22, seconds=35)}')""",
            f"""(2, 12, '{now - datetime.timedelta(hours=12, minutes=15, seconds=27)}', NULL)""",
            f"""(3, 7, '{now - datetime.timedelta(hours=27, minutes=42, seconds=52)}', '{now - datetime.timedelta(hours=10, minutes=5, seconds=46)}')""",
            f"""(4, 33, '{now - datetime.timedelta(hours=34, minutes=25, seconds=33)}', NULL)""",
            f"""(5, 27, '{now - datetime.timedelta(hours=18, minutes=32, seconds=59)}', '{now - datetime.timedelta(hours=4, minutes=11, seconds=23)}')""",
            f"""(6, 8, '{now - datetime.timedelta(hours=43, minutes=15, seconds=17)}', NULL)""",
            f"""(7, 16, '{now - datetime.timedelta(hours=38, minutes=52, seconds=51)}', '{now - datetime.timedelta(hours=9, minutes=45, seconds=37)}')""",
            f"""(8, 9, '{now - datetime.timedelta(hours=19, minutes=5, seconds=28)}', NULL)"""]
    for rental in rentals:
        c.execute("""INSERT INTO Rentals (customerID, equipmentItemID, rentalStart, rentalEnd) VALUES """ + rental)

    
    conn.commit()
    conn.close()

    print("Added demo data")


demodb()
