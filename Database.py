# a user-created video game database that allows the user to add and remove games from the database, as well as search
#   their database by a variety of parameters
#
# by Matthew Ridderikhoff, created 06/08/2016

import sqlite3

class Database:
    def __init__(self, dbName, tableName, invalidResponse):
        self.dbName = dbName + ".db"  # name of the database
        self.tableName = tableName  # name of the table where the data is stored
        self.invalidResponse = invalidResponse  # error message when response is not one of the options

        # create connection to database
        self.conn = sqlite3.connect(self.dbName)

        # create cursor to execute SQLite commands
        self.c = self.conn.cursor()

        # create new table (if it already doesn't exist) with rows: id, name, console, and ESRB rating
        self.c.execute('CREATE TABLE IF NOT EXISTS ' +
                       self.tableName + '(id INTEGER, name TEXT, console TEXT, esrbRating TEXT)')

    # main menu:
    # states user options and gets selection from user
    # - if the user makes a valid selection, send the user to that menu/exits program
    # - if the user makes an invalid selection, repeat the main menu and get another input
    def mainMenu(self):
        print('Choose one of the following:')
        print('1 - add/remove game(s)')
        print('2 - search your game database')
        print('3 - exit myGameDatabase')
        print('')

        response = self.getSelection()  # get user selection

        if response == '1':
            self.addOrRemoveMenu()  # sends user to add/remove menu

        elif response == '2':
            self.searchMenu()  # sends user to search menu

        elif response == '3':
            print('Goodbye')  # exits myGameDatabase
            self.conn.commit()
            self.conn.close()

        else:
            print(self.invalidResponse)  # restart mainMenu() because of the invalid response
            self.mainMenu()

    # add/remove menu:
    # presents selections, either:
    # - add a game from the database
    # - remove a game from the database
    # - return to the main menu
    def addOrRemoveMenu(self):
        print('Would you like to:')
        print('1 - add a game to your collection')
        print('2 - remove a game from your collection')
        print('3 - return to the main menu')
        print('')

        response = self.getSelection()

        if response == '1':
            self.addGame()

        elif response == '2':
            self.removeGame()  # send user to removeGame

        elif response == '3':
            self.mainMenu()  # send user to main menu

        else:
            print(self.invalidResponse)  # restart addOrRemove() because of an invalid response
            self.addOrRemoveMenu()

    # creates a new game in the database, unless the name of the game the user is trying to add is already in the database
    def addGame(self):
        print("What is the name of the game you'd like to add?")
        nameResponse = input()

        duplicate = self.isGameInDatabase(nameResponse)  # check if the name given is already  listed in the database

        # perform action based on whether or not a duplicate was entered
        if duplicate:
            print('That game is already in your database')
            self.addOrRemoveMenu()
        else:
            print('What console is ' + nameResponse + ' on?')
            consoleResponse = self.pickConsole(nameResponse)

            print("What is the ESRB rating of " + nameResponse + "?")
            esrbRatingResponse = self.pickESRB(nameResponse)

            gameSQLCOde = self.addGameSQLCode(nameResponse, consoleResponse,
                                              esrbRatingResponse)  # compile responses into SQLite

            self.c.execute(gameSQLCOde)  # add game to database
            print(nameResponse + " has been added to your database")

            self.addOrRemoveMenu()

    # helper function to ensure the user only inputs supported consoles
    def pickConsole(self, nameResponse):
        print('1 - Xbox One, 2 - Playstation 4, 3 - WiiU')

        invalidResponse = True

        while invalidResponse:
            response = input()

            if response == '1':
                invalidResponse = False
                return 'XONE'
            elif response == '2':
                invalidResponse = False
                return 'PS4'
            elif response == '3':
                invalidResponse = False
                return 'WiiU'

            # will only execute if the user inputs an invalid response, asks the question again
            print(self.invalidResponse)
            print('What console is ' + nameResponse + ' on?')
            print('1 - Xbox One, 2 - Playstation 4, 3 - WiiU')


    # helper function to ensure the user only inputs supported ESRB ratings
    def pickESRB(self, nameResponse):
        print('1 - E10+ for Everyone 10 and up, 2 - T for Teen, 3 - M for Mature')

        invalidResponse = True

        while invalidResponse:
            response = input()

            if response == '1':
                invalidResponse = False
                return 'E10+'
            elif response == '2':
                invalidResponse = False
                return 'T'
            elif response == '3':
                invalidResponse = False
                return 'M'

            print(self.invalidResponse)
            print("What is the ESRB rating of " + nameResponse + "?")
            print('1 - E10+ for Everyone 10 and up, 2 - T for Teen, 3 - M for Mature')


    # helper function to create the SQLite code string we will pass to add a game
    def addGameSQLCode(self, name, console, esrbRating):
        return "INSERT INTO " + self.tableName + " VALUES(" + str(
            self.getLowestAvailableId()) + ", '" + name + "', '" + console + "', '" + esrbRating + "')"

    # helper function that returns the lowest available Id
    # NOTE: it does NOT account for Ids that were once assigned, but who's game has been removed
    def getLowestAvailableId(self):
        self.c.execute("SELECT id FROM " + self.tableName)  # get all used Ids

        ids = self.c.fetchall()
        num = 0

        for n in ids:
            intValue = n[0]  # retrieve the single int from the tuple (should never have more than 1 item)
            if intValue > num:
                num = intValue

        return num + 1

    # helper function that checks to see if a given name is in the database
    def isGameInDatabase(self, gameName):
        inDB = False

        self.c.execute('SELECT name FROM ' + self.tableName)
        allGameNames = self.c.fetchall()
        for name in allGameNames:
            nameString = name[0]  # retrieve the single string from the tuple (should never have more than 1 item)
            if nameString == gameName:
                inDB = True

        return inDB

    # removes a game from the database, if that game is in the database
    def removeGame(self):
        print("What game would you like to remove?")
        nameResponse = input()

        # checks to see if the name is actually in the database
        canRemove = self.isGameInDatabase(nameResponse)

        if canRemove:
            self.c.execute('DELETE FROM ' + self.tableName + ' WHERE name = "' + nameResponse + '"')

            print(nameResponse + " has been successfully removed")
            self.addOrRemoveMenu()
        else:
            print("That game is not in your database")
            self.addOrRemoveMenu()

    # search menu:
    # allows the user to search the database by any row
    # - except for the id row, which not be seen by the user todo user can see it currently
    def searchMenu(self):
        print('How would you like to search?')
        print('1 - by name')
        print('2 - by console')
        print('3 - by ESRB rating')
        print('4 - return to main menu')
        print('')

        response = self.getSelection()

        if response == '1':
            self.searchByName()
        elif response == '2':
            self.searchByConsole()
        elif response == '3':
            self.searchByESRB()
        elif response == '4':
            self.mainMenu()  # return to main menu
        else:
            print(self.invalidResponse)  # ask again
            self.searchMenu()

    # performs search by name, letting the user search for one game, a series, or  see their database organized by name
    def searchByName(self):
        print('Do you want to search for:')
        print('1 - a single game')
        print('2 - a series of games')
        print('3 - all your games organized alphabetically')

        response = self.getSelection()

        if response == '1':
            print('What is the name of the game?')
            name = input()

            validName = self.isGameInDatabase(name)  # check if game is in the database

            if validName:
                self.c.execute('SELECT * FROM ' + self.tableName + ' WHERE name = "' + name + '"')
                self.printSearchResults(self.c.fetchall())
            else:
                print("That game is not in your database")

        elif response == '2':
            print("What is the name of the series?")
            name = input()

            self.c.execute('SELECT * FROM ' + self.tableName + ' WHERE name like "' + name + '%"')
            self.printSearchResults(self.c.fetchall())

        elif response == '3':
            self.c.execute('SELECT * FROM ' + self.tableName + ' ORDER BY name ASC')
            self.printSearchResults(self.c.fetchall())

        else:
            print(self.invalidResponse)
            self.searchByName()

        self.mainMenu()

    # performs search by console (PS4, XONE, WiiU)
    def searchByConsole(self):
        print('Do you want to see games on the console')
        print('1 - Playstation 4')
        print('2 - Xbox One')
        print('3 - WiiU')

        response = self.getSelection()

        if response == '1':
            self.c.execute(self.createSearchSQL('console', 'PS4'))
            self.printSearchResults(self.c.fetchall())
        elif response == '2':
            self.c.execute(self.createSearchSQL('console', 'XONE'))
            self.printSearchResults(self.c.fetchall())
        elif response == '3':
            self.c.execute(self.createSearchSQL('console', 'WiiU'))
            self.printSearchResults(self.c.fetchall())
        else:
            print(self.invalidResponse)
            self.searchByConsole()

        self.mainMenu()

    # performs search by ESRB rating (E10+, T, M)
    def searchByESRB(self):
        print('Do you want to see games with an ESRB rating of:')
        print('1 - E10+')
        print('2 - T')
        print('3 - M')

        response = self.getSelection()

        if response == '1':
            self.c.execute(self.createSearchSQL('esrbRating', 'E10+'))
            self.printSearchResults(self.c.fetchall())
        elif response == '2':
            self.c.execute(self.createSearchSQL('esrbRating', 'T'))
            self.printSearchResults(self.c.fetchall())
        elif response == '3':
            self.c.execute(self.createSearchSQL('esrbRating', 'M'))
            self.printSearchResults(self.c.fetchall())
        else:
            print(self.invalidResponse)
            self.searchByESRB()

        self.mainMenu()

    # helper function that compiles the search parameters into SQLite code
    def createSearchSQL(self, category, searchParameter):

        return 'SELECT * FROM ' + self.tableName + ' WHERE "' + category + '" = "' + searchParameter + '"'

    # helper function that gets input from user and returns it
    def getSelection(self):
        print('Your Selection:')
        response = input()
        return response

    # helper function that displays all search results in a user-friendly way
    def printSearchResults(self, results):
        print('')

        for game in results:
            name = game[1]  # index 1 will always have the name (index 0 has the id)
            console = game[2]  # index 2 will always be the game's console
            esrb = game[3]  # index 3 will always be the game's ESRB rating
            print(name + ' : ' + console + ' : ' + esrb)

        print('')


# creates a new database with the given parameters, and sends the user to the main menu, which runs the application
db = Database("myGameDatabase", "tableName", "Invalid Response")
db.mainMenu()
