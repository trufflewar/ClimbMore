import datetime
import dbaccess as db
import datetime


# create a rental (hireout)
def createRental(customerID, equipmentItemID):
    now = datetime.datetime.now().replace(microsecond=0)
    now = str(now)
    db.executeSQL('INSERT INTO Rentals (customerID, equipmentItemID, rentalStart) VALUES (?,?,?)', (customerID, equipmentItemID, now))
    #TODO check that the item is not currently rented out


#search rentals
def getRental(rentalID = None, customerID = None, equipmentTypeID = None, date = None, lowerDate = None, upperDate = None):
    searchParams = locals()
    del searchParams[lowerDate]
    del searchParams[upperDate]

    #TODO: if date, and either lower or upper given, question it.....

    if type(searchParams[date])!=datetime.date and searchParams[date]!=None:
        return "dateMustBeDatetimeDateObject"

    #setup command
    command = 'SELECT * FROM Customers WHERE '
    values = []

    #add search terms
    for parameter in searchParams:
        if searchParams[parameter] != None:
            command = command + parameter + ' = ? AND '
            values.append(searchParams[parameter])

    #clean up and execute
    command = command[:(len(command)-4)]
    #print(command)
    results = db.executeSQL(command, tuple(values))
    
    if lowerDate!=None and type(lowerDate)!=datetime.date:
        return 'lowerDateMustBeNoneTypeOrDatetimeDate'
    if upperDate!=None and type(upperDate)!=datetime.date:
        return 'upperDateMustBeNoneTypeOrDatetimeDate'

    if lowerDate!=None:
        for rental in results:
            if rental[3]<lowerDate:
                results.remove(rental)
    
    if upperDate!=None:
        for rental in results:
            if rental[4]>upperDate:
                results.remove(rental)

    return results


#end a rental 
def endRental(rentalID):
    now = datetime.datetime.now().replace(microsecond=0)
    now = str(now)
    db.executeSQL('UPDATE Rentals SET rentalEnd = ? WHERE rentalID = ?', (now, rentalID))


#add an item of equipment
def addItem(equipmentTypeID, size = None):
    db.executeSQL('INSERT INTO Equipment(equipmentTypeID, size) VALUES (?,?)', (equipmentTypeID, size))


#remove an item of equipment
def removeItem():
    pass