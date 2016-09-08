# a user-created video game database that allows the user to add and remove games from the database, as well as search
#   their database by a variety of parameters
#
# by Matthew Ridderikhoff, created 06/08/2016

import sqlite3

# DATA DECLARATIONS
dbName = 'myGameCollection.db'  # name of the database
tableName = 'games'  # name of the table where the data is stored
invalidResponse = 'Invalid response'  # error message when response is not one of the options


# start up the database manager, send user to the main menu
# makes sure that if a database has been created earlier to not create another
def startUp():
    # checks to see if myGameDatabase has ever been run before
    #   (has a database already created instead of needing to make one)
    # - if not: create new database

    # create connection to database
    conn = sqlite3.connect(dbName)

    # create cursor to execute SQLite commands
    c = conn.cursor()

    # create new table (if it already doesn't exist) with rows: id, name, console, and ESRB rating
    c.execute('CREATE TABLE IF NOT EXISTS ' +
              tableName + '(id INTEGER, name TEXT, console TEXT, esrbRating TEXT)')

    print('Greetings')
    print('')

    mainMenu(c)

    # after user is done with the database, save and close the connect
    conn.commit()
    conn.close()


# main menu:
# states user options and gets selection from user
# - if the user makes a valid selection, send the user to that menu/exits program
# - if the user makes an invalid selection, repeat the main menu and get another input
def mainMenu(c):
    print('Choose one of the following:')
    print('1 - add/remove game(s)')
    print('2 - search your game database')
    print('3 - exit myGameDatabase')
    print('')

    response = getSelection()  # get user selection

    if response == '1':
        addOrRemoveMenu(c)  # sends user to add/remove menu

    elif response == '2':
        searchMenu(c)  # sends user to search menu

    elif response == '3':
        print('Goodbye')  # exits myGameDatabase

    else:
        print(invalidResponse)  # restart mainMenu() because of the invalid response
        mainMenu(c)


# add/remove menu:
# presents selections, either:
# - add a game from the database
# - remove a game from the database
# - return to the main menu
def addOrRemoveMenu(c):
    print('Would you like to:')
    print('1 - add a game to your collection')
    print('2 - remove a game from your collection')
    print('3 - return to the main menu')
    print('')

    response = getSelection()

    if response == '1':
        addGame(c)

    elif response == '2':
        removeGame(c)  # send user to removeGame

    elif response == '3':
        mainMenu(c)  # send user to main menu

    else:
        print(invalidResponse)  # restart addOrRemove() because of an invalid response
        addOrRemoveMenu(c)


# creates a new game in the database, unless the name of the game the user is trying to add is already in the database
def addGame(c):
    print("What is the name of the game you'd like to add?")
    nameResponse = input()

    duplicate = isGameInDatabase(c, nameResponse)  # check if the name given is already  listed in the database

    # perform action based on whether or not a duplicate was entered
    if duplicate:
        print('That game is already in your database')
        addOrRemoveMenu(c)
    else:
        print('What console is ' + nameResponse + ' on?')
        consoleResponse = pickConsole()

        print("What is the ESRB rating of " + nameResponse + "?")
        esrbRatingResponse = pickESRB()

        gameSQLCOde = addGameSQLCode(c, nameResponse, consoleResponse,
                                     esrbRatingResponse)  # compile responses into SQLite

        c.execute(gameSQLCOde)  # add game to database
        print(nameResponse + " has been added to your database")

        addOrRemoveMenu(c)


# helper function to ensure the user only inputs supported consoles
def pickConsole():
    print('1 - Xbox One, 2 - Playstation 4, 3 - WiiU')

    response = input()

    if response == '1':
        return 'XONE'
    elif response == '2':
        return 'PS4'
    elif response == '3':
        return 'WiiU'
    else:
        print(invalidResponse)
        pickConsole()

# helper function to ensure the user only inputs supported ESRB ratings
def pickESRB():
    print('1 - E10+ for Everyone 10 and up, 2 - T for Teen, 3 - M for Mature')

    response = input()

    if response == '1':
        return 'E10+'
    elif response == '2':
        return 'T'
    elif response == '3':
        return 'M'
    else:
        print(invalidResponse)
        pickESRB()

# helper function to create the SQLite code string we will pass to add a game
def addGameSQLCode(c, name, console, esrbRating):
    return "INSERT INTO " + tableName + " VALUES(" + str(
       getLowestAvailableId(c)) + ", '" + name + "', '" + console + "', '" + esrbRating + "')"


# helper function that returns the lowest available Id
# NOTE: it does NOT account for Ids that were once assigned, but who's game has been removed
def getLowestAvailableId(c):
    c.execute("SELECT id FROM " + tableName)  # get all used Ids

    ids = c.fetchall()
    num = 0

    for n in ids:
        intValue = n[0]  # retrieve the single int from the tuple (should never have more than 1 item)
        if intValue > num:
            num = intValue

    return num + 1


