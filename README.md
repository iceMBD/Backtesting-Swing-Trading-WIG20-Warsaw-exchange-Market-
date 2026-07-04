


**⚠️ Disclaimer: You are welcome to use, fork, and explore this code with your team. However, this software is provided "as is" with no guarantees or warranties that it will work as expected. This project was built strictly for educational and entertainment purposes. Do not use this engine for live financial trading with real capital.**




# Backtesting-Swing-Trading-WIG20-Warsaw-exchange-Market-
A lightweight Backtesting Swing Trading WIG20, high-frequency backtesting engine with a Tkinter graphical interface. This tool allows users to simulate and compare "buy-the-dip" mean-reversion strategies using three distinct mathematical indicators: Simple Moving Average (SMA), Exponential Moving Average (EMA), and the Hull Moving Average (HMA).




📂 **[Download the sample dataset from here](https://github.com/iceMBD/Warsaw-Exchange-stock-market-WIG20-CSV-GPW-QuantSandbox)**






**The Core Trading Logic**

Regardless of the specific algorithm being used, the underlying strategy acts on the following rules:

Risk & Liquidity Management: Before making a trade, the engine calculates the median trading volume for the stock over 5-minute windows. It restricts your trade size to a maximum percentage of that volume (default 20%) so that your simulated trades wouldn't artificially crash or pump the real market.

The Buy Signal: The engine calculates a "Signal Line" (a moving average). If the current stock price drops below that line by your defined Buy Dip Threshold (e.g., 0.4%), it triggers a buy order.

The Sell Signal: Once holding shares, the engine waits until the stock price rises above your original buy price by your defined Profit Target (e.g., 1.2%). Once hit, it sells everything.

Friction: Every buy and sell deducts a 0.3% broker fee. Every profitable sell deducts a 19% tax from the gross profit before updating your capital.


**The Algorithms Used**

To determine that "Signal Line" to buy the dip against, the engine runs three distinct algorithms side-by-side to see which performs best. All three are calculated using a 5-period window on 5-minute data chunks:

1. **SMA (Simple Moving Average)**
How it works: It takes the closing prices of the last 5 periods, adds them up, and divides by 5.

Role: This is your baseline algorithm. It's slow to react to sudden price changes but provides a smooth, reliable trendline.

2. **EMA (Exponential Moving Average)**
How it works: Similar to the SMA, but it applies a mathematical multiplier to give more "weight" to the most recent prices.

Role: It reacts to sudden market drops or spikes much faster than the SMA, potentially getting you into a dip-buy slightly earlier.

3. **HMA (Hull Moving Average)**
How it works: This is the most complex algorithm in the script. It attempts to eliminate the "lag" associated with moving averages while keeping the line perfectly smooth. It uses Weighted Moving Averages (WMA) combined in a specific formula: <img width="486" height="51" alt="image" src="https://github.com/user-attachments/assets/5e2dca70-b92a-4bd7-9c52-ea0855ed523a" />




<img width="1895" height="1036" alt="image" src="https://github.com/user-attachments/assets/e04167e7-c864-47bc-bfc1-8a534b4681fe" />






**The Output**


You can run this against a single stock or execute a Batch Analysis across an entire folder of stocks. The script populates a visual dashboard with the Win Rate, Number of Trades, and Net Profit (in PLN) for the SMA, EMA, and HMA separately, and exports a highly detailed chronological .txt ledger of every trade made.






<img width="648" height="971" alt="image" src="https://github.com/user-attachments/assets/291cddfa-f270-4f6c-9798-2204c50725e8" />



