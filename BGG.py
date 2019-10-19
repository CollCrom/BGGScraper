import sys
sys.path.append(r"c:\users\ccromwell\appdata\local\programs\python\python37-32\lib\site-packages")
import requests
from bs4 import BeautifulSoup
import pickle
from time import sleep
import timeit
import csv

def request(msg, slp=1):
    '''A wrapper to make robust https requests.'''
    status_code = 500
    while status_code != 200:
        sleep(slp)
        try:
            r = requests.get(msg)
            status_code = r.status_code
            if status_code != 200:
                print("Server Error! Response Code %i. Retrying..." % (r.status_code))
        except:
            print("An exception has occurred, probably a momentory loss of connection. Waiting one seconds...")
            sleep(1)
    return r
    
min_nrate = 1e5
npage = 1
ids = []
while min_nrate > 100:
    # Get full HTML for a specific page in the full listing of boardgames sorted by 
    r = request("https://boardgamegeek.com/browse/boardgame/page/%i?sort=numvoters&sortdir=desc" % (npage,))
    soup = BeautifulSoup(r.text, "html.parser")    
    
    # Get rows for the table listing all the games on this page
    table = soup.find_all("tr", attrs={"id": "row_"})  # Get list of all the rows (tags) in the list of games on this page
    # Loop through each row and pull out the info for that game
    for idx, row in enumerate(table):
        # Row may or may not start with a "boardgame rank" link, if YES then strip it
        links = row.find_all("a")
        if "name" in links[0].attrs.keys():
            del links[0]
        gamelink = links[1]  # Get the relative URL for the specific game
        gameid = int(gamelink["href"].split("/")[2])  # Get the game ID by parsing the relative URL
        ids.append(gameid)
        ratings_str = row.find_all("td", attrs={"class": "collection_bggrating"})[2].contents[0]
        nratings = int("".join(ratings_str.split()))
        if min_nrate > nratings:
            min_nrate = nratings

    print("Page %i scraped, minimum number of ratings was %i" % (npage, min_nrate))
    npage += 1
    sleep(2) # Keep the BGG server happy.

with open('bggIds.csv', 'w+', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for val in ids:
        writer.writerow([val]) 