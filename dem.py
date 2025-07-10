import requests

bbox = (-8.6, 4.2, -2.5, 10.7)  
API_KEY = "7813a95ce783ddcdb9e45d4d992db0a3"  

# Define endpoint and parameters
url = "https://portal.opentopography.org/API/globaldem"
params = {
    "demtype": "COP90",          
    "south": bbox[1],
    "north": bbox[3],
    "west": bbox[0],
    "east": bbox[2],
    "outputFormat": "GTiff",     
    "API_Key": API_KEY           
}

# Send request
response = requests.get(url, params=params)

# Check response
if response.status_code == 200:
    with open("cotedivoire_cop30.tif", "wb") as f:
        f.write(response.content)
    print("✅ DEM saved as 'cotedivoire_cop30.tif'")
else:
    print(f"❌ Failed to fetch DEM. HTTP {response.status_code}:\n{response.text}")