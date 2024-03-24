import datetime
import dbaccess as db
import datetime
from accountsBackend import getAge


#search membership types
def getMemberships(membershipID = None, name = None, noAdults = None, noKids = None, freeEquipHire = None, duration = None, price = None):
    searchParams = locals()
    del searchParams['name']

    #setup command
    command = 'SELECT * FROM Memberships WHERE '
    values = []

    #add params
    for parameter in searchParams:
        if searchParams[parameter] != None:
            command = command + parameter + ' = ? AND '
            values.append(searchParams[parameter])

    #cleanup command
    command = command[:(len(command)-4)]

    #separate code for name as it does not require full name, just part
    if name != None:
        command = command + 'AND name LIKE ?'
        values.append('%' + name + '%')

    results = db.executeSQL(command, tuple(values))
    return results


#add membership type
def addMembership(name, description, noAdults, noKids, allowPeak, freeEquipHire, duration, price):
    db.executeSQL('INSERT INTO Memberships (name, description, noAdults, noKids, allowPeak, freeEquipHire, duration, price) VALUES (?,?,?,?,?,?,?,?)', (name, description, noAdults, noKids, allowPeak, freeEquipHire, duration, price))

    
#change membership price
def changeMembershipPrice(membershipID, price):
    db.executeSQL('UPDATE Memberships SET price = ? WHERE membershipID = ?', (price, membershipID))

   
#discontinue membership - set active flag field to 0
def discontinueMembership(membershipID):
    db.executeSQL('UPDATE Memberships SET active = 0 WHERE membershipID = ?', (membershipID,))


#add membership record
def buyMembership(membershipID, adult1 = None, adult2 = None, kid1 = None, kid2 = None, kid3 = None, kid4 = None):
    members = locals()
    today = datetime.datetime.now().replace(microsecond = 0, second = 0, minute = 0, hour = 0)

    del members['membershipID']

    #check is membership is available
    if db.executeSQL('SELECT active FROM Memberships WHERE membershipID = ?',(membershipID,))==0:
        return 'DiscontinuedMembership'

    #setup command
    command = 'INSERT INTO MembershipRecords (membershipID, startDate, '
    values = [membershipID, today.strftime('%Y-%m-%d')]
    count = 2

    #add params
    for member in members:
        if members[member] != None:
            if ('adult' in member and getAge(members[member]) >=18) or ('kid' in member and getAge(members[member]) <=17):
                command = command + member + ', '
                count += 1
                values.append(members[member])
            else:
                return 'AgeMismatch'

    #cleanup, configure and add ? tuple, execute
    command = command[:(len(command)-2)]
    command = command + ') VALUES (' + ' '.join(['?,' for x in range(count)])
    command = command[:(len(command)-1)] + ')'
    db.executeSQL(command, tuple(values))


#check active membership
def checkMember(membershipID):
    #get all memberships purchased
    records = db.executeSQL('SELECT membershipID, startDate FROM MembershipRecords WHERE (adult1 = ? OR adult2 = ? OR kid1 = ? OR kid2 = ? OR kid3 = ? OR kid4 = ?)', (membershipID, membershipID, membershipID, membershipID, membershipID, membershipID))
    today = datetime.datetime.now().replace(microsecond = 0, second = 0, minute = 0, hour = 0)

    #setup 
    for record in records:
        length = db.executeSQL('SELECT duration FROM Memberships WHERE membershipID = ?', (record[0],))
        length = length[0][0]

        #check for active memberships
        startDate = datetime.datetime.strptime(record[1], '%Y-%m-%d')
        endDate = startDate + datetime.timedelta(days = length)
        if endDate > today:
            return 'ActiveMembership'
        else:
            pass

    return 'NoActiveMembership'


#search membership records
#Should prob fix this as only searches specific fields but should really check if customerId in any fields
def getMembershipRecord(ACTIVE = None, purchaseID = None, membershipID = None, startDate = None, customerID = None):
    searchParams = locals()
    del searchParams['ACTIVE']
    del searchParams['customerID']

    results = []

    for field in ['adult1', 'adult2', 'kid1', 'kid2', 'kid3', 'kid4']:
        #setup command
        if customerID != None:  
            command = 'SELECT * FROM MembershipRecords WHERE ' + field + ' = ? AND '
            values = [customerID]

        else:
            command = 'SELECT * FROM MembershipRecords WHERE '
            values = []

        #add params
        for parameter in searchParams:
            if searchParams[parameter] != None:
                command = command + parameter + ' = ? AND '
                values.append(searchParams[parameter])

        #cleanup and execute
        command = command[:(len(command)-4)]
        results.extend(db.executeSQL(command, tuple(values)))


    #run check for active membershup if required
    if ACTIVE == None:
        return results

    elif ACTIVE == True or ACTIVE == False:
        if ACTIVE == True:
            ACTIVE = 1
        else:
            ACTIVE = 0

        today = datetime.datetime.now().replace(microsecond = 0, second = 0, minute = 0, hour = 0)
        
        for result in results:
            length = db.executeSQL('SELECT duration FROM Memberships WHERE membershipID = ?', (result[1],))
            length = length[0][0]

            startDate = datetime.datetime.strptime(result[2], '%Y-%m-%d')
            endDate = startDate + datetime.timedelta(days = length)
            if endDate < today:
                results.remove(result)

        #(results)
                   
    else:
        raise TypeError('ACTIVE flag should be Bool or None')
    
    return results



#TODO need to ensure that all get methods have a catch to remove the WHERE clause if no conditions are included - DONT THINK THIS IS Actually a problem lol
#see end of getClass for example
