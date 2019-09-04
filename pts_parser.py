import requests
import logging
import csv
import datetime
import urllib.request
import time
from bs4 import BeautifulSoup

currencySign = "€"
queryKey ="?saison_id="
currentSeason=2019
firstPossibleSeason=1888

def buildUrl(basePath, year) :
  return f"{basePath}{queryKey}{year}/"

def writeOutputToCsv(fileName, data) :
  with open(fileName, "a") as my_csv:
    csvWriter = csv.writer(my_csv, delimiter=',')
    csvWriter.writerows(data)

def getRootData(url) :
  data = requests.get(url, headers =  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'})
  return BeautifulSoup(data.text, "html.parser")

#replace strings to thoursands
def normalizePrice(price) :
  if price.endswith(f' Mill. {currencySign}') :
    return float(price.replace(f' Mill. {currencySign}', '')) * 1000
  elif price.endswith(f' Th. {currencySign}') :
    return price.replace(f' Th. {currencySign}', '')
  elif price.endswith(f' Bill. {currencySign}') :
    return float(price.replace(f' Bill. {currencySign}', '')) * 1000000
  else :
    return price

def grabDataFromUrl(url, country, year, outputFileName) :  
  soup = getRootData(url)
  table = soup.find("div", {"class": "responsive-table"})
  for x in table.findAll('thead'):
        x.extract()
  for x in table.findAll('img'):
      x.extract()
  allData = []
  for trTag in table.findAll('tr') :
    aTags = [f'{year}', f'{country}']
    for aTag in trTag.findAll('a') :   
      if len(aTag.contents) > 0 :
        aTags.append(aTag.contents[0])
    for tdTag in trTag.findAll('td')[-3:] :
      if len(tdTag.contents) > 0 :
        aTags.append(tdTag.contents[0])
    allData.append(aTags)   
 
  print("start writing output to file")  
  writeOutputToCsv(outputFileName, allData)
  print("finished writing output to file") 

#actually it gets all possible years. no need to set a year param!
def getYearsRange(soup) :
  selectTable = soup.find("select", {"name" : "saison_id"})
  possibleYears = []
  for o in selectTable.findAll("option") :
    possibleYears.append(o["value"]) 
  unorderedList = list(map(int, possibleYears))  
  return unorderedList

# gets input params from csv
def main(inputFileName, outputFileName) :
  open(outputFileName, 'a').close()
  with open(inputFileName) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
      possibleYears = getYearsRange(getRootData(buildUrl(row[1], currentSeason)))
      for year in possibleYears :
       searchUrl = buildUrl(row[1], year)
       print(f'Started processing data from url: {searchUrl}')
       try:
        grabDataFromUrl(searchUrl, row[0], year, outputFileName)
       except Exception as e:
        print(f'Failed to process data from url: {searchUrl} \n {e}') 
        break              
      print(f'Finished processing data from url: {searchUrl}')
      line_count += 1
    print(f'Processed {line_count} lines.')
	
	
main('input_for_pts_parsing.csv', f'pts_output_{time.time_ns()}.csv')