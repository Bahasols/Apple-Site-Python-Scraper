import requests
from bs4 import BeautifulSoup
import csv
import re
import string
#Import link https://www.apple.com/retail/storelist/
#Json data link https://www.apple.com/rsp-web/store-detail?storeSlug='{INSERT STORE NAME HERE}'&locale=en_US
site_url = 'https://www.apple.com/retail/storelist/'
r = requests.get(site_url)                                  #HTTP request GET
html_content = r.content                                    #Response content of (HTML)
soup = BeautifulSoup(html_content, 'html.parser')
stores = soup.find_all('div', {'class':'address-lines'})        #Retrieving all tags with class name "address-lines"

data = []    #List of dictionaries to pass into the csv writer
             #This will contain the results of our work


for store in stores:
    text = store.text               #The text content of the stores object retrieved using soup.find_all('div', {'class':'address-lines'})
    name = ''
    street = ''                     #Initializing data for debugging purposes
    locality = ''                   #Also gives visualization of what the fields in the 'data' list look like
    region = ''
    postal_code = ''
    latitude = ''
    longitude = ''
    url = ''

    name_match = re.search(r'(?<=,\s)(.*)', text)               #Expression to retrieve the string before the comma
    name = name_match.group(1)                                  #GETTING 'NAME' COLUMN
    locality_match = re.search(r'([^,]+)',text)                 #Expression to retrieve the string after the comma
    if locality_match:
        locality = locality_match.group(1)                          #GETTING 'LOCALITY' COLUMN
        print('Parsing '+name + " -- " + locality + '....')

    #Example of a store URL : https://www.apple.com/retail/thesummit/
    #Follows similar pattern as original url, however, spaces must be removed from 'name'
    punc_pattern = r"[{}]".format(re.escape(string.punctuation))
    spaceless_name = name
    spaceless_name = spaceless_name.replace(" ", "")    #Remove spaces
    puncless_name = re.sub(punc_pattern,"",spaceless_name)

    url = 'https://www.apple.com/retail/' + puncless_name + '/'        #Append the spaceless name and add '/'
    url = url.lower()
    #Convert into lowercase (crashes if you don't)

    # store_response = requests.get(url)
    # store_soup = BeautifulSoup(store_response.content, 'html.parser')             #Complete Pain
    # address_tag = store_soup.find('address')                                      #Attempting to use regex to parse the html
    # print(address_tag)
    # if address_tag:
    #     address = address_tag.get_text(strip= True)
    #     print(address)
    #     address_match = re.match(r"^(\d+)\s+([\w\s\.,]+?)([A-Za-z]+),([A-Za-z]{2})(\d{5})$", address)
    #
    # if address_match:                   #If match is found, retrieve the results
    #     street = address_match.group(1) + " " + address_match.group(2)
    #     city = address_match.group(3)
    #     region = address_match.group(4)
    #     postal_code = address_match.group(5)

    url_geo = 'https://www.apple.com/rsp-web/store-detail?storeSlug='+puncless_name.lower()+'&locale=en_US'   #URL for JSON FILE


    location_response = requests.get(url_geo)
    if location_response:
        json_data = location_response.json()             #retrieving the json file
        latitude = json_data['geolocation']['latitude']      #retrieving the latitude from json file
        longitude = json_data['geolocation']['longitude']    #retrieving longitude from json file
        street = json_data['address']['address1']           #retrieving street from json file
        region = json_data['address']['stateCode']          #retrieving region from json file
        postal_code = json_data['address']['postal']        #retrieving postal from json file
        print('Success.')
    else:
        print('Failed to parse store location' + name)

    data.append(      #Appending the scraped data into the list of dictionaries
        {
            'Name' : name,
            'Street' : street,
            'Locality' : locality,
            'Region' : region,
            'Postal Code' : postal_code,
            'Latitude' : latitude,
            'Longitude' : longitude,
            'URL' : url
        }
    )

with open('apple_stores.csv', 'w', newline='') as file: #CSV file name to be generated
    writer = csv.DictWriter(file,fieldnames=['Name','Street', 'Locality','Region', 'Postal Code' , 'Latitude' , 'Longitude', 'URL'])
    writer.writeheader()
    for store_data in data:         #Store each object into rows
        writer.writerow(store_data)