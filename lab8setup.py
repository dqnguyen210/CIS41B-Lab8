#lab8: Write a program (lab8setup.py) that downloads the data of all 93 countries and save it in an SQL database and a JSON file, 
#      then write a second program (lab8.py) that uses the database and JSON file to let the user look up information.
#Name: Quynh Nguyen
#Date: 3/12/18

import requests
from bs4 import BeautifulSoup 
from collections import defaultdict, namedtuple
import re
import time
import json
import sqlite3

NUM_SPORTS = 15 

def getCountryList() :
    '''Fuction fetch data from the website and store country names in a dictionary, which is stored
       in a json file. Return a list of tuple (country name, url to the country info).
    '''
    try:
        page = requests.get("https://www.olympic.org/pyeongchang-2018/results/en/general/nocs-list.htm", timeout=3)
        page.raise_for_status()    # ask Requests to raise any exception 
        soup = BeautifulSoup(page.content, 'lxml')
        baseLink = "https://www.olympic.org/pyeongchang-2018/results/"
    
        countryDict = defaultdict(list)
        countryList = []
        Country = namedtuple('Country', 'name url')
        
        for country in soup.find_all('div', class_='CountriesListItem') :
            name = country.find('strong').get_text()
            url = re.sub('../../', baseLink, country.find('a').get('href'))
            countryList.append(Country(name, url))
            countryDict[name[0]].append(name)
            countryDict[name[0]].sort()
        # save dictionary to json file
        with open('countryDict.json', 'w') as fh:
            json.dump(countryDict, fh, indent=3)    
        return countryList
    
    except requests.exceptions.HTTPError as e: 
        print ("HTTP Error:", e) 
        raise SystemExit
    except requests.exceptions.ConnectionError as e: 
        print ("Error Connecting:", e) 
        raise SystemExit        
    except requests.exceptions.Timeout as e: 
        print ("Timeout Error:", e) 
        raise SystemExit        
    except requests.exceptions.RequestException as e:  # any Requests error
        print ("Request exception: ", e)
        raise SystemExit        
    

def createTables(cur):
    '''Create Sports table and CountryDB table
    '''
    # create new table Sports by removing old Sports table
    cur.execute("DROP TABLE IF EXISTS Sports")      
    cur.execute('''CREATE TABLE Sports(             
                       id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                       sport TEXT UNIQUE ON CONFLICT IGNORE)''')
    
    # create new table CountryDB by removing old CountryDB table
    cur.execute("DROP TABLE IF EXISTS CountryDB")      
    cur.execute('''CREATE TABLE CountryDB(             
                       name TEXT NOT NULL PRIMARY KEY UNIQUE,
                       totalAthletes INTEGER, 
                       sport_id1 INTEGER, sport_id2 INTEGER, sport_id3 INTEGER, 
                       sport_id4 INTEGER, sport_id5 INTEGER, sport_id6 INTEGER, 
                       sport_id7 INTEGER, sport_id8 INTEGER, sport_id9 INTEGER, 
                       sport_id10 INTEGER, sport_id11 INTEGER, sport_id12 INTEGER, 
                       sport_id13 INTEGER, sport_id14 INTEGER, sport_id15 INTEGER)''')    


def saveCountryInfo():
    '''Fetch data from the URL and save data to database
    '''    
    conn = sqlite3.connect('CountryInfo.db')
    cur = conn.cursor()
    createTables(cur)
    
    for i,country in enumerate(getCountryList()) :
        time.sleep(5)
        try :
            page = requests.get(country.url, timeout=3)
            soup = BeautifulSoup(page.content, 'lxml')
            table = soup.find('table', class_='ResTableFull')
            (totalAthletes, sport_IDs) = inspectTable(table, cur)
            #insert data to Countries table            
            cur.execute('''INSERT INTO CountryDB VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', tuple([country.name, totalAthletes] + sport_IDs))   
            
        except requests.exceptions.HTTPError as e: 
            print ("HTTP Error:", e) 
            raise SystemExit
        except requests.exceptions.ConnectionError as e: 
            print ("Error Connecting:", e) 
            raise SystemExit        
        except requests.exceptions.Timeout as e: 
            print ("Timeout Error:", e) 
            raise SystemExit        
        except requests.exceptions.RequestException as e:     # any Requests error
            print ("Request exception: ", e)
            raise SystemExit                     

    conn.commit()
    # close connection    
    conn.close()
                
    
def inspectTable(table, cur):
    '''Function inspects the table of information, saves the sports into Sports table
       Return the total atheles and the sport id list
    '''
    total = table.select('tr.MedalStd1 td.StyleCenter b')[0].get_text() #select returns a list of result
    sport_IDs = [None for i in range(NUM_SPORTS)]
    for i,sport in enumerate(table.find_all('tr', class_=re.compile('Res\d', re.I))) :
        #get the sport name
        sportname = sport.find('a').get_text() 
        #insert data to Sports table
        cur.execute('''INSERT INTO Sports (sport) VALUES (?)''', (sportname, )) #insert sport in Sports
        cur.execute('SELECT id FROM Sports WHERE sport = ? ', (sportname, )) #get id of that sport
        sport_IDs[i] = cur.fetchone()[0] #save that id in sport_IDs   

    return (total, sport_IDs)
    
saveCountryInfo()