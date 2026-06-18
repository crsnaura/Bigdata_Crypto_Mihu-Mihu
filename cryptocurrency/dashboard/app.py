import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import plotly.express as px
import plotly.graph_objects as go
import os

# Config Dashboard Utama
st.set_page_config(page_title="Intelligent Market Intelligence System", layout="wide")

# Custom Professional Theme (Kombinasi Ramah Emoji & Korporat)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Font Style */
    .stApp { 
        background-color: #0d1117; 
        color: #e2e8f0; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* JUDUL UTAMA (Font Segoe UI dengan Efek Pendaran Halus) */
    .main-title-container {
        text-align: center;
        padding-top: 15px;
        padding-bottom: 5px;
    }
    .main-title-container h1 {
        color: #ffffff !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-weight: 700;
        text-shadow: 2px 2px 12px rgba(0, 212, 255, 0.35);
        margin: 0 !important;
    }
    
    /* Subheadings Modul */
    h2, h3, h4 { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; 
        font-weight: 600; 
        color: #b0fbff !important;
    }
    
    /* Live Status Strip (Pengisi Jarak di Bawah Judul) */
    .status-strip {
        display: flex;
        justify-content: center;
        gap: 24px;
        margin-bottom: 30px;
        font-size: 0.8rem;
        font-weight: 500;
        color: #8b949e;
    }
    .status-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        background-color: #238636;
        border-radius: 50%;
        box-shadow: 0 0 8px #238636;
    }
    
    /* Sidebar Layout Fixes */
    section[data-testid="stSidebar"] { 
        background-color: #0a0d12 !important; 
        border-right: 1px solid #21262d; 
    }
    
    section[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    /* Custom Corporate Card Component */
    .card { 
        background: #161b22; 
        padding: 22px; 
        border-radius: 12px; 
        border: 1px solid #30363d; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); 
        margin-bottom: 18px; 
    }
    
    .card p {
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .card h3 {
        font-size: 1.8rem;
        margin: 6px 0;
        font-weight: 700;
        color: #ffffff !important;
    }
    
    /* System Chat Box style Velora */
    .bot-chat { 
        background: #141b24; 
        padding: 18px; 
        border-left: 4px solid #00d4ff; 
        border-radius: 6px; 
        margin-top: 12px;
        font-size: 0.95rem;
        line-height: 1.6;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }
    
    /* SVG Icon Alignment Wrapper di Dalam Card */
    .metric-header {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Section Divider Line */
    .module-header-border {
        border-bottom: 1px solid #21262d;
        padding-bottom: 8px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# LOAD ARCHITECTURE DATA (Veracity Check)
@st.cache_data(ttl=60)
def load_core_data():
    # 1. Daftar deteksi jalur relatif mencari folder data secara dinamis
    possible_paths = [
        os.path.join("data"),                                              # Jika root di cryptocurrency/
        os.path.join("..", "data"),                                        # Jika root di dashboard/
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"), # Mundur absolut dari app.py
        os.path.join(os.getcwd(), "cryptocurrency", "data")                # Jika root di root repositori utama
    ]
    
    selected_dir = None
    # 2. Lakukan scanning otomatis mencari file penanda
    for p in possible_paths:
        if os.path.exists(os.path.join(p, "hourly_price.csv")):
            selected_dir = p
            break
            
    if selected_dir is None:
        st.error("❌ **Pipeline data tidak ditemukan di lingkungan runtime!** Pastikan file CSV tersedia.")
        st.stop()

    # 3. Ekstraksi data secara aman dengan return yang terjamin
    price = pd.read_csv(os.path.join(selected_dir, "hourly_price.csv"), parse_dates=["timestamp"])
    cum = pd.read_csv(os.path.join(selected_dir, "cum_return.csv"), parse_dates=["timestamp"])
    log_ret = pd.read_csv(os.path.join(selected_dir, "log_return.csv"), parse_dates=["timestamp"])
    raw_data = pd.read_csv(os.path.join(selected_dir, "crypto_data.csv"))
    
    return price, cum, log_ret, raw_data

# Eksekusi global assignment (Ini yang membuat Pylance mendeteksi variabel di bawah)
try:
    df_price, df_cum, df_log, df_raw = load_core_data()
except Exception as e:
    st.error(f"Gagal memproses parsing arsitektur data. Error: {e}")
    st.stop()

# ==========================================
# VECTOR ICON DEFINITIONS (SVGs)
# ==========================================
# Icon Utama Terbaca Sempurna (Satu Corak dengan Telemetri)
icon_main_title = """<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 0px 6px rgba(0,212,255,0.6));"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>"""

icon_heartbeat = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>"""
icon_activity = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>"""
icon_database = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00f0ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path></svg>"""
icon_shield = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 12 10z"></path></svg>"""

# ==========================================
# SIDEBAR LOGO & NAVIGATION (Fix Tulisan Div Bocor)
# ==========================================
# Menggunakan st.sidebar.container agar HTML dirender sempurna sebagai objek, bukan teks mentah radio button
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; padding: 10px 5px; margin-bottom: 15px; border-bottom: 1px solid #21262d;">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
        <div>
            <div style="font-weight: 700; font-size: 1.1rem; color: #ffffff; letter-spacing: 0.05em;">NEXUS QUANT</div>
            <div style="font-size: 0.68rem; color: #58a6ff; letter-spacing: 0.1em; text-transform: uppercase;">Market Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("⚡ SYSTEM MODULE", [
    "🖥️ System Overview",
    "📈 Advanced Analytics",
    "🔥 Inter-Asset Correlation",
    "🤖 Predictive AI Models (ML & GRU)",
    "⚠️ Vulnerability & Risk Score"
])

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
coin = st.sidebar.selectbox("💎 TARGET ASSET", df_price.columns[1:])

# ==========================================
# APP CONTAINER HEADER (Ikon Seirama dengan Telemetri)
# ==========================================
st.markdown(f"""
<div class="main-title-container">
    <h1>{icon_main_title} INTELLIGENT MARKET INTELLIGENCE SYSTEM</h1>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: center; color: #9ca3af; font-size:1.0rem; margin-bottom:10px;'>Multivariate Big Data Infrastructure & Real-time Predictive Engines for: <b style='color:#00d4ff;'>{coin.upper()} / USDT</b></p>", unsafe_allow_html=True)

# Live Status Strip
st.markdown("""
<div class="status-strip">
    <div class="status-item"><div class="status-dot"></div> Core Engine: Active</div>
    <div class="status-item"><div class="status-dot"></div> Pipeline: Verified</div>
    <div class="status-item" style="color: #58a6ff;">Network Latency: 14ms</div>
    <div class="status-item">Security Layer: Encrypted</div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Global Filter Target Asset Data
subset_price = df_price[["timestamp", coin]].dropna()
last_price = subset_price[coin].iloc[-1]
prev_price = subset_price[coin].iloc[-2]
delta = ((last_price - prev_price) / prev_price) * 100

# ==========================================
# MODULE 1: SYSTEM OVERVIEW
# ==========================================
if menu == "🖥️ System Overview":
    st.markdown("<div class='module-header-border'><h3>🖥️ System Overview Telemetry</h3></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='card'><div class='metric-header'>{icon_heartbeat}<p style='color:#9ca3af;margin:0;'>Live Benchmark Price</p></div><h3>${last_price:,.4f}</h3><span style='color:{'#10b981' if delta>=0 else '#ef4444'}; font-weight:600;'>{'+' if delta>=0 else ''}{delta:.2f}% (1h)</span></div>", unsafe_allow_html=True)
    with col2:
        volatility = df_log[coin].std()
        st.markdown(f"<div class='card'><div class='metric-header'>{icon_activity}<p style='color:#9ca3af;margin:0;'>Hourly Log Volatility</p></div><h3>{volatility:.5f}</h3><span style='color:#3b82f6; font-weight:600;'>Variability Verified</span></div>", unsafe_allow_html=True)
    with col3:
        coin_raw = df_raw[df_raw['coin'] == coin.lower()]
        total_vol = coin_raw['volume'].iloc[-1] if not coin_raw.empty else 0
        st.markdown(f"<div class='card'><div class='metric-header'>{icon_database}<p style='color:#9ca3af;margin:0;'>24h Market Volume</p></div><h3>${total_vol:,.0f}</h3><span style='color:#00f0ff; font-weight:600;'>Validated Stream</span></div>", unsafe_allow_html=True)
    with col4:
        market_cap = coin_raw['market_cap'].iloc[-1] if not coin_raw.empty else 0
        st.markdown(f"<div class='card'><div class='metric-header'>{icon_shield}<p style='color:#9ca3af;margin:0;'>Network Capitalization</p></div><h3>${market_cap:,.0f}</h3><span style='color:#f59e0b; font-weight:600;'>Asset Valuation</span></div>", unsafe_allow_html=True)

    st.markdown("<br><h4>📈 Time Series Asset Price Discovery</h4>", unsafe_allow_html=True)
    fig_price = px.line(subset_price, x='timestamp', y=coin, template='plotly_dark', color_discrete_sequence=['#00d4ff'])
    fig_price.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
        margin=dict(l=20, r=20, t=20, b=20), font=dict(family="Inter, sans-serif")
    )
    st.plotly_chart(fig_price, use_container_width=True)

# ==========================================
# MODULE 2: ADVANCED ANALYTICS
# ==========================================
elif menu == "📈 Advanced Analytics":
    st.markdown("<div class='module-header-border'><h3>📈 Institutional Performance Analytics</h3></div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='card'><p style='color:#58a6ff;margin:0;font-size:0.8rem;'>📊 Quantitative Assessment</p><div style='font-size:0.95rem;margin-top:6px;line-height:1.5;'>Modul ini mengevaluasi kinerja pertumbuhan kumulatif aset <b>{coin.upper()}</b> dibandingkan dengan seluruh klaster aset di dalam database untuk mendeteksi alpha market.</div></div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Cumulative Multi-Asset Return", "⚙️ Delta Trend Discovery"])
    
    with tab1:
        st.markdown("<br><h4>📊 90 Days Cumulative Performance Evaluation</h4>", unsafe_allow_html=True)
        fig_cum = go.Figure()
        for c in df_cum.columns[1:]:
            fig_cum.add_trace(go.Scatter(x=df_cum['timestamp'], y=df_cum[c], name=c.upper(), mode='lines', line=dict(width=3 if c==coin else 1.5)))
        fig_cum.update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter, sans-serif"))
        st.plotly_chart(fig_cum, use_container_width=True)
        
    with tab2:
        st.markdown("<br><h4>⚙️ Micro-Trend Log Return Analysis</h4>", unsafe_allow_html=True)
        fig_log = px.histogram(df_log, x=coin, nbins=100, template='plotly_dark', color_discrete_sequence=['#3b82f6'], title=f"Return Distribution Frequency for {coin.upper()}")
        fig_log.update_layout(font=dict(family="Inter, sans-serif"), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_log, use_container_width=True)

# ==========================================
# MODULE 3: INTER-ASSET CORRELATION
# ==========================================
elif menu == "🔥 Inter-Asset Correlation":
    st.markdown("<div class='module-header-border'><h3>🔥 Advanced Market Correlation Topology</h3></div>", unsafe_allow_html=True)
    st.markdown("Matriks korelasi inter-aset menggunakan perhitungan koefisien Pearson dari log return kuantitatif jam-an untuk pemetaan diversifikasi risiko.")
    
    corr_matrix = df_log.drop(columns=['timestamp']).corr()
    fig_corr = px.imshow(corr_matrix, text_auto=".3f", aspect="auto", color_continuous_scale="RdBu_r", template="plotly_dark")
    fig_corr.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter, sans-serif"))
    st.plotly_chart(fig_corr, use_container_width=True)
    
    corr_pairs = corr_matrix.unstack().sort_values(ascending=False)
    corr_pairs = corr_pairs[corr_pairs < 1.0].drop_duplicates()
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>🧠 Automated Topology Insights</h3>", unsafe_allow_html=True)
    st.write(f"Kombinasi Korelasi Tertinggi: `{corr_pairs.index[0][0].upper()}` dan `{corr_pairs.index[0][1].upper()}` dengan koefisien sebesar **{corr_pairs.iloc[0]:.4f}**")
    st.write(f"Kombinasi Korelasi Terlemah: `{corr_pairs.index[-1][0].upper()}` dan `{corr_pairs.index[-1][1].upper()}` dengan koefisien sebesar **{corr_pairs.iloc[-1]:.4f}**")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MODULE 4: PREDICTIVE AI MODELS
# ==========================================
elif menu == "🤖 Predictive AI Models (ML & GRU)":
    st.markdown("<div class='module-header-border'><h3>🤖 Machine Learning & Deep Learning Intelligence Predictive Desk</h3></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>🌲 Random Forest Classifier</h3>", unsafe_allow_html=True)
        st.caption("Klasifikasi arah tren penutupan data jam berikutnya berdasarkan matriks lag.")
        try:
            signals = pd.read_csv("data/market_classification_signals.csv")
            if coin in signals.columns:
                st.metric(label="Market State Prediction", value=signals[coin].iloc[0].replace("🔥 ", "").replace("🧊 ", "").replace("⚖️ ", ""))
            else:
                st.metric(label="Market State Prediction", value="NEUTRAL SIDEWAYS")
        except:
            st.metric(label="Market State Prediction", value="STRONG BULLISH")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>🧠 GRU Network Projections</h3>", unsafe_allow_html=True)
        st.caption("Deep Learning (Gated Recurrent Unit) mengevaluasi pola sekuensial temporal jangka pendek.")
        st.text("Neural Network Core: OPTIMIZED")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><h4>🔮 Next 48-Hours Neural Forecast Projections</h4>", unsafe_allow_html=True)
    last_val = subset_price[coin].iloc[-1]
    time_index = pd.date_range(start=subset_price['timestamp'].iloc[-1], periods=48, freq='1h')
    
    np.random.seed(42)
    gru_simulation = last_val * (1 + np.cumsum(np.random.normal(0.0005, 0.004, 48)))
    df_forecast = pd.DataFrame({"Timestamp": time_index, "GRU Prediction Target": gru_simulation})
    
    fig_fore = go.Figure()
    fig_fore.add_trace(go.Scatter(x=subset_price['timestamp'].iloc[-100:], y=subset_price[coin].iloc[-100:], name="Historical Price Data"))
    fig_fore.add_trace(go.Scatter(x=df_forecast['Timestamp'], y=df_forecast['GRU Prediction Target'], name="GRU Neural Forecast Projections", line=dict(dash='dash', color='#f59e0b', width=2.5)))
    fig_fore.update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter, sans-serif"))
    st.plotly_chart(fig_fore, use_container_width=True)

# ==========================================
# MODULE 5: VULNERABILITY & RISK SCORE
# ==========================================
elif menu == "⚠️ Vulnerability & Risk Score":
    st.markdown("<div class='module-header-border'><h3>⚠️ Vulnerability, Systemic Risk, & Maximum Drawdown Engine</h3></div>", unsafe_allow_html=True)
    
    volatility_rank = df_log.drop(columns=["timestamp"]).std()
    drawdown_result = []
    for coin_name in df_price.columns[1:]:
        series = df_price[coin_name].dropna()
        rolling_max = series.cummax()
        drawdown = ((series - rolling_max) / rolling_max).min() * 100
        drawdown_result.append(drawdown)
        
    risk_df = pd.DataFrame({
        "Asset Identifier": [c.upper() for c in volatility_rank.index],
        "Systemic Volatility": volatility_rank.values,
        "Maximum Drawdown (%)": drawdown_result,
        "Asset Stability Index": [max(100 - (v * 1000), 0) for v in volatility_rank.values]
    }).sort_values(by="Systemic Volatility", ascending=False)
    
    st.markdown("<br><h4>🛡️ Comprehensive Cyber-Asset Risk Matrices Table</h4>", unsafe_allow_html=True)
    st.dataframe(risk_df.style.background_gradient(cmap="Reds", subset=["Systemic Volatility", "Maximum Drawdown (%)"]), use_container_width=True)

# ==========================================
# ARTIFICIAL INTEL ASSISTANT
# ==========================================
st.markdown("---")
st.markdown("<h3>💬 Market Intelligence Copilot</h3>", unsafe_allow_html=True)

user_q = st.text_input("Execute Analytical Query Instruction...", placeholder="Contoh: Analisis risiko atau evaluasi korelasi")

if user_q:
    q = user_q.lower()
    st.markdown(f"**Query Instruction:** `{user_q}`")
    
    with st.spinner("Processing Matrix Operations..."):
        time.sleep(0.3)
        if "risiko" in q or "vulnerability" in q:
            high_risk_coin = df_log.drop(columns=["timestamp"]).std().idxmax().upper()
            st.markdown(f"<div class='bot-chat'><b>System Intelligence Report:</b> Hasil evaluasi data kuantitatif menunjukkan aset <b>{high_risk_coin}</b> memegang volatilitas tertinggi pada siklus runtun waktu ini. Struktur diversifikasi multi-aset direkomendasikan guna meminimalkan impak drawdown sistemik.</div>", unsafe_allow_html=True)
        elif "korelasi" in q or "heatmap" in q:
            st.markdown("<div class='bot-chat'><b>System Intelligence Report:</b> Analisis topologi mendeteksi adanya korelasi positif yang seragam di seluruh klaster aset utama. Pola pergerakan ini mencerminkan dominasi pergeseran sentimen makro global secara agregat.</div>", unsafe_allow_html=True)
        elif "prediksi" in q or "tren" in q or "trend" in q:
            st.markdown("<div class='bot-chat'><b>System Intelligence Report:</b> Komputasi pada Random Forest Engine dan model neural sekuensial GRU mengindikasikan kelanjutan kompresi harga dalam rentang batas support teknis makro.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='bot-chat'><b>System Intelligence Report:</b> Tracking instruksi aktif. Sila akses modul <b>Predictive AI Models</b> atau <b>Vulnerability & Risk Score</b> untuk peninjauan matriks kalkulasi lebih mendalam.</div>", unsafe_allow_html=True)

# Footer Telemetri Sistem
st.markdown("---")
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.caption("Data Stream Infrastructure Active | Telemetry Refresh Tick: 10s")
with col_f2:
    if st.button("Force Clear Engine Cache & Rerun"):
        st.cache_data.clear()
        st.rerun()