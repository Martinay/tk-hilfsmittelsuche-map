import folium
from geopy.geocoders import Nominatim
import xml.etree.ElementTree as ET
import re
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

########### get html ##########################
def load_adresses_from_tk_homepage(category):
    addresses = []
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.tk.de/service/app/2003358/hilfsmittelsuche/suche.app")
        page.get_by_role("link", name="Auswahl bestätigen").click()
        page.locator("div").filter(has_text=re.compile(f"^{category}$")).locator("div").nth(2).click()
        page.get_by_role("link", name="Hilfsmittelpartner anzeigen").click()
    
        while True:
            page.locator("[id=\"j_idt15\\:himiPartner_data\"] div") # wait until search results are loaded
            result_html = [search_result.inner_html().strip() for search_result in page.query_selector_all('[role="gridcell"]')]
            
            for result in result_html:
                soup = BeautifulSoup(result, 'html.parser')
                address_div = soup.find_all('div')[1]  # Assuming the second div contains the address
                addresses.append(address_div.get_text(strip=True).replace(u'\xa0', u' '))  # Get the text and strip whitespace

            next_page_link = page.get_by_role("link", name="Nächste Seite")       
            tab_index = next_page_link.get_attribute("tabindex")      
            if tab_index == '-1': # if tabindex is negative then it's the last page
                break
            
            next_page_link.click()

        # ---------------------
        context.close()
        browser.close()

    return addresses

########### print map from adresses ##########################
def get_coordinates(address):
    geolocator = Nominatim(user_agent="tkDoctorExtractor")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

def display_addresses_on_map(addresses):
    # Initialize a map centered around Germany
    map = folium.Map(location=[51.163364, 10.447682], zoom_start=5)
    
    for address in addresses:
        coords = get_coordinates(address)
        time.sleep(1.5)  # wait for 1.5 second to prevent getting blocked by geopy
        if coords:
            folium.Marker(location=coords, popup=address).add_to(map)

    return map

########### main ##########################
category = 'Schuheinlagen'
addresses = load_adresses_from_tk_homepage(category)

print("address:")
for address in addresses:
    print(address)


print("print map")
map_obj = display_addresses_on_map(addresses)
map_obj.save(f"map-{category}.html")
print("done")