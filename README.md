# RSI_Trading_backtesting_neo

URL : https://rsitradingbacktestingneo-baqc8ycektyj8bntyjz9my.streamlit.app/

Core Strategy:
Uses Relative Strength Index (RSI) with a 14-period window
Day trading only - no overnight positions
All positions are liquidated at the end of each trading day

Entry/Exit Rules:
Buy Signal (Entry):
RSI drops below 30 (oversold condition)
Uses fixed percentage of initial capital for each trade
Only enters if sufficient cash is available


Sell Signal (Exit):
RSI rises above 70 (overbought condition)
Sells entire position
Mandatory exit at end of trading day

Risk Management:
Stoploss Protection:
Monitors portfolio value drops
Exits all positions if loss exceeds stoploss threshold
Stoploss percentage is customizable


Kill Switch Feature:
Optional risk management tool
When enabled, stops trading for the rest of the day if stoploss is hit
Resets for next trading day


Parameters (Customizable):
Initial Capital: Starting portfolio value
Trading Capital Percentage: Portion of capital used per trade
Stoploss Percentage: Maximum allowed loss before forced exit
Kill Switch: Toggle for additional risk management
