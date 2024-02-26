import datetime
import dbaccess as db
import datetime
import re


#Add class type    
def addClassType(name, description = None, lowerAge = None, upperAge = None, capacity = None, noStaff = None, length = None, price = None):
    db.executeSQL('INSERT INTO ClassTypes (name, description, lowerAge, upperAge, capacity, noStaff, length, price) VALUES (?,?,?,?,?,?,?,?) ', (name, description, lowerAge, upperAge, capacity, noStaff, length, price))


#search class times
def getClassType(name = None, lowerAge = None, upperAge = None, capacity = None, noStaff = None, length = None, price = None):
    searchParams = locals()
    del searchParams['name']

    #setup command
    command = 'SELECT * FROM ClassTypes WHERE '
    values = []

    #add params
    for parameter in searchParams:
        if searchParams[parameter] != None:
            command = command + parameter + ' = ? AND '
            values.append(searchParams[parameter])

    #cleanup command
    if len(values) != 0:
        command = command[:(len(command)-4)]

    #separate code for name as it does not require full name, just part
    if name != None:
        if len(values)==0:
            command = command + ' name LIKE ?'
        else:
            command = command + ' AND name LIKE ?'
        values.append('%' + name + '%')

    print(command)
    results = db.executeSQL(command, tuple(values))
    return results


#delete a class type and convert to another
def removeClassType(classTypeID):
    # TODO: once make removeClass, getClass methods
    pass

#Don't know if there should ba an editClassType - may cause significant problems regarding capacity, staffing etc


#addClass instance
def addClass(classTypeID, dateTime, customName = None, instructors = []):
    if type(dateTime) is not datetime.datetime:
        return "Not Datetime Object"

    dateTime = dateTime.replace(microsecond = 0)

    #get number of staff need for class
    noStaff = (db.executeSQL('SELECT noStaff FROM ClassTypes WHERE classTypeID = ?', (classTypeID,)))[0][0]

    #check there is the correct number of instructors
    if len(instructors)!=noStaff:
        return "Instructor number mismatch"
    
    #check all instructors exist
    for instructor in instructors:
        if len(db.executeSQL('SELECT * FROM Instructors WHERE instructorID = ?', (instructor,))) != 1:
            return "Instructor " + instructor + " does not exist"

    #check for duplicates    
    instructorSet = set(instructors)
    if len(instructorSet) < len(instructors):
        return "Duplicate Instructors Found"
    
    #get classID
    classID = db.executeSQL("INSERT INTO Classes (classTypeID, dateTime, customName) VALUES (?, ?, ?)", (classTypeID, str(dateTime), customName), returnCursor=True)

    #add respective isntructor assignments
    for instructor in instructors:
        db.executeSQL("INSERT INTO InstructorAssignments (classID, instructorID) VALUES (?,?)", (classID, instructor))


#search classes
def getClass(classID = None, classTypeID = None, customName = None, date = None):
    
    #setup command
    command = 'SELECT * FROM Classes WHERE '
    values  = []

    #add conditions for classID and classtypeID
    if classID != None:
        command = command + 'classID = ? AND '
        values.append(classID)
    if classTypeID != None:
        command = command + 'classTypeID = ? AND '
        values.append(classTypeID)
    
    #add date condition
    if date != None:
        if type(date) != datetime.date:
            return "Need datetime.date object"
        else:
            command = command + 'dateTime LIKE ? AND '
            values.append(str(date) + '%')

    #add condition for name
    if customName != None:
        command = command + ' customName LIKE ?'
        values.append('%' + customName + '%')
    elif len(values)!=0:
        command = command[:len(command)-4]
    else:
        command = command[:len(command)-6]

    print(command)

    results = db.executeSQL(command, tuple(values))
    return results


#remove/cancel a class
def deleteClass(classID):
    #TODO, delete instructor assignments, bookings, send email
    db.executeSQL('DELETE FROM Classes WHERE classID = ?', (classID,))


#change a class time
def changeClassTime(classID, dateTime):
    #add date condition
    if type(dateTime) != datetime.datetime:
        return "Need datetime.date object"
    else:
        dateTime.replace(microseconds = 0)
        db.executeSQL('UPDATE Classes SET dateTime = ? WHERE classID = ?', (dateTime, classID))
    #TODO add email to inform customers


#add a booking
def addBooking(classID, customerID):
    #TODO add catching for overbooking and duplicate bookings
    db.executeSQL('INSERT INTO Bookings (classID, customerID) VALUES (?,?)', (classID, customerID))


#search bookings
def getBookings(classID = None, customerID = None):
    
    #setup command
    command = 'SELECT * FROM Bookings WHERE '
    values = []

    #add arguments
    if classID != None:
        command = command + 'classID = ? AND '
        values.append(classID)
    if customerID != None:
        command = command + 'customerID = ? AND '
        values.append(customerID)

    #cleanup
    if len(values)==0:
        command = command[:len(command)-6]
    else:
        command = command[:len(command)-4]

    #get and return results
    results = db.executeSQL(command, tuple(values))
    return results


#remove class booking
def removeBooking(bookingID):
    db.executeSQL('DELETE FROM Bookings WHERE bookingID = ?', (bookingID,))
    #TODO add email to customer to inform them


#get instructorAssignment
def getAssignment(classID = None, instructorID = None):

    #setup command
    command = 'SELECT * FROM InstructorAssignments WHERE '
    values = []

    #add arguments
    if classID != None:
        command = command + 'classID = ? AND '
        values.append(classID)
    if instructorID != None:
        command = command + 'instructorID = ? AND '
        values.append(instructorID)

    #cleanup
    if len(values)==0:
        command = command[:len(command)-6]
    else:
        command = command[:len(command)-4]

    #return results
    results = db.executeSQL(command, tuple(values))
    return results


#change instructors
def changeInstructor(classID, prevInstructor, newInstructor):
    #check if old instructor actually booked
    assignment = db.executeSQL('SELECT allocationID FROM InstructorAssignments WHERE classID = ? and instructorID = ?', (classID, prevInstructor))
    if len(assignment)==0:
        return "AssignmentDoesNotExist"
    
    #Update assignment
    db.executeSQL('UPDATE InstructorAssignments SET instructorID = ? WHERE allocationID = ?', (newInstructor, assignment[0][0]))
    #TODO Send email to instructor??

