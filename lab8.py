#lab8: Write a program (lab8setup.py) that downloads the data of all 93 countries and save it in an SQL database and a JSON file, 
#      then write a second program (lab8.py) that uses the database and JSON file to let the user look up information.
#Name: Quynh Nguyen
#Date: 3/12/18

from collections import defaultdict, namedtuple
import re
import time
import json
import sqlite3

def countrySearch():
    '''Function searches for country names with a starting letter
    '''
    with open('countryDict.json', 'r') as fh:
        countryDict = json.load(fh)  
    invalid = True # flag for invalid input                
    while invalid:
        try:
            letter = input("Enter the first letter of country name: ").upper()            
            if not letter.isalpha() :
                raise ValueError("=> Invalid letter of the alphabet")
            if letter not in countryDict : 
                raise ValueError("=> No country name matching the letter")
            
            #print the list of countries starting with the letter
            print("Country names starting with %s: " %letter)
            for i,country in enumerate(countryDict[letter]) :                
                print("\t%d: %s" %(i+1, country))
            
            invalid = True # flag for invalid input            
            while (invalid) : # re-prompt when invalid input
                option = input("\nType in a number: ")
                if not (option.isdigit() and 1 <= int(option) <= len(countryDict[letter])):
                    print("=> Invalid number chosen from the country list")
                else:
                    countryName = countryDict[letter][int(option) - 1]
                    conn = sqlite3.connect('CountryInfo.db')
                    cur = conn.cursor()
                    cur.execute("SELECT totalAthletes FROM CountryDB WHERE name = ?", (countryName,))
                    print("%d athletes for %s." %(cur.fetchone()[0], countryName))
                    conn.close()    # close connection  
                    invalid = False
        except ValueError as e:
            print(e)


def sportSearch() :
    '''Function searches for the countries participate in a sport
    '''
    conn = sqlite3.connect('CountryInfo.db')
    cur = conn.cursor()   
    print('Sports: ' + ', '.join('%s' %sport for sport in sorted(cur.execute("SELECT sport FROM Sports")))) 
    sport = input("Enter sport name: ").title()
    print('Countries participating in %s:' %sport)
    condition = ''
    for i in range(1,16):
        condition += re.sub('\d', str(i), 'CountryDB.sport_id1 = Sports.id') + ' OR '
    command = 'SELECT CountryDB.name FROM CountryDB JOIN Sports ON ('+ condition.strip(' OR ') +') AND Sports.sport = ?'
    cur.execute(command, (sport,)) 
    results = cur.fetchall()
    # display the list of results or "Not found" if not found
    print('\n'.join('%s' %country for country in sorted(results))) if results else print("Not found")
    conn.close()     # close connection  
    
        
def totalAthletesSearch() :
    '''Function searches for countries that have the total athletes between min and max
    '''
    invalid = True
    while invalid:
        try :
            range_= input('Enter min, max number of athletes: ').split(',')
            if len(range_) != 2 : # if user not entering 2 values
                raise ValueError("Input has to be 2 numbers separated by ','")
            (min_, max_) = tuple(map(int, range_))  # convert to int, ValueError raised by the system
            if min_ > max_: (min_, max_) = (max_, min_) # swap the 2 values if min > max
            print('Countries with %d to %d athletes:' %(min_, max_))
            # open connection to database
            conn = sqlite3.connect('CountryInfo.db')
            cur = conn.cursor()              
            cur.execute('SELECT CountryDB.name from CountryDB WHERE totalAthletes BETWEEN ? AND ? ORDER BY name', (min_, max_)) 
            results = cur.fetchall()
            # display the list of results or "Not found" if not found
            print('\n'.join('%s' %country for country in results)) if results else print("Not found")  
            conn.close()   # close connection
            invalid = False
        except ValueError as e:
            print('=> ValueError: '+ str(e))
        
        
def printMenu() :
    print('''\n***************************** MENU ******************************
    1. Displaying number of athletes for one country
    2. Displaying all countries that participated in one sport
    3. Displaying countries with certain number of athletes
    0. Exit
*****************************************************************\n''')    

def main() :
    option = '1'
    while option != 0:
        printMenu()
        try :
            option = int(input('Enter an option or 0 to exit: '))
            if not 0 <= option <= 3 : raise ValueError
            if option == 1: countrySearch()
            elif option == 2: sportSearch()
            elif option == 3: totalAthletesSearch()
            else : print('\nExiting...\nThank you for using the program!')
        except ValueError as e:
            print('=> Please enter a number from 0 to 3')
            
main()