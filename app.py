import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

def load_data(ticker):
    local_tickers = ['EURUSD', 'EURGBP', 'GBPUSD']  # List of tickers available locally
    base_url = "https://raw.githubusercontent.com/NVT-RishikeshMahadevan/Datasets_algotrading_freedata/refs/heads/rishi/"
    
    if ticker in local_tickers:
        # Load data from local files
        return pd.read_csv(r"C:\Users\rishi\Downloads\{ticker}.csv")  # Adjust path as needed
    else:
        # Load data from the online repository
        return pd.read_csv(f"{base_url}{ticker}.csv")
        
def main():
    st.title("RSI Trading Strategy Dashboard")
    
    # User inputs in sidebar
    st.sidebar.header("Strategy Parameters")
    
    # Ticker selection
    ticker_options = ['SPY', 'QQQ', 'META', 'AMZN', 'MSFT', 'NVDA','EURUSD','EURGBP','GBPUSD']
    ticker = st.sidebar.selectbox("Select Ticker", ticker_options)
    
    # Strategy parameters
    initial_capital = st.sidebar.number_input("Initial Capital ($)", value=1000000, step=100000)
    trade_fraction = st.sidebar.number_input("Trading Capital Percentage (%)", value=25, min_value=0, max_value=100) / 100
    stoploss_percent = st.sidebar.number_input("Stoploss Percentage (%)", value=0.5, min_value=0.001, max_value=100.0, format="%.2f") / 100
    kill_switch = st.sidebar.checkbox("Enable Kill Switch")

    if st.sidebar.button("Run Strategy"):
        with st.spinner("Loading and processing data..."):
            # Load data
            df = load_data(ticker)
            
            # Data processing
            df['datetime'] = pd.to_datetime(df['t'], unit='ms', utc=True)
            est = pytz.timezone('US/Eastern')
            df['datetime_est'] = df['datetime'].dt.tz_convert(est)

            # RSI calculation
            window_length = 14
            delta = df['c'].diff()
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            avg_gain = gains.rolling(window=window_length, min_periods=window_length).mean()
            avg_loss = losses.rolling(window=window_length, min_periods=window_length).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            df['RSI'] = rsi
            df.loc[:window_length - 1, 'RSI'] = None

            # Time filtering
            df['time_est'] = df['datetime_est'].dt.time
            start_time = datetime.strptime("09:30:00", "%H:%M:%S").time()
            end_time = datetime.strptime("16:00:00", "%H:%M:%S").time()
            df['date'] = df['datetime_est'].dt.date
            df['date'] = pd.to_datetime(df['date'])
            df1 = df[(df['time_est'] >= start_time) & (df['time_est'] <= end_time)]
            df1 = df1.reset_index(drop=True)

            # Your existing trading logic
            # [All the portfolio management code remains exactly the same]
            df1['cash'] = initial_capital
            df1['shares'] = 0
            df1['portfolio_value'] = initial_capital
            df1['signal'] = ''
            df1['stoploss'] = 0

            current_cash = initial_capital
            current_shares = 0
            stoploss_hit = False
            prev_date = None
            stoploss_limit = initial_capital * stoploss_percent
            prev_portfolio_value = initial_capital
            kill_switch_triggered_date = None
            skip_trading_today = False

            # Trading loop
            total_rows = len(df1)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Get the last minute for each trading day
            last_minutes = df1.groupby('date')['datetime_est'].transform('max')
            
            for i, row in enumerate(df1.iterrows()):
                # Update progress every 100 rows
                if i % 100 == 0:
                    progress = int((i / total_rows) * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing trades... {progress}% ({i}/{total_rows} rows)")
                
                price = row[1]['c']
                rsi = row[1]['RSI']
                current_date = row[1]['date']
                current_datetime = row[1]['datetime_est']

                # Check if it's the last minute of trading day
                if current_datetime == last_minutes[i] and current_shares > 0:
                    current_cash += current_shares * price
                    current_shares = 0
                    df1.loc[i, 'signal'] = 'S'  # Mark as sell signal for visualization
                
                if kill_switch_triggered_date and current_date != kill_switch_triggered_date:
                    skip_trading_today = False
                    stoploss_hit = False
                    prev_portfolio_value = current_cash + current_shares * price
                    kill_switch_triggered_date = None

                portfolio_value = current_cash + current_shares * price

                # Only allow new trades if not in last minute
                if current_datetime != last_minutes[i]:
                    if not stoploss_hit and portfolio_value - prev_portfolio_value < -stoploss_limit:
                        stoploss_hit = True
                        df1.loc[i, 'stoploss'] = 1
                        current_cash += current_shares * price
                        current_shares = 0

                        if kill_switch:
                            skip_trading_today = True
                            kill_switch_triggered_date = current_date
                            df1.loc[i, 'cash'] = current_cash
                            df1.loc[i, 'shares'] = current_shares
                            df1.loc[i, 'portfolio_value'] = current_cash + current_shares * price
                            prev_portfolio_value = current_cash
                            prev_date = current_date
                            continue
                        else:
                            df1.loc[i, 'cash'] = current_cash
                            df1.loc[i, 'shares'] = current_shares
                            df1.loc[i, 'portfolio_value'] = current_cash + current_shares * price
                            prev_portfolio_value = current_cash
                            continue

                    if not stoploss_hit and rsi < 30:
                        trade_cash = initial_capital * trade_fraction
                        shares_to_buy = trade_cash // price
                        cost = shares_to_buy * price

                        if current_cash >= cost and shares_to_buy > 0:
                            current_cash -= cost
                            current_shares += shares_to_buy
                            df1.loc[i, 'signal'] = 'B'

                    if not stoploss_hit and rsi > 70 and current_shares > 0:
                        current_cash += current_shares * price
                        current_shares = 0
                        df1.loc[i, 'signal'] = 'S'

                df1.loc[i, 'cash'] = current_cash
                df1.loc[i, 'shares'] = current_shares
                df1.loc[i, 'portfolio_value'] = current_cash + current_shares * price

                prev_portfolio_value = current_cash + current_shares * price

                if not kill_switch:
                    stoploss_hit = False

                prev_date = current_date

            # Complete the progress bar
            progress_bar.progress(100)
            status_text.text(f"Completed processing {total_rows} rows!")

            # Create summary DataFrame
            df2 = df1.groupby('date').tail(1)[['date', 'portfolio_value', 'c']].reset_index(drop=True)

            # Store data in session state for persistence
            st.session_state['df1'] = df1
            st.session_state['df2'] = df2
            st.session_state['ticker'] = ticker

            # Calculate and display metrics
            daily_returns = df2['portfolio_value'].pct_change()
            geometric_return = ((df2['portfolio_value'].iloc[-1] / df2['portfolio_value'].iloc[0]) ** (252 / len(df2)) - 1) * 100
            mean_daily_return = daily_returns.mean() * 252 * 100
            std_dev_daily_return = daily_returns.std() * np.sqrt(252) * 100
            sharpe_ratio = mean_daily_return / std_dev_daily_return

            # Store metrics in session state
            st.session_state['metrics'] = {
                'geometric_return': geometric_return,
                'mean_daily_return': mean_daily_return,
                'std_dev_daily_return': std_dev_daily_return,
                'sharpe_ratio': sharpe_ratio
            }

    # Display metrics and charts (outside the if statement)
    if 'metrics' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Geometric Return (%)", f"{st.session_state['metrics']['geometric_return']:.2f}")
            st.metric("Mean Daily Return (%)", f"{st.session_state['metrics']['mean_daily_return']:.2f}")
        with col2:
            st.metric("Standard Deviation (%)", f"{st.session_state['metrics']['std_dev_daily_return']:.2f}")
            st.metric("Sharpe Ratio", f"{st.session_state['metrics']['sharpe_ratio']:.2f}")

        # Overall performance chart
        st.subheader("Portfolio Performance")
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(st.session_state['df2']['date'], st.session_state['df2']['portfolio_value'], 
                color='blue', label='Portfolio Value')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Portfolio Value ($)', color='blue')
        
        ax2 = ax1.twinx()
        ax2.plot(st.session_state['df2']['date'], st.session_state['df2']['c'], 
                color='red', label='Stock Price')
        ax2.set_ylabel('Stock Price ($)', color='red')
        
        plt.title("RSI Trading Strategy Performance")
        st.pyplot(fig)
        plt.close()

        # Date selector for detailed analysis
        st.subheader("Daily Analysis")
        available_dates = st.session_state['df1']['date'].dt.date.unique()
        selected_date = st.date_input(
            "Select date for detailed analysis",
            min_value=available_dates[0],
            max_value=available_dates[-1],
            value=available_dates[0]
        )

        if selected_date:
            filtered_df = st.session_state['df1'][
                st.session_state['df1']['date'].dt.date == selected_date
            ]
            
            if not filtered_df.empty:
                fig, axs = plt.subplots(3, 1, figsize=(14, 12), 
                                      gridspec_kw={'height_ratios': [3, 1, 1]})
                plt.subplots_adjust(hspace=0.3)

                # Price and signals plot
                axs[0].plot(filtered_df['datetime_est'], filtered_df['portfolio_value'], 
                           label="Portfolio Value", color="blue")
                ax2 = axs[0].twinx()
                ax2.plot(filtered_df['datetime_est'], filtered_df['c'], 
                        label="Stock Price", color="orange")
                
                # Add buy/sell/stoploss signals
                buy_signals = filtered_df[filtered_df['signal'] == 'B']
                sell_signals = filtered_df[filtered_df['signal'] == 'S']
                stoploss_signals = filtered_df[filtered_df['stoploss'] == 1]
                
                ax2.scatter(buy_signals['datetime_est'], buy_signals['c'], 
                          color='green', marker='^', s=100, label='Buy')
                ax2.scatter(sell_signals['datetime_est'], sell_signals['c'], 
                          color='red', marker='v', s=100, label='Sell')
                ax2.scatter(stoploss_signals['datetime_est'], stoploss_signals['c'], 
                          color='black', marker='s', s=100, label='Stoploss')

                # Add legends
                lines1, labels1 = axs[0].get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

                # RSI plot
                axs[1].plot(filtered_df['datetime_est'], filtered_df['RSI'], color='purple')
                axs[1].axhline(y=70, color='r', linestyle='--')
                axs[1].axhline(y=30, color='g', linestyle='--')
                axs[1].set_title('RSI')
                axs[1].set_ylim(0, 100)

                # Portfolio allocation
                cash_allocation = filtered_df['cash']
                share_value = filtered_df['shares'] * filtered_df['c']
                axs[2].stackplot(filtered_df['datetime_est'], 
                               [cash_allocation, share_value],
                               labels=['Cash', 'Shares'],
                               colors=['lightblue', 'orange'])
                axs[2].set_title('Portfolio Allocation')
                axs[2].legend()

                # Set title and adjust layout
                axs[0].set_title(f'Trading Activity on {selected_date.strftime("%Y-%m-%d")}')
                plt.tight_layout()

                st.pyplot(fig)
                plt.close()
            else:
                st.warning("No data available for selected date.")

if __name__ == "__main__":
    main()