# helper function that checks to see if a given name is in the database
def isGameInDatabase(c, gameName):
    inDB = False

    c.execute('SELECT name FROM ' + tableName)
    allGameNames = c.fetchall()
    for name in allGameNames:
        nameString = name[0]  # retrieve the single string from the tuple (should never have more than 1 item)
        if nameString == gameName:
            inDB = True

    return inDB


# removes a game from the database, if that game is in the database
def removeGame(c):
    print("What game would you like to remove?")
    nameResponse = input()

    # checks to see if the name is actually in the database
    canRemove = isGameInDatabase(c, nameResponse)

    if canRemove:
        c.execute('DELETE FROM ' + tableName + ' WHERE name = "' + nameResponse + '"')

        print(nameResponse + " has been successfully removed")
        addOrRemoveMenu(c)
    else:
        print("That game is not in your database")
        addOrRemoveMenu(c)


# search menu:
# allows the user to search the database by any row
# - except for the id row, which not be seen by the user todo user can see it currently
def searchMenu(c):
    print('How would you like to search?')
    print('1 - by name')
    print('2 - by console')
    print('3 - by ESRB rating')
    print('4 - return to main menu')
    print('')

    response = getSelection()

    if response == '1':
        searchByName(c)
    elif response == '2':
        searchByConsole(c)
    elif response == '3':
        searchByESRB(c)
    elif response == '4':
        mainMenu()  # return to main menu
    else:
        print(invalidResponse)  # ask again
        searchMenu(c)


# performs search by name, letting the user search for one game, a series, or  see their database organized by name
def searchByName(c):
    print('Do you want to search for:')
    print('1 - a single game')
    print('2 - a series of games')
    print('3 - all your games organized alphabetically')

    response = getSelection()

    if response == '1':
        print('What is the name of the game?')
        name = input()

        validName = isGameInDatabase(c, name)  # check if game is in the database

        if validName:
            c.execute('SELECT * FROM ' + tableName + ' WHERE name = "' + name + '"')
            printSearchResults(c.fetchall())
        else:
            print("That game is not in your database")

    elif response == '2':
        print("What is the name of the series?")
        name = input()

        c.execute('SELECT * FROM ' + tableName + ' WHERE name like "' + name + '%"')
        printSearchResults(c.fetchall())

    elif response == '3':
        c.execute('SELECT * FROM ' + tableName + ' ORDER BY name ASC')
        printSearchResults(c.fetchall())

    else:
        print(invalidResponse)
        searchByName(c)

    mainMenu(c)

# performs search by console (PS4, XONE, WiiU)
def searchByConsole(c):
    print('Do you want to see games on the console')
    print('1 - Playstation 4')
    print('2 - Xbox One')
    print('3 - WiiU')

    response = getSelection()

    if response == '1':
        c.execute(createSearchSQL(c, 'console', 'PS4'))
        printSearchResults(c.fetchall())
    elif response == '2':
        c.execute(createSearchSQL(c, 'console', 'XONE'))
        printSearchResults(c.fetchall())
    elif response == '3':
        c.execute(createSearchSQL(c, 'console', 'WiiU'))
        printSearchResults(c.fetchall())
    else:
        print(invalidResponse)
        searchByConsole(c)

    mainMenu(c)


# performs search by ESRB rating (E10+, T, M)
def searchByESRB(c):
    print('Do you want to see games with an ESRB rating of:')
    print('1: E10+')
    print('2: T')
    print('3: M')

    response = getSelection()

    if response == '1':
        c.execute(createSearchSQL(c, 'esrbRating', 'E10+'))
        printSearchResults(c.fetchall())
    elif response == '2':
        c.execute(createSearchSQL(c, 'esrbRating', 'T'))
        printSearchResults(c.fetchall())
    elif response == '3':
        c.execute(createSearchSQL(c, 'esrbRating', 'M'))
        printSearchResults(c.fetchall())
    else:
        print(invalidResponse)
        searchByESRB(c)

    mainMenu(c)


# helper function that compiles the search parameters into SQLite code
def createSearchSQL(c, category, searchParameter):

    return 'SELECT * FROM ' + tableName + ' WHERE "' + category + '" = "' + searchParameter + '"'


# helper function that gets input from user and returns it
def getSelection():
    print('Your Selection:')
    response = input()
    return response


# helper function that displays all search results in a user-friendly way
def printSearchResults(results):
    print('')

    for game in results:
        name = game[1]  # index 1 will always have the name (index 0 has the id)
        console = game[2]  # index 2 will always be the game's console
        esrb = game[3]  # index 3 will always be the game's ESRB rating
        print(name + ' : ' + console + ' : ' + esrb)

    print('')

# PROGRAM
# calls startUp(), which starts the database
startUp()
