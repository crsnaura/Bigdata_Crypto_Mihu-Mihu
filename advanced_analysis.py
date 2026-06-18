import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import os

print("🧠 [PROCESSING] Running Advanced Predictive Engine...")

if not os.path.exists("data/crypto_data.csv"):
    print("❌ Error: data/crypto_data.csv tidak ditemukan. Jalankan fetch_data.py terlebih dahulu.")
    exit()

df = pd.read_csv("data/crypto_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

# Pivot data ke format time-series horizontal
df_pivot = df.pivot(index="timestamp", columns="coin", values="price")
df_hourly = df_pivot.resample("1h").last().ffill()

# Log Return & Cumulative Return
df_log_return = np.log(df_hourly / df_hourly.shift(1))
df_cum_return = (df_hourly / df_hourly.iloc[0] - 1) * 100

# ====================================================
# RANDOM FOREST MARKET CLASSIFICATION ENGINE
# ====================================================
# Membuat fitur lag (data masa lalu) untuk melatih model klasifikasi
market_signals = {}
for coin in df_hourly.columns:
    coin_series = df_hourly[coin].dropna()
    X_features = pd.DataFrame({
        'lag_1': coin_series.shift(1),
        'lag_2': coin_series.shift(2),
        'lag_3': coin_series.shift(3),
        'ma_24': coin_series.rolling(24).mean()
    }).dropna()
    
    # Target: 1 jika harga naik di jam berikutnya, 0 jika turun
    y_target = (coin_series.shift(-1) > coin_series).astype(int).loc[X_features.index]
    
    # Train model Random Forest sederhana
    rf = RandomForestClassifier(n_estimators=50, random_state=42)
    rf.fit(X_features, y_target)
    
    # Ambil data paling terakhir untuk prediksi realtime nanti di dashboard
    last_features = np.array([[coin_series.iloc[-1], coin_series.iloc[-2], coin_series.iloc[-3], coin_series.rolling(24).mean().iloc[-1]]])
    prob_bullish = rf.predict_proba(last_features)[0][1]
    
    market_signals[coin] = {
        "classification": "🔥 STRONG BULLISH" if prob_bullish > 0.6 else "🧊 BEARISH CONSOLIDATION" if prob_bullish < 0.4 else "⚖️ NEUTRAL SIDEWAYS",
        "confidence": prob_bullish
    }

# Simpan hasil klasifikasi ke file kecil agar app.py tinggal membacanya dengan cepat (Velocity)
pd.DataFrame(market_signals).to_csv("data/market_classification_signals.csv")

# Save Preprocessed Files
df_hourly.to_csv("data/hourly_price.csv")
df_log_return.to_csv("data/log_return.csv")
df_cum_return.to_csv("data/cum_return.csv")

print("✅ [SUCCESS] Advanced Analysis and ML Models trained completely!")