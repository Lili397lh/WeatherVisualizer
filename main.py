import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import pandas as pd
from Functions import *
import numpy as np

#Principal window
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Last 12h AEMET Stations")
        self.geometry("1200x800")

        # Station selected
        self.selected_estation = tk.StringVar()
        
        # DataFrame stations inventory
        self.station_names = stations_inventory()
        
        # Widgets
        self.widgets()
        
    def widgets(self):
        # Combobox station selection
        self.stations_combobox()

        # Empty plots
        self.empty_plots()
        
    def stations_combobox(self):
        self.frame_combo_button = ttk.Frame(self)
        self.frame_combo_button.pack(anchor='w', padx=(10,0))
        
        self.label = ttk.Label(self.frame_combo_button, text="Select a station:")
        self.label.pack(side='left')

        station_names = list(self.station_names["nombre"])
        self.combobox = ttk.Combobox(self.frame_combo_button, textvariable=self.selected_estation, values=station_names, state="readonly")
        self.combobox.pack(side='left', padx=(10,0))

        self.button = ttk.Button(self.frame_combo_button, text="Select", command=self.on_select)
        self.button.pack(side='left', padx=(10,0))     
    
    def empty_plots(self):
        import numpy as np
        # Create figure
        self.fig = plt.figure(figsize=(10, 8))

        # Create subplots
        self.axs = [[None, None], [None, None]]
        self.axs[0][0] = self.fig.add_subplot(2, 2, 1)
        self.axs[0][1] = self.fig.add_subplot(2, 2, 2)
        self.axs[1][0] = self.fig.add_subplot(2, 2, 3)
        self.axs[1][1] = self.fig.add_subplot(2, 2, 4, polar=True)
        self.axs = np.array(self.axs)

        # Top left
        self.axs[0, 0].set_title("Temperature")
        self.axs[0, 0].set_xlabel("Time")
        self.axs[0, 0].set_ylabel("Temperature (°C)")

        # Top right
        self.axs[0, 1].set_title("Humidity")
        self.axs[0, 1].set_xlabel("Time")
        self.axs[0, 1].set_ylabel("Humidity (%)")

        # Bottom left
        self.axs[1, 0].set_title("Wind Speed")
        self.axs[1, 0].set_xlabel("Time")
        self.axs[1, 0].set_ylabel("Wind Speed (m/s)")

        # Bottom right
        self.axs[1, 1].set_title("Wind Direction")

        # Spacing between rows
        self.fig.subplots_adjust(hspace=0.5)

        # Embed in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Empty plots
        self.update_plots(pd.DataFrame())  
        
    def on_select(self):
        selection = self.selected_estation.get()
        row = self.station_names[self.station_names["nombre"] == selection]
        if not row.empty:
            indicativo = row["indicativo"].values[0]
            store_selected_station(indicativo)
        else:
            print("Station not found")

        data = station_met_data()
        self.update_plots(data)
    
    def update_plots(self, data):
        # Clear all plots
        for ax in self.axs.flat:
            ax.clear()

        if not data.empty:
            # Adjust column names based on actual data
            if 'ta' in data.columns:
                self.axs[0, 0].plot(data['datetime'], data['tamax'], color="#010c14", label='T max')
                self.axs[0, 0].plot(data['datetime'], data['ta'], color='#1f77b4', label='T mean')
                self.axs[0, 0].plot(data['datetime'], data['tamin'], color='#4c9cd9', label='T min')
                self.axs[0, 0].set_title("Temperature")
                self.axs[0, 0].set_xlabel("Time (h)")
                self.axs[0, 0].set_ylabel("Temperature (°C)")
                self.axs[0, 0].xaxis.set_major_formatter(DateFormatter('%H'))
                self.axs[0, 0].legend()

            if 'hr' in data.columns:
                self.axs[0, 1].plot(data['datetime'], data['hr'], label='Humidity', color='orange')
                self.axs[0, 1].set_title("Humidity")
                self.axs[0, 1].set_xlabel("Time (h)")
                self.axs[0, 1].set_ylabel("Humidity (%)")
                self.axs[0, 1].xaxis.set_major_formatter(DateFormatter('%H'))
                self.axs[0, 1].legend()

            if 'vv' in data.columns:
                self.axs[1, 0].plot(data['datetime'], data['vv'], label='Wind', color='green')
                self.axs[1, 0].set_title("Wind Speed")
                self.axs[1, 0].set_xlabel("Time (h)")
                self.axs[1, 0].set_ylabel("Wind Speed (m/s)")
                self.axs[1, 0].xaxis.set_major_formatter(DateFormatter('%H'))
                self.axs[1, 0].legend()

            # For polar plot, assuming 'dv' is wind direction in degrees
            data = wind_rose()
            if 'frecuencia' in data.columns:
                self.axs[1, 1].set_title("Wind Direction")
                # Convert sectors to radians for theta
                theta = np.deg2rad(data['sectors'])
                r = data['frecuencia']
                # Plot as polar bar chart
                self.axs[1, 1].bar(theta, r, width=np.deg2rad(22.5), bottom=0.0, alpha=0.8, color='blue', edgecolor='black')
        else:
            # Set titles for empty plots
            self.axs[0, 0].set_title("Temperature")
            self.axs[0, 0].set_xlabel("Time")
            self.axs[0, 0].set_ylabel("Temperature (°C)")

            self.axs[0, 1].set_title("Humidity")
            self.axs[0, 1].set_xlabel("Time")
            self.axs[0, 1].set_ylabel("Humidity (%)")

            self.axs[1, 0].set_title("Wind Speed")
            self.axs[1, 0].set_xlabel("Time")
            self.axs[1, 0].set_ylabel("Wind Speed (m/s)")

            self.axs[1, 1].set_title("Wind Direction")

        self.canvas.draw() 
        

if __name__ == "__main__":
    app = App()
    app.mainloop()