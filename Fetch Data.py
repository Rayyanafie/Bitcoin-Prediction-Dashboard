import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM
from datetime import datetime, timedelta
import yfinance as yf
from joblib import load
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ==============================================================================
# CONFIGURATION NON BIAS
# ==============================================================================
MODEL_PATH    = "Model.keras"
SCALER_PATH   = "minmax_scaler.joblib" 
HMM_PATH      = "hmm_btc_2024.joblib"  
LOOKBACK      = 30
FORECAST_DAYS = 1  # 1 = Besok saja, 7 = Seminggu kedepan
OUT_CSV       = "predict.csv"
FORECAST_CSV  = "future_prediction_results.csv"

# ==============================================================================
# STEP 1: DOWNLOAD & PREPARE DATA
# ==============================================================================
print("⏳ Downloading Bitcoin Data...")
end_date = datetime.today()
start_date = end_date - timedelta(days=60) 

btc_df = yf.download('BTC-USD', start=start_date, end=end_date)

# Jika MultiIndex (yfinance update baru), ratakan
if isinstance(btc_df.columns, pd.MultiIndex):
    btc_df.columns = btc_df.columns.get_level_values(0)

# Pastikan data bersih
btc_df = btc_df.reset_index()
btc_data = btc_df[['Close']].dropna().values

# ==============================================================================
# STEP 2: GENERATE HIDDEN STATES (HMM)
# ==============================================================================
print("⏳ Generating Hidden States...")
try:
    hmm_model = load(HMM_PATH)
    hidden_states = hmm_model.predict(btc_data)
    
    # Potong btc_df agar panjangnya sama dengan hidden_states (jika ada dropna)
    btc_df = btc_df.iloc[-len(hidden_states):].copy()
    btc_df['HiddenState'] = hidden_states
    
    # Simpan intermediate result
    btc_df[['Date', 'Close', 'HiddenState']].to_csv("bitcoin_with_hidden_states.csv", index=False)
except Exception as e:
    raise RuntimeError(f"Gagal load HMM atau predict state: {e}")

# ==============================================================================
# STEP 3: PREPARE FEATURES & LOAD SCALER
# ==============================================================================
print("⏳ Loading Scaler & Transforming Data...")

# Fitur yang digunakan: Close dan HiddenState
features = btc_df[["Close", "HiddenState"]].values.astype(np.float32)
n_features = features.shape[1] # Harusnya 2

try:
    scaler = load(SCALER_PATH)
    X_scaled_full = scaler.transform(features)
    print("✅ Scaler loaded successfully.")
except FileNotFoundError:
    raise FileNotFoundError(f"File '{SCALER_PATH}' tidak ditemukan!")

# ==============================================================================
# STEP 4: WALK-FORWARD EVALUATION (RAW MODEL PREDICTION)
# ==============================================================================
print("\n=== Walk-Forward Evaluation (Raw Model Output) ===")

model = load_model(MODEL_PATH)

start_idx = LOOKBACK
end_idx   = len(btc_df) - 1

pred_dates = []
y_true_list = []
y_pred_list = [] 

# --- Loop Prediksi ---
for t in range(start_idx, end_idx + 1):
    window = X_scaled_full[t - LOOKBACK : t]
    window = window.reshape(1, LOOKBACK, n_features)

    # Prediksi
    predicted_scaled = model.predict(window, verbose=0)
    
    # Inverse Transform
    dummy_zeros = np.zeros((predicted_scaled.shape[0], n_features - 1))
    combined_array = np.concatenate((predicted_scaled, dummy_zeros), axis=1)
    yhat = scaler.inverse_transform(combined_array)[:, 0][0]

    # Simpan
    pred_dates.append(btc_df.loc[t, "Date"])
    y_true_list.append(btc_df.loc[t, "Close"])
    y_pred_list.append(yhat)

# Ubah ke numpy array
y_true = np.array(y_true_list)
y_pred = np.array(y_pred_list)

# --- HITUNG ERROR (TANPA BIAS) ---
mae  = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

print(f"Samples: {len(y_true)}")
print(f"MAE (Raw)  : {mae:,.4f}")
print(f"RMSE (Raw) : {rmse:,.4f}")
print(f"MAPE (Raw) : {mape:.2f}%")

# Simpan CSV Evaluasi
out = pd.DataFrame({
    "date": pred_dates, 
    "actual": y_true, 
    "predicted": y_pred
})
out.to_csv(OUT_CSV, index=False)
print(f"✅ Saved evaluation: {OUT_CSV}")

# ==============================================================================
# STEP 5: FORECASTING (PREDIKSI MASA DEPAN) - RAW
# ==============================================================================
print(f"\n=== Generating Forecast for next {FORECAST_DAYS} days ===")

current_batch = features[-LOOKBACK:].copy()
last_real_date = btc_df['Date'].iloc[-1]
future_results = []

for i in range(FORECAST_DAYS):
    # Scale
    current_batch_scaled = scaler.transform(current_batch)
    input_data = current_batch_scaled.reshape(1, LOOKBACK, n_features)
    
    # Prediksi Raw
    pred_scaled = model.predict(input_data, verbose=0)
    
    # Inverse Transform
    dummy_zeros = np.zeros((pred_scaled.shape[0], n_features - 1))
    combined_array = np.concatenate((pred_scaled, dummy_zeros), axis=1)
    pred_price = scaler.inverse_transform(combined_array)[:, 0][0]
    
    # === TANPA BIAS (MURNI MODEL) ===
    
    next_date = last_real_date + timedelta(days=i + 1)
    print(f"Day +{i+1} ({next_date.date()}): {pred_price:,.2f}")
    
    future_results.append({
        "Date": next_date,
        "Predicted_Price": pred_price
    })
    
    # Update Window untuk loop selanjutnya (Recursive)
    last_hidden_state = current_batch[-1, 1] # Menggunakan hidden state terakhir
    new_row = np.array([[pred_price, last_hidden_state]])
    
    current_batch = np.vstack([current_batch[1:], new_row])

pd.DataFrame(future_results).to_csv(FORECAST_CSV, index=False)
print(f"✅ Future forecast saved to: {FORECAST_CSV}")