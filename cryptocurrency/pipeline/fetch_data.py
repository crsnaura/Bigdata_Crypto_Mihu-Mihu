import requests
import pandas as pd
import time
import os

coins = ["bitcoin", "ethereum", "solana", "dogecoin", "binancecoin"]
all_data = []

# Buat folder data jika belum ada
os.makedirs("data", exist_ok=True)

print("🌐 [START] Fetching Crypto Data for Intelligent System...")

for coin in coins:
    print(f"📡 Downloading 90-days history for {coin.upper()}...")
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {"vs_currency": "usd", "days": "90"}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            df_price = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            df_market = pd.DataFrame(data["market_caps"], columns=["timestamp", "market_cap"])
            df_volume = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])
            
            df = df_price.merge(df_market, on="timestamp").merge(df_volume, on="timestamp")
            df["coin"] = coin
            all_data.append(df)
        else:
            print(f"⚠️ Failed to fetch {coin}: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error on {coin}: {str(e)}")
        
    time.sleep(1.5) # Mencegah rate limit Coingecko

if all_data:
    final_df = pd.concat(all_data)
    final_df.to_csv("data/crypto_data.csv", index=False)
    print("✅ [SUCCESS] Core Data Engine Ready inside data/crypto_data.csv")
else:
    print("❌ [CRITICAL] No data saved.")