import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np

class StockAlphaEngine:

    def __init__(self, root):
        self.root = root
        self.root.title("Quantitative Rotation Engine - Comparative Edition")
        self.root.geometry("1100x880") # Expanded for the new indicator columns
        self.root.configure(bg="#1e1e24")

        # Configure dark theme styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#1e1e24", foreground="#efefef", font=("Arial", 10))
        self.style.configure("TFrame", background="#1e1e24")
        self.style.configure("TButton", font=("Arial", 10, "bold"), background="#2a2a35", foreground="#efefef", borderwidth=1)
        self.style.map("TButton", background=[("active", "#3a3a45")], foreground=[("active", "#ffffff")])

        self.csv_folder = tk.StringVar()
        self.selected_file = tk.StringVar()

        self.create_widgets()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # --- Top Header ---
        header = tk.Label(
            self.root,
            text="COMPARATIVE ALGO ENGINE [SMA vs EMA vs HMA]",
            font=("Arial", 14, "bold"),
            bg="#1e1e24",
            fg="#00ffcc",
        )
        header.pack(pady=15)

        # --- Input Configuration Frame ---
        config_frame = ttk.LabelFrame(self.root, text=" Strategy Configuration ", padding=15)
        config_frame.pack(fill="x", padx=20, pady=5)

        # Row 0: Capital & Target Settings
        ttk.Label(config_frame, text="Target Capital (PLN):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.capital_entry = ttk.Entry(config_frame, width=15)
        self.capital_entry.insert(0, "100000")
        self.capital_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(config_frame, text="Buy Dip Threshold (%):").grid(row=0, column=2, sticky="w", padx=15, pady=5)
        self.dip_entry = ttk.Entry(config_frame, width=10)
        self.dip_entry.insert(0, "0.4")
        self.dip_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Row 1: Target & Risk Settings
        ttk.Label(config_frame, text="Profit Target (%):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.target_entry = ttk.Entry(config_frame, width=15)
        self.target_entry.insert(0, "1.2")
        self.target_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Liquidity Protection Parameter
        ttk.Label(config_frame, text="Max Vol Impact (% of 5m Median):").grid(row=1, column=2, sticky="w", padx=15, pady=5)
        self.impact_entry = ttk.Entry(config_frame, width=10)
        self.impact_entry.insert(0, "20.0")
        self.impact_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Row 2: Broker Fee & Tax
        ttk.Label(
            config_frame,
            text="Friction: 0.30% Broker Fee | 19% Capital Gains Tax included in Net calculations.",
            font=("Arial", 9, "italic"),
            foreground="#aaa",
        ).grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky="w")

        # --- File Selection Frame ---
        file_frame = ttk.LabelFrame(self.root, text=" Data Source Selection ", padding=15)
        file_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(file_frame, text="Select Data Folder", command=self.browse_folder).grid(row=0, column=0, padx=5, pady=5)
        self.folder_label = ttk.Label(file_frame, text="No folder selected", wraplength=450, foreground="#aaa")
        self.folder_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(file_frame, text="Available CSV Files:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.file_dropdown = ttk.Combobox(file_frame, textvariable=self.selected_file, width=40, state="readonly")
        self.file_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # --- Action Buttons ---
        btn_frame = tk.Frame(self.root, bg="#1e1e24")
        btn_frame.pack(pady=10)

        self.run_btn = tk.Button(
            btn_frame,
            text="ANALYZE SELECTED STOCK",
            font=("Arial", 11, "bold"),
            bg="#00ffcc",
            fg="#1e1e24",
            activebackground="#00ccaa",
            command=self.run_single_simulation,
            padx=15,
            pady=8,
            relief="flat",
        )
        self.run_btn.grid(row=0, column=0, padx=10)

        self.batch_btn = tk.Button(
            btn_frame,
            text="EXECUTE BATCH ANALYSIS",
            font=("Arial", 11, "bold"),
            bg="#ffaa00",
            fg="#1e1e24",
            activebackground="#cc8800",
            command=self.run_batch_simulation,
            padx=15,
            pady=8,
            relief="flat",
        )
        self.batch_btn.grid(row=0, column=1, padx=10)

        # --- Results Dashboard ---
        results_frame = ttk.LabelFrame(self.root, text=" Comparative Simulation Matrix ", padding=15)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 3-Way Metrics Dashboard
        self.metrics_frame = tk.Frame(results_frame, bg="#2a2a35")
        self.metrics_frame.pack(fill="x", pady=(0, 10))

        # Define grid layout for dashboard
        self.metrics_frame.columnconfigure(0, weight=1)
        self.metrics_frame.columnconfigure(1, weight=1)
        self.metrics_frame.columnconfigure(2, weight=1)

        self.sma_lbl = tk.Label(self.metrics_frame, text="[SMA] Profit: -- PLN | Win Rate: --% | Trades: --", bg="#2a2a35", fg="#00ffcc", font=("Arial", 10, "bold"), pady=5)
        self.sma_lbl.grid(row=0, column=0, sticky="nsew")

        self.ema_lbl = tk.Label(self.metrics_frame, text="[EMA] Profit: -- PLN | Win Rate: --% | Trades: --", bg="#2a2a35", fg="#ffaa00", font=("Arial", 10, "bold"), pady=5)
        self.ema_lbl.grid(row=0, column=1, sticky="nsew")

        self.hma_lbl = tk.Label(self.metrics_frame, text="[HMA] Profit: -- PLN | Win Rate: --% | Trades: --", bg="#2a2a35", fg="#ff5555", font=("Arial", 10, "bold"), pady=5)
        self.hma_lbl.grid(row=0, column=2, sticky="nsew")

        # Liquidity Display Board
        self.liquidity_label = tk.Label(
            results_frame,
            text="Median 5m Volume: -- PLN   |   Actual Capital Deployed: -- PLN",
            font=("Arial", 10, "italic"),
            bg="#1e1e24",
            fg="#aaa",
        )
        self.liquidity_label.pack(fill="x", pady=(0, 5))

        # Trade Log Treeview (Added Indicator Column)
        columns = ("datetime", "ticker", "indicator", "action", "price", "shares", "net_profit")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        self.tree.heading("datetime", text="Date/Time")
        self.tree.heading("ticker", text="Ticker")
        self.tree.heading("indicator", text="Logic")
        self.tree.heading("action", text="Action")
        self.tree.heading("price", text="Price")
        self.tree.heading("shares", text="Volume")
        self.tree.heading("net_profit", text="Net Profit")

        self.tree.column("datetime", width=140, anchor="center")
        self.tree.column("ticker", width=70, anchor="center")
        self.tree.column("indicator", width=60, anchor="center")
        self.tree.column("action", width=70, anchor="center")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("shares", width=90, anchor="e")
        self.tree.column("net_profit", width=150, anchor="e")

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.csv_folder.set(folder)
            self.folder_label.config(text=folder, foreground="#efefef")
            csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
            if csv_files:
                self.file_dropdown["values"] = csv_files
                self.file_dropdown.current(0)
            else:
                self.file_dropdown["values"] = []
                self.selected_file.set("")
                messagebox.showwarning("No CSV Files", "No .csv files found in selected folder.")

    def calculate_wma(self, series, window):
        """Helper to calculate Weighted Moving Average"""
        window = max(1, int(window))
        weights = np.arange(1, window + 1)
        return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

    def core_strategy_engine(self, filepath, target_capital, dip_pct, target_pct, impact_pct, indicator="SMA"):
        """ Runs a single strategy based on the indicator passed """
        try:
            df = pd.read_csv(filepath, header=None)
            df.columns = ["Date", "Time", "Price", "Volume", "Type"]
            df["Time_str"] = df["Time"].astype(str).str.zfill(6)
            df["Datetime"] = pd.to_datetime(df["Date"].astype(str) + df["Time_str"], format="%y%m%d%H%M%S")
            df.set_index("Datetime", inplace=True)

            # Capacity Limits
            df["Value_PLN"] = df["Price"] * df["Volume"]
            df_5m_val = df["Value_PLN"].resample("5min").sum()
            df_5m_val = df_5m_val[df_5m_val > 0]
            median_5m_liquidity = df_5m_val.median() if not df_5m_val.empty else 0
            
            safe_capacity = median_5m_liquidity * impact_pct
            deployed_capital = min(target_capital, safe_capacity)
            
            # Indicator Setup
            df_resampled = df["Price"].resample("5min").agg("last").dropna()
            
            if indicator == "SMA":
                signal_line = df_resampled.rolling(window=5).mean()
            elif indicator == "EMA":
                signal_line = df_resampled.ewm(span=5, adjust=False).mean()
            elif indicator == "HMA":
                half_length = max(1, int(5 / 2))
                sqrt_length = max(1, int(np.sqrt(5)))
                wmaf = self.calculate_wma(df_resampled, half_length)
                wmas = self.calculate_wma(df_resampled, 5)
                signal_line = self.calculate_wma(2 * wmaf - wmas, sqrt_length)

            capital = deployed_capital
            position = 0
            buy_price = 0
            total_trades = 0
            winning_trades = 0
            cumulative_profit = 0.0
            trade_logs = []

            for i in range(5, len(df_resampled)):
                price = df_resampled.iloc[i]
                dt = df_resampled.index[i]

                # BUY SIGNAL
                if price < signal_line.iloc[i] * (1 - dip_pct) and position == 0:
                    shares = int(capital / (price * 1.003)) 
                    if shares > 0:
                        buy_cost = shares * price
                        entry_fee = buy_cost * 0.003
                        capital -= (buy_cost + entry_fee)

                        position = shares
                        buy_price = price
                        
                        trade_logs.append((dt.strftime("%Y-%m-%d %H:%M"), indicator, "BUY", price, shares, 0.0))

                # SELL SIGNAL
                elif price > buy_price * (1 + target_pct) and position > 0:
                    gross_revenue = position * price
                    exit_fee = gross_revenue * 0.003

                    total_entry_cost = (position * buy_price) * 1.003
                    gross_profit = gross_revenue - exit_fee - total_entry_cost

                    tax = gross_profit * 0.19 if gross_profit > 0 else 0
                    net_profit = gross_profit - tax

                    capital += (gross_revenue - exit_fee - tax)
                    cumulative_profit += net_profit
                    total_trades += 1
                    if net_profit > 0:
                        winning_trades += 1

                    trade_logs.append((dt.strftime("%Y-%m-%d %H:%M"), indicator, "SELL", price, position, net_profit))
                    position = 0 

            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            return trade_logs, cumulative_profit, win_rate, total_trades, deployed_capital, median_5m_liquidity

        except Exception as e:
            return None, 0.0, 0.0, 0, 0.0, 0.0

    def update_dashboard_labels(self, results):
        """ Updates the 3-way color-coded dashboard """
        self.sma_lbl.config(text=f"[SMA] Profit: {results['SMA']['profit']:.2f} PLN | Win Rate: {results['SMA']['win_rate']:.1f}% | Trades: {results['SMA']['trades']}")
        self.ema_lbl.config(text=f"[EMA] Profit: {results['EMA']['profit']:.2f} PLN | Win Rate: {results['EMA']['win_rate']:.1f}% | Trades: {results['EMA']['trades']}")
        self.hma_lbl.config(text=f"[HMA] Profit: {results['HMA']['profit']:.2f} PLN | Win Rate: {results['HMA']['win_rate']:.1f}% | Trades: {results['HMA']['trades']}")

    def run_single_simulation(self):
        folder = self.csv_folder.get()
        filename = self.selected_file.get()

        if not folder or not filename:
            messagebox.showerror("Error", "Please select a folder and a file.")
            return

        try:
            target_capital = float(self.capital_entry.get())
            dip_pct = float(self.dip_entry.get()) / 100.0
            target_pct = float(self.target_entry.get()) / 100.0
            impact_pct = float(self.impact_entry.get()) / 100.0
        except ValueError:
            messagebox.showerror("Error", "Check your parameter inputs.")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        filepath = os.path.join(folder, filename)
        ticker = filename.replace(".csv", "").upper()
        
        all_logs = []
        results = {"SMA": {}, "EMA": {}, "HMA": {}}
        med_vol_val = 0.0
        dep_cap_val = 0.0

        for ind in ["SMA", "EMA", "HMA"]:
            logs, cum_profit, win_rate, trades, deployed_capital, med_vol = self.core_strategy_engine(filepath, target_capital, dip_pct, target_pct, impact_pct, indicator=ind)
            if logs is not None:
                all_logs.extend(logs)
                results[ind] = {"profit": cum_profit, "win_rate": win_rate, "trades": trades}
                med_vol_val = med_vol
                dep_cap_val = deployed_capital
            else:
                messagebox.showerror("Data Error", f"Could not process {ind} for this CSV.")
                return

        # Sort combined logs chronologically
        all_logs.sort(key=lambda x: x[0])

        report_lines = [
            f"--- COMPARATIVE REPORT: {ticker} ---",
            f"Parameters: Buy Dip {dip_pct*100}% | Target {target_pct*100}%",
            f"Target Capital: {target_capital} PLN",
            "--------------------------------------------------",
            f"Median 5m Volume: {med_vol_val:.2f} PLN | DEPLOYED CAP: {dep_cap_val:.2f} PLN",
            "--------------------------------------------------\n",
            "--- COMBINED CHRONOLOGICAL TRADE LOG ---"
        ]

        for log in all_logs:
            dt, ind, action, price, shares, net = log
            net_str = f"+{net:.2f} PLN" if action == "SELL" else "--"
            self.tree.insert("", "end", values=(dt, ticker, ind, action, f"{price:.2f}", shares, net_str))
            report_lines.append(f"{dt} | [{ind}] | {action.ljust(4)} | Price: {price:.2f} | Shares: {shares} | Net Profit: {net_str}")

        self.update_dashboard_labels(results)
        self.liquidity_label.config(text=f"Median 5m Volume: {med_vol_val:.2f} PLN   |   Actual Capital Deployed: {dep_cap_val:.2f} PLN")
        
        report_lines.append("\n--- STRATEGY PERFORMANCE COMPARISON ---")
        for ind in ["SMA", "EMA", "HMA"]:
            report_lines.append(f"[{ind}] Net Profit: {results[ind]['profit']:.2f} PLN | Win Rate: {results[ind]['win_rate']:.1f}% | Trades: {results[ind]['trades']}")

        output_path = os.path.join(folder, f"{ticker}_comparative.txt")
        with open(output_path, "w") as f:
            f.write("\n".join(report_lines))
            
        messagebox.showinfo("Export Complete", f"Comparative simulation finished. Report saved to:\n{output_path}")

    def run_batch_simulation(self):
        folder = self.csv_folder.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder containing CSV files.")
            return

        try:
            target_capital = float(self.capital_entry.get())
            dip_pct = float(self.dip_entry.get()) / 100.0
            target_pct = float(self.target_entry.get()) / 100.0
            impact_pct = float(self.impact_entry.get()) / 100.0
        except ValueError:
            messagebox.showerror("Error", "Check your parameter inputs.")
            return

        csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
        if not csv_files: return

        for item in self.tree.get_children():
            self.tree.delete(item)

        master_report = [
            "==================================================",
            "        PORTFOLIO BATCH COMPARISON REPORT         ",
            "==================================================",
            f"Parameters: Buy Dip {dip_pct*100}% | Sell Target {target_pct*100}%",
            "Friction applied: 0.30% Round-trip Fee + 19% Belka Tax\n\n"
        ]

        grand_totals = {
            "SMA": {"profit": 0.0, "trades": 0, "wins": 0},
            "EMA": {"profit": 0.0, "trades": 0, "wins": 0},
            "HMA": {"profit": 0.0, "trades": 0, "wins": 0}
        }

        for file in csv_files:
            filepath = os.path.join(folder, file)
            ticker = file.replace(".csv", "").upper()
            master_report.append(f"--- TICKER: {ticker} ---")
            
            ticker_logs = []
            for ind in ["SMA", "EMA", "HMA"]:
                logs, cum_profit, win_rate, trades, deployed_capital, med_vol = self.core_strategy_engine(filepath, target_capital, dip_pct, target_pct, impact_pct, indicator=ind)
                
                if logs is None: continue 
                ticker_logs.extend(logs)
                
                grand_totals[ind]["profit"] += cum_profit
                grand_totals[ind]["trades"] += trades
                if trades > 0:
                    grand_totals[ind]["wins"] += int(trades * (win_rate/100))

                master_report.append(f"[{ind}] Profit: {cum_profit:.2f} | Win Rate: {win_rate:.1f}% | Trades: {trades}")
            
            master_report.append("") # spacer
            
            ticker_logs.sort(key=lambda x: x[0])
            for log in ticker_logs:
                dt, ind, action, price, shares, net = log
                net_str = f"+{net:.2f} PLN" if action == "SELL" else "--"
                self.tree.insert("", "end", values=(dt, ticker, ind, action, f"{price:.2f}", shares, net_str))

        # Calculate combined win rates
        for ind in ["SMA", "EMA", "HMA"]:
            t_trades = grand_totals[ind]["trades"]
            grand_totals[ind]["win_rate"] = (grand_totals[ind]["wins"] / t_trades * 100) if t_trades > 0 else 0.0

        master_report.append("==================================================")
        master_report.append("             PORTFOLIO GRAND TOTALS               ")
        master_report.append("==================================================")
        for ind in ["SMA", "EMA", "HMA"]:
             master_report.append(f"[{ind}] TOTAL PROFIT: {grand_totals[ind]['profit']:.2f} PLN | OVERALL WIN RATE: {grand_totals[ind]['win_rate']:.1f}% | TOTAL TRADES: {grand_totals[ind]['trades']}")

        output_path = os.path.join(folder, "batch_comparison.txt")
        with open(output_path, "w") as f:
            f.write("\n".join(master_report))

        self.update_dashboard_labels(grand_totals)
        self.liquidity_label.config(text=f"Batch Mode Active: 3-Way Comparative Analysis Complete.")
        
        messagebox.showinfo("Batch Complete", f"Successfully analyzed {len(csv_files)} files.\nMaster report saved to:\n{output_path}")

    def on_closing(self):
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass
        finally:
            os._exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAlphaEngine(root)
    root.mainloop()
