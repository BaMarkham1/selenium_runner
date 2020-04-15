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

#this is caled by getAdvRushStats()
#this is called for every combination of team and year that we need to search for
#returns a table of the stats we need
def getAdvStats(browser, category, year):

    def formatTable(webPage, rushTable, year):

        #this function is called by getTeamAdvRushStats()
        #given a table, it extracts all the links in the table
        #the links are for each player's page
        #we don't need to go to the link, but the link contains the player's id
        #this id is parsed from the link, and added to an array that is returned
        def getPlayerIDs(webPage):
            links =  BeautifulSoup(webPage.get_attribute("innerHTML"), parse_only=SoupStrainer('a'), features="lxml")
            playerIDs = []
            for index, each in enumerate(links):
                #get the url
                linkString = str(each['href'])
                #split the url based on slashes
                splitLink = linkString.split("/")
                if splitLink[1] == "players":
                    #get player id portion of link
                    playerID = splitLink[3].split(".")[0]
                    #append it to the list
                    playerIDs.append(playerID)
            return playerIDs

        #get the player ID's
        playerIDs = getPlayerIDs(webPage)
        #remove team total row
        rushTable = rushTable.loc[rushTable["Player"] != "Player" ]
        #add the player ids
        rushTable.insert(1, "player_id", playerIDs)
        #add the year as a column
        yearColumn = [year] * len(rushTable.index)
        rushTable.insert(2, "season", yearColumn)
        return rushTable

    def fix_column_names(table):
        new_columns = []
        for col in list(table.columns):
            new_columns.append(col[len(col)-1])
        table.columns = new_columns
        return table


    #assemble the url
    url = "https://www.pro-football-reference.com/years/" + str(year) + "/" + category + "_advanced.htm"
    #load the page
    browser.get(url)
    #print(browser.page_source)
    #get the tables on the page
    tables = pd.read_html(browser.page_source)
    print(len(tables))
    if category == "receiving":
        table = tables[1]
    else:
        table = tables[0]
    print(table.columns)
    if category == "rushing":
        table = fix_column_names(table)
    #get table we need for rushing and trim down the columns
    webPage = browser.find_element_by_id("advanced_" + category)
    print(webPage.get_attribute("innerHTML"))
    category_dict = {"rushing" : ["Player", "YAC", "BrkTkl"], "receiving" : ["Player", "YBC" , "YAC", "BrkTkl"]}
    #print(table.columns)
    table = table[category_dict[category]].copy()
    category_dict2 = {"rushing" : ["Player", "Yards After Contact", "Rush BrkTkl"], "receiving" : ["Player", "Yards Before Catch" , "Yards After Catch", "Rec BrkTkl"]}
    table.columns = category_dict2[category]
    table = formatTable(webPage, table, year)
    return table

print("getting receiving stats")
rec_table = getAdvStats(driver, "receiving", 2019)
#print("getting rushing stats")
#rush_table = getAdvStats(driver, "rushing", 2019)


#print(rush_table)
print(rec_table)
driver.close()
