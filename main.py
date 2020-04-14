from selenium import webdriver
import os
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
#driver.get("https://www.pro-football-reference.com/years/2019/rushing_advanced.htm")
#tables = pd.read_html(driver.page_source)
#print("num of tables:", str(len(tables)))
#for index, table in enumerate(tables):
#    print("Index:", str(index))
#    for col in list(table.columns):
#        print(col)
#    print(table)



###Advanced stats grabber#####
#grabs Broken tackles and Yards after contact related stats for running backs
#grabs Yards after catch and broken tackle related stats for RB's, WR's, and TE
#writes each to it's own csv
#set the csv name and years you need at bottom of page


#path to the chrome
#browser = webdriver.Chrome(executable_path = r"C:/Users/lemar/Desktop/Schoolwork/Senior Design 2/chromedriver_win32/chromedriver.exe")

# a list of the abbreviations pfr.com uses for each team
teamList = [
                "crd" ,
                "atl" ,
                "rav" ,
                "buf" ,
                "car" ,
                "chi" ,
                "cin" ,
                "cle" ,
                "dal" ,
                "den" ,
                "det" ,
                "gnb" ,
                "htx" ,
                "clt" ,
                "jax" ,
                "kan" ,
                "sdg" ,
                "ram" ,
                "mia" ,
                "min" ,
                "nwe" ,
                "nor" ,
                "nyg" ,
                "nyj" ,
                "rai" ,
                "phi" ,
                "pit" ,
                "sfo" ,
                "sea" ,
                "tam" ,
                "oti" ,
                "was" ,
            ]


#this function is called by getTeamAdvRushStats()
#given a table, it extracts all the links in the table
#the links are for each player's page
#we don't need to go to the link, but the link contains the player's id
#this id is parsed from the link, and added to an array that is returned
def getPlayerIDs(webPage):
    links =  BeautifulSoup(webPage.get_attribute("innerHTML"), parse_only=SoupStrainer('a'), features="lxml")
    playerIDs = []
    for each in links:
        #get the url
        linkString = str(each['href'])
        #split the url based on slashes
        splitLink = linkString.split("/")
        #get player id portion of link
        playerID = splitLink[3].split(".")[0]
        #append it to the list
        playerIDs.append(playerID)
    return playerIDs

#this is caled by getAdvRushStats()
#this is called for every combination of team and year that we need to search for
#returns a table of the stats we need
def getTeamAdvStats(browser, team, year):
    #assemble the url
    url = "https://www.pro-football-reference.com/teams/" + team + "/" + str(year) + "_advanced.htm"
    #load the page
    browser.get(url)
    #get the appropriate table
    webPage =  browser.find_element_by_id("advanced_rushing")
    #get the tables on the page
    tables = pd.read_html(browser.page_source)
    #get table we need for rushing and trim down the columns
    rushTable = tables[4]
    rushTable = rushTable[["Player", "YAC", "BrkTkl"]].copy()
    rushTable = formatTable(webPage, rushTable, year)
    recTable = tables[5][["Player", "YBC" , "YAC", "BrkTkl"]].copy()
    webPage = browser.find_element_by_id("advanced_receiving")
    recTable = formatTable(webPage, recTable, year)
    return rushTable, recTable

def formatTable(webPage, rushTable, year):
    #get the player ID's
    playerIDs = getPlayerIDs(webPage)
    #remove team total row
    rushTable = rushTable.loc[rushTable["Player"] != "Team Total" ]
    #add the player ids
    rushTable.insert(1, "player_id", playerIDs)
    #add the year as a column
    yearColumn = [year] * len(rushTable.index)
    rushTable.insert(2, "season", yearColumn)
    return rushTable


#main calls this
#calls getTeamAdvRushStats() for every combo of team and year we need
#appends the result of getTeamAdvRushStats() to a single table
#returns one mega-table with all the player stats we need
def getAdvStats(browser, teamList, firstYear, lastYear):
    #create data frame we'll need
    mainRushTable = pd.DataFrame()
    mainRecTable = pd.DataFrame()
    #for each team in the team list
    for team in teamList:
        print(team)
        #for each year we need stats from
        for year in range(firstYear, lastYear+1):
            #get a table for the team and year combo we need
            teamRushTable, teamRecTable = getTeamAdvStats(browser, team, year)
            #append it to the main table
            mainRushTable = mainRushTable.append(teamRushTable, ignore_index = True)
            mainRecTable = mainRecTable.append(teamRecTable, ignore_index = True)
    #rename columns
    mainRushTable.columns = ["Player", "player_id", "season", "Yards After Contact", "Rush BrkTkl",]
    mainRecTable.columns = ["Player", "player_id", "season", "Yards Before Catch" , "Yards After Catch", "Rec BrkTkl"]


    return mainRushTable, mainRecTable


#main
#set what years to grab here
#note: these stats only go back to 2018
print("calling top function")
rushTable, recTable = getAdvStats(driver, teamList, 2018, 2019)
print(rushTable)
print(recTable)
#rushTable.to_csv("csvs/adv_rush_stats.csv")
#rushTable.to_csv("/home/thefanta/ffpscripttest/statpull/adv_rush_stats.csv")
#recTable.to_csv("/home/thefanta/ffpscripttest/statpull/adv_rec_stats.csv")
#recTable.to_csv("csvs/adv_rec_stats.csv")

