import requests
import logging
import csv
import datetime
import urllib.request
import time
from bs4 import BeautifulSoup

currentSeason = 2019
currencySign = "â‚¬Â"
queryKey = "plus/?saison_id="
firstPossibleSeason = 1888
rootUrl = 'https://www.transfermarkt.com'


def writeOutputToCsv(fileName, data):
    with open(fileName, "a", encoding="utf-8") as my_csv:
        csvWriter = csv.writer(my_csv, delimiter=',')
        csvWriter.writerows(data)


def getRootData(url):
    data = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.100 Safari/537.36'})
    soup = BeautifulSoup(data.content, "html.parser", from_encoding="windows-1250")
    soup.encode("windows-1250")
    return soup
    # return BeautifulSoup(data.content, "html.parser")


# actually it gets all possible years. no need to set a year param!
def getYearsRange(soup):
    selectTable = soup.find("select", {"name": "saison_id"})
    possibleYears = []
    for o in selectTable.findAll("option"):
        possibleYears.append(o["value"])
    unorderedList = list(map(int, possibleYears))
    unorderedList.remove(unorderedList[0])
    return unorderedList

def normalizePrice(price):
    if ' Mill.' in price:
        price = price.split(" Mill.", 1)[0]
        price = price.replace(",", ".")
        return float(price) * 1000
    elif' Th.' in price:
        price = price.split(" Th.", 1)[0]
        price = price.replace(",", ".")
        return float(price)
    elif ' Bill.' in price:
        price = price.split(" Bill.", 1)[0]
        price = price.replace(",", ".")
        return float(price) * 1000000
    else:
        return price


def getClubsHrefs(soup):
    table = soup.find("table", {"class", "items"})
    tbody = table.find("tbody")
    aTags = tbody.findAll("a", {"class", "vereinprofil_tooltip"})
    hrefs = []
    for aTag in aTags:
        tagWithoutYear = aTag["href"][:-4]
        hrefs.append(f'{rootUrl}{tagWithoutYear}')
    return list(dict.fromkeys(hrefs))


def getClubName(soup):
    return soup.find("div", {"class", "dataTop"}).find("span").contents[0]


def getPlayersData(url, year, country):
    soup = getRootData(f'{url}{year}')
    clubName = getClubName(soup)
    print(f'searching for club {clubName} for year {year}')
    table = soup.find("div", {"class": "responsive-table"})

    tbody = table.find('tbody')
    allData = []
    try:
        if type(tbody) is not None:
            allTrs = tbody.findAll("tr", class_ = ['even', 'odd'])
            for k, tr in enumerate(allTrs):
                alltds = tr.findAll('td')
                aTags = [f'{year}', f'{country}', f'{clubName}']
                for l, td in enumerate(alltds):
                    # posCached = []
                    # porsela = td.find("td", {"class", "posrela"})
                    # posCached.append(porsela)
                    # porsela.extract()
                    if l == 0:
                        aTags.append(td["title"])
                    if l == 3:
                        aTags.append(td.find("a").contents[0])
                    if l == 5:
                        aTags.append(td.contents[0])
                    if l == 8:
                        aTags.append(normalizePrice(td.contents[0]))
                    if l == 6:
                        aTags.append(td.find('img')["title"])
                allData.append(aTags)
    except Exception as e:
        allData.append(
            [f'exception occured while parsing players data table for {year} and {country} with root cause: {e}'])
    print(f'all data: {allData}')
    return allData


def main(inputFileName, outputFileName):
    open(outputFileName, 'a').close()
    with open(inputFileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        allData = []
        for row in csv_reader:
            try:
                soup = getRootData(row[1])
                for year in getYearsRange(soup):
                    clubshrefs = getClubsHrefs(getRootData(f'{row[1]}{queryKey}{year}'))
                    for href in clubshrefs:
                        writeOutputToCsv(outputFileName, getPlayersData(href, year, row[0]))
            except Exception as e:
                print(f'Failed to process data from url: {row[1]} \n {e}')
            break
    print(f'Finished processing data from url: {row[1]}')
    line_count += 1
    print(allData)
    writeOutputToCsv(outputFileName, allData)
    print(f'Processed {line_count} lines.')


main('input_for_overview.csv', f'output_{time.time_ns()}.csv')
# readInputParamsFromFile('input.csv')


# grabDataFromUrl( 'https://www.transfermarkt.com/chinese-super-league/startseite/wettbewerb/CSL/plus/?saison_id=2019')
