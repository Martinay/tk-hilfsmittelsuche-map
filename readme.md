A Python script that retrieves addresses from the "Hilsmittelsuche" section of the [TK website](https://www.tk.de/service/app/2003358/hilfsmittelsuche/suche.app) and displays them on an HTML page.

# How to run
1. Install python packages
```
pip install folium geopy playwright beautifulsoup4
```
2. Setup chromium for playwright
```
playwright install chromium   
```
2. Modify the variable category
3. Run the script
```
    python main.py
```