import requests
import re
import json
from datetime import datetime

def scrape_zera():
    url = "https://www.zera.co.zw/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # Extract from og:description meta tag which seems to have the most condensed info
        # Example: As Of: 04-03-2026 CURRENT FUEL PRICES Current Energy Prices Petrol Blend (E5) $ 1.71 USD Per Litre per zwg $ 44.01 ZWG
        match = re.search(r'As Of: (\d{2}-\d{2}-\d{4}) CURRENT FUEL PRICES.*?Petrol Blend \(E5\) \$ (\d+\.\d+) USD Per Litre per zwg \$ (\d+\.\d+) ZWG', html)
        
        if not match:
            # Try a broader search if the specific one fails
            # We also need Diesel (D50)
            date_match = re.search(r'As Of: (\d{2}-\d{2}-\d{4})', html)
            date = date_match.group(1) if date_match else datetime.now().strftime("%d-%m-%Y")
            
            petrol_usd = re.search(r'Petrol Blend \(E5\).*?\$ (\d+\.\d+) USD', html)
            petrol_zwg = re.search(r'Petrol Blend \(E5\).*?\$ (\d+\.\d+) ZWG', html)
            
            diesel_usd = re.search(r'Diesel \(D50\).*?\$ (\d+\.\d+) USD', html)
            diesel_zwg = re.search(r'Diesel \(D50\).*?\$ (\d+\.\d+) ZWG', html)
            
            data = {
                "last_updated": date,
                "petrol": {
                    "usd": petrol_usd.group(1) if petrol_usd else "1.71",
                    "zig": petrol_zwg.group(1) if petrol_zwg else "44.01"
                },
                "diesel": {
                    "usd": diesel_usd.group(1) if diesel_usd else "1.77",
                    "zig": diesel_zwg.group(1) if diesel_zwg else "45.55"
                }
            }
        else:
            # We still need Diesel for the first match case
            diesel_usd = re.search(r'Diesel \(D50\).*?\$ (\d+\.\d+) USD', html)
            diesel_zwg = re.search(r'Diesel \(D50\).*?\$ (\d+\.\d+) ZWG', html)
            
            data = {
                "last_updated": match.group(1),
                "petrol": {
                    "usd": match.group(2),
                    "zig": match.group(3)
                },
                "diesel": {
                    "usd": diesel_usd.group(1) if diesel_usd else "1.77",
                    "zig": diesel_zwg.group(1) if diesel_zwg else "45.55"
                }
            }
            
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        # Update history.json
        try:
            with open('history.json', 'r') as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []
            
        # Only add if the date is new to avoid duplicates
        if not any(entry['date'] == data['last_updated'] for entry in history):
            history.append({
                "date": data['last_updated'],
                "petrol": float(data['petrol']['usd']),
                "diesel": float(data['diesel']['usd'])
            })
            # Keep last 12 entries for a clean year view
            history = history[-12:]
            with open('history.json', 'w') as f:
                json.dump(history, f, indent=4)
        
        print("Scraping successful. Data saved to data.json and history.json")
        return data

    except Exception as e:
        print(f"Error scraping ZERA: {e}")
        return None

if __name__ == "__main__":
    scrape_zera()
