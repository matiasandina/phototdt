import pandas as pd
import tdt
import os
from phototdt import get_tdt_data, calculate_zdFF

import tkinter as tk
from tkinter import filedialog

def tdt_to_csv(folder_path=None):
	if folder_path is None:
		root = tk.Tk()
		root.withdraw()
		home = os.path.expanduser('~')
		folder_path = filedialog.askdirectory(initialdir = home)

	photo_data = get_tdt_data(folder_path, remove_start=False)
	photo_data = calculate_zdFF(photo_data)
	home = os.path.expanduser('~')
	filename = filedialog.asksaveasfilename(title="Type filename to save",
		filetypes = (("csv files","*.csv.gz"),("all files","*.*")),
		initialdir = folder_path)
	photo_data.to_csv(filename, index=False)
