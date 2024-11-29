# RSI_Trading_Backtesting_Neo

**URL**: [RSI Trading Backtesting Neo](https://rsitradingbacktestingneo-baqc8ycektyj8bntyjz9my.streamlit.app/)

---

## Core Strategy
- Utilizes **Relative Strength Index (RSI)** with a 14-period window.
- Focuses exclusively on **day trading**—no overnight positions.
- All positions are liquidated at the **end of each trading day**.

---

## Entry/Exit Rules

### **Buy Signal (Entry)**
- Triggered when **RSI drops below 30** (oversold condition).
- Uses a **fixed percentage of initial capital** for each trade.
- Enters only if **sufficient cash** is available.

### **Sell Signal (Exit)**
- Triggered when **RSI rises above 70** (overbought condition).
- Sells the **entire position**.
- **Mandatory exit** at the end of the trading day.

---

## Risk Management

### **Stoploss Protection**
- Monitors portfolio value drops.
- Exits all positions if the loss exceeds the **stoploss threshold**.
- **Stoploss percentage** is customizable.

### **Kill Switch Feature**
- An optional risk management tool.
- When enabled, stops trading for the rest of the day if the **stoploss** is hit.
- Resets for the **next trading day**.

---

## Parameters (Customizable)
- **Initial Capital**: Starting portfolio value.
- **Trading Capital Percentage**: Portion of capital used per trade.
- **Stoploss Percentage**: Maximum allowed loss before forced exit.
- **Kill Switch**: Toggle for additional risk management.
