import tkinter as tk
from tkinter import font, filedialog, messagebox
import pandas as pd
import os
import sys
from util import *


class MainApplication(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.setup_interface(master)
        self.input_fname = None
        self.filter_fname = None

    # Set up button click methods
    def on_select_input_file(self):
        self.input_fname = filedialog.askopenfilename(title="Select File")
        if self.input_fname and self.input_fname.split('.')[-1] == 'txt':
            self.input_file_text.config(
                text=self.input_fname.split('/')[-1])
        else:
            messagebox.showerror(
                title="Error",
                message="Something went wrong, did you select an appropriately input file?")
            return
        self.run_filter_button.config(state='normal')
        self.filter_file_button.config(state='normal')

    def on_select_filter_file(self):
        self.filter_fname = filedialog.askopenfilename(title="Select File")
        if self.filter_fname and self.filter_fname.split('.')[-1] == 'csv':
            self.filter_file_text.config(
                text=self.filter_fname.split('/')[-1])
        else:
            messagebox.showerror(
                title="Error",
                message="Something went wrong, did you select an appropriately filter file?")
            return

        # set the default value of patient ID, date and include 
        OPTIONS = pd.read_csv(
                    self.filter_fname).columns.values.tolist()
        self.patient_id_entry.set(OPTIONS[0])
        self.date_entry.set(OPTIONS[1])
        self.include_entry.set('All')
        # patient ID column
        if 'empi' in OPTIONS:
            self.patient_id_entry.set('empi')
        elif 'EMPI' in OPTIONS:
            self.patient_id_entry.set('EMPI')
        # date column
        if 'procedure_date' in OPTIONS:
            self.date_entry.set('procedure_date')
        else:
            for o in OPTIONS:
                if 'date' in o.lower(): 
                    self.date_entry.set(o); break
        # load the columns to drop down menu
        try:
            self.patient_id_entry_menu = tk.OptionMenu(
                self.main_frame, self.patient_id_entry, *OPTIONS)
            self.patient_id_entry_menu.grid(column=2, columnspan=2, row=2, sticky='snwe')
            self.patient_id_entry_menu.config(
                font=font.Font(family='Roboto', size=12), bg=self.bg_color)
            self.date_entry_menu = tk.OptionMenu(
                self.main_frame, self.date_entry, *OPTIONS)
            self.date_entry_menu.grid(column=2, columnspan=2, row=3, sticky='snwe')
            self.date_entry_menu.config(
                font=font.Font(family='Roboto', size=12), bg=self.bg_color)
            OPTIONS.append('All')
            self.include_entry_menu = tk.OptionMenu(
                self.main_frame, self.include_entry, *OPTIONS)
            self.include_entry_menu.grid(column=2, columnspan=2, row=6, sticky='snwe')
            self.include_entry_menu.config(
                font=font.Font(family='Roboto', size=12), bg=self.bg_color)
            self.before_days = tk.Entry(self.main_frame)
            self.before_days.grid(column=2, columnspan=2, row=4, sticky='ew')
            self.after_days = tk.Entry(self.main_frame)
            self.after_days.grid(column=2, columnspan=2, row=5, sticky='ew')
        except BaseException:
            messagebox.showerror(
                title="Error",
                message="Something went wrong, did you select an appropriately file to perform the Regex on?")
            return
        self.run_filter_button.config(text='Filter RPDR File')

    def on_run_function(self):
        # filter RPDR file
        if self.filter_fname:
            try:
                days_before = int(self.before_days.get())
                days_after = int(self.after_days.get())
            except BaseException:
                messagebox.showerror(
                    title="Error",
                    message="Please enter the integer in before days and/or after days")
                return
            if not days_before or not days_after: 
                messagebox.showerror(
                    title="Error",
                    message="Please enter the before days and/or after days")
                return
            if not self.input_fname or not self.filter_fname:
                messagebox.showerror(
                    title="Error",
                    message="Please select the files using the 'Select File' button.")
                return
            patient_column = self.patient_id_entry.get()
            date_column = self.date_entry.get()
            include_column = self.include_entry.get()
            empi_to_date_range = get_empi_to_date_range(self.filter_fname, patient_column, date_column, include_column, days_before, days_after)
            if empi_to_date_range == 'error': 
                messagebox.showerror(
                        title="Error",
                        message="Something went wrong, did you select the correct columns?")
            else:
                msg = filter_rpdr_file(self.input_fname, empi_to_date_range, days_before, days_after)

        # convert RPDR to CSV
        else:
            msg = rpdr_to_csv(self.input_fname)

        if msg == 'error':
            messagebox.showerror(
                    title="Error",
                    message="Something went wrong, did you select an appropriately formatted RPDR file?")
        elif msg == 'done':
            messagebox.showinfo(
                    title="Done",
                    message="File saved!!")


    def setup_interface(self, root):
        # Define fonts
        textfont = font.Font(family='Roboto', size=16)
        labelfont = font.Font(family='Roboto', size=12)
        self.bg_color = "pale turquoise"

        # Creating main containers
        self.main_frame = tk.Frame(root, bg=self.bg_color)

        # Laying out all main containers
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.main_frame.grid(
            column=0,
            row=0,
            sticky='nsew')
        for i in range(10):
            self.main_frame.grid_rowconfigure(i, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=4)
        self.main_frame.grid_columnconfigure(3, weight=4)
        self.main_frame.grid_columnconfigure(4, weight=1)

        # Input RPDR/CSV file
        self.input_file_text = tk.Label(
            self.main_frame,
            text='RPDR File',
            font=labelfont,
            bg=self.bg_color)
        self.input_file_text.grid(column=1, row=0, sticky='nsw')

        self.input_file_text = tk.Label(
            self.main_frame,
            text='',
            font=labelfont,
            fg='dodgerblue4',
            bg=self.bg_color)
        self.input_file_text.grid(column=2, row=0, sticky='nsw')

        self.input_file_button = tk.Button(
            self.main_frame,
            text='Select',
            bg=self.bg_color,
            command=self.on_select_input_file)
        self.input_file_button.grid(column=3, row=0, sticky='e')

        # filter file
        self.filter_file_text = tk.Label(
            self.main_frame,
            text='Filter File',
            bg=self.bg_color,
            font=labelfont)
        self.filter_file_text.grid(column=1, row=1, sticky='nsw')

        self.filter_file_text = tk.Label(
            self.main_frame,
            text='',
            font=labelfont,
            bg=self.bg_color,
            fg='dodgerblue4')
        self.filter_file_text.grid(column=2, row=1, sticky='nsw')

        self.filter_file_button = tk.Button(
            self.main_frame,
            text='Select',
            bg=self.bg_color,
            state='disabled',
            command=self.on_select_filter_file)
        self.filter_file_button.grid(column=3, row=1, sticky='e')

        # Patient ID
        self.patient_id_label = tk.Label(
            self.main_frame,
            text='Patient ID column: ',
            bg=self.bg_color,
            font=labelfont)
        self.patient_id_label.grid(column=1, row=2, sticky='nsw')
        self.patient_id_entry = tk.StringVar(self.main_frame)

        # Procedure Date
        self.date_label = tk.Label(
            self.main_frame,
            text='Date column: ',
            bg=self.bg_color,
            font=labelfont)
        self.date_label.grid(column=1, row=3, sticky='nsw')
        self.date_entry = tk.StringVar(self.main_frame)

        # Before days
        self.before_label = tk.Label(
            self.main_frame,
            text='Before days: ',
            bg=self.bg_color,
            font=labelfont)
        self.before_label.grid(column=1, row=4, sticky='nsw')

        # After days
        self.after_label = tk.Label(
            self.main_frame,
            text='After days: ',
            bg=self.bg_color,
            font=labelfont)
        self.after_label.grid(column=1, row=5, sticky='nsw')

        # Include
        self.include_label = tk.Label(
            self.main_frame,
            text='Include: ',
            bg=self.bg_color,
            font=labelfont)
        self.include_label.grid(column=1, row=6, sticky='nsw')
        self.include_entry = tk.StringVar(self.main_frame)

        # Run filter
        self.run_filter_button = tk.Button(
            self.main_frame,
            text='Convert to CSV',
            font=textfont,
            state='disabled',
            bg=self.bg_color,
            command=self.on_run_function)
        self.run_filter_button.grid(column=1, row=8, columnspan=3, sticky='nswe')



