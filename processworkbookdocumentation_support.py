#! /usr/bin/env python
#
# Support module generated by PAGE version 4.8.9
# In conjunction with Tcl version 8.6
#    Apr 10, 2017 01:27:02 PM
#    Apr 14, 2017 04:19:25 PM

import os
from tkinter import filedialog
from tkinter import messagebox
import logging
import glob
import support_functions
from WorkbookDocumentation import workbook_documentation
import threading

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1


def set_Tk_var():
    # These are Tk variables used passed to Tkinter and must be
    # defined before the widgets using them are created.
    global inEntryTxt
    inEntryTxt = StringVar()

    global outEntryTxt
    outEntryTxt = StringVar()

    global file_or_dir
    file_or_dir = StringVar()
    file_or_dir.set("File")

    global auto_start
    auto_start = BooleanVar()

    global suppress_error_dialogs
    suppress_error_dialogs = BooleanVar()


def exit_window():
    destroy_window()


def inBrowse():
    global inEntryTxt
    global file_or_dir
    global top_level

    oldFoc = top_level.focus_get()

    opts = {}
    if os.name != 'posix':
        opts['filetypes'] = [('Tableau workbooks and data sources', '*.twb;*.twbx;*.tds;*.tdsx'),
                             ('all files', '.*')]
    if file_or_dir.get() == "File":
        inEntryTxt.set(filedialog.askopenfilename(**opts))
    elif file_or_dir.get() == "Directory":
        inEntryTxt.set(filedialog.askdirectory())
    else:
        messagebox.showinfo("Error", "Please select an option of File or Directory")

    if oldFoc:
        oldFoc.focus_set()


def outBrowse():
    global outEntryTxt
    global top_level

    oldFoc = top_level.focus_get()
    outEntryTxt.set(filedialog.askdirectory())
    if oldFoc:
        oldFoc.focus_set()


def open_config(inconfig=None):
    global top_level
    global process_cfg

    old_foc = top_level.focus_get()
    support_functions.open_config("process_cfg", process_cfg, inconfig)
    if old_foc:
        old_foc.focus_set()


def save_config():
    global top_level
    global process_cfg

    old_foc = top_level.focus_get()
    support_functions.save_config("process_cfg", process_cfg)
    if old_foc:
        old_foc.focus_set()


def process_files():
    global inEntryTxt
    global outEntryTxt
    global file_or_dir
    global top_level
    global w
    global suppress_error_dialogs

    oldFoc = top_level.focus_get()

    input_file_dir = support_functions.validate_infile(inEntryTxt.get(),
                                                       file_or_dir)
    output_dir = support_functions.validate_file_or_dir(outEntryTxt.get(),
                                                        "Output directory",
                                                        "directory")
    step = 0
    error_count = 0
    error_files = ""
    if input_file_dir and output_dir:
        if file_or_dir.get() == "Directory":
            os.chdir(input_file_dir)
            logging.info("input_file_dir = " + input_file_dir)
            w.add_progbar(0, len(glob.glob("*.t[dw][bs]*")), 4)

            for infileName in glob.glob("*.t[dw][bs]*"):
                try:
                    logging.info("infile name = {}".format(infileName))
                    workbook_documentation(infileName, output_dir)
                except:
                    logging.error("error processing {}".format(infileName))
                    error_files = error_files + chr(13) + chr(10) + infileName
                    if suppress_error_dialogs.get() is not True:
                        if error_count < 3:
                            messagebox.showerror("File error",
                                                 "Error encountered while processing {}".format(infileName))
                            error_count += 1
                        else:
                            if messagebox.askokcancel('File errors',
                                                      "Multiple errors encountered. Latest: {}. ".format(infileName) +
                                                      "OK to continue, Cancel to quit"):
                                error_count = 0
                            else:
                                exit(1)
                step += 1
                w.update_progbar(step, "Now processing: {}".format(infileName))
            w.update_progbar(step, "Finished processing")
        elif file_or_dir.get() == "File":
            logging.info("infile name = " + input_file_dir)
            workbook_documentation(input_file_dir, output_dir)

        print(error_files)
        logging.info('Finished Workbook Documentation creation using processworkbookdocumentation.py')
        if len(error_files) > 0:
            error_files = "{}{}Found errors with the following files: {}".format(chr(13) + chr(10), chr(13) + chr(10),
                                                                                 error_files)
        messagebox.showinfo("Finished", "Finished Workbook Documentation{}".format(error_files))
    else:
        logging.info('Error with input or output file')
        messagebox.showerror("Unable to start", "Error with input content or output destination")
    if oldFoc:
        oldFoc.focus_set()


def init(top, gui, *args, **kwargs):
    global w, top_level, root, process_cfg
    global inEntryTxt
    global file_or_dir
    global outEntryTxt

    w = gui
    top_level = top
    root = top
    process_cfg = []
    process_cfg.append(support_functions.config_entry("input_file_dir", inEntryTxt))
    process_cfg.append(support_functions.config_entry("save_dir", outEntryTxt))
    process_cfg.append(support_functions.config_entry("file_or_dir", file_or_dir))

    logging.basicConfig(filename='process_workbook_documentation.log',
                        level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('Started')


def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None


if __name__ == '__main__':
    import processworkbookdocumentation
    processworkbookdocumentation.vp_start_gui()
