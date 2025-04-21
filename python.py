# Pramod 30 Minutes Code Challenges - Enhanced Version
import re
from tkinter import *
from tkinter.ttk import *
from datetime import datetime, timedelta
from tkinter import messagebox
from tkinter import filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText
import time
import webbrowser
import os
import sys
import platform
from threading import Thread
import json

# The root widget
root = Tk()
root.title('Pramod 30 Minutes Code Challenges')
root.resizable(0, 0)

# Configuration variables
CONFIG_FILE = "pramod_challenge_config.json"
DEFAULT_CHALLENGE_TIME = 30  # minutes

# Timer variables
time_left = timedelta(minutes=DEFAULT_CHALLENGE_TIME)
timer_running = False
last_activity_time = datetime.now()
inactivity_threshold = 5  # seconds
challenge_start_time = None
total_keystrokes = 0
word_count = 0

# Challenge statistics
challenge_stats = {
    'challenges_completed': 0,
    'total_time_spent': 0,
    'average_keystrokes': 0,
    'average_words': 0
}

# Load configuration
def load_config():
    global challenge_stats, DEFAULT_CHALLENGE_TIME
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            challenge_stats = config.get('stats', challenge_stats)
            DEFAULT_CHALLENGE_TIME = config.get('default_time', DEFAULT_CHALLENGE_TIME)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

# Save configuration
def save_config():
    config = {
        'stats': challenge_stats,
        'default_time': DEFAULT_CHALLENGE_TIME
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

load_config()

# Creating scrollable notepad window with syntax highlighting
notepad = ScrolledText(root, width=90, height=40, wrap=WORD, font=('Consolas', 11))
fileName = ''

# Timer label at the top
timer_label = Label(root, text=f"{DEFAULT_CHALLENGE_TIME}:00", font=('Arial', 14, 'bold'))
timer_label.pack()

# Stats label
stats_label = Label(root, text="Keystrokes: 0 | Words: 0", font=('Arial', 10))
stats_label.pack()

# Challenge theme selector
theme_var = StringVar(value='light')
themes = {
    'light': {'bg': 'white', 'fg': 'black'},
    'dark': {'bg': '#2d2d2d', 'fg': 'white'},
    'solarized': {'bg': '#fdf6e3', 'fg': '#657b83'}
}

def change_theme():
    theme = theme_var.get()
    notepad.config(
        background=themes[theme]['bg'],
        foreground=themes[theme]['fg'],
        insertbackground=themes[theme]['fg']
    )

# Disable copy-paste functionality
def disable_copy_paste(event):
    return "break"

notepad.bind("<Control-c>", disable_copy_paste)
notepad.bind("<Control-v>", disable_copy_paste)
notepad.bind("<Control-x>", disable_copy_paste)

# Track user activity and statistics
def record_activity(event=None):
    global last_activity_time, timer_running, total_keystrokes, word_count
    
    # Update statistics
    if event and event.keysym not in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R']:
        total_keystrokes += 1
        stats_label.config(text=f"Keystrokes: {total_keystrokes} | Words: {word_count}")
    
    # Update word count
    current_text = notepad.get("1.0", "end-1c")
    word_count = len(current_text.split())
    stats_label.config(text=f"Keystrokes: {total_keystrokes} | Words: {word_count}")
    
    last_activity_time = datetime.now()
    # Resume if paused and time is left
    if not timer_running and time_left.total_seconds() > 0:
        timer_running = True
        update_timer()

# Bind key press and mouse events to record activity
notepad.bind("<Key>", record_activity)
notepad.bind("<Button>", record_activity)

# Update timer function
def update_timer():
    global time_left, timer_running, challenge_stats

    if timer_running:
        # Check for inactivity
        inactive_for = (datetime.now() - last_activity_time).total_seconds()
        if inactive_for >= inactivity_threshold:
            timer_running = False
            timer_label.config(text="PAUSED", foreground='orange')
            return

        time_left -= timedelta(seconds=1)
        if time_left.total_seconds() <= 0:
            timer_running = False
            time_left = timedelta(seconds=0)
            timer_label.config(text="TIME'S UP!", foreground='red')
            
            # Update challenge statistics
            challenge_stats['challenges_completed'] += 1
            challenge_stats['total_time_spent'] += DEFAULT_CHALLENGE_TIME
            challenge_stats['average_keystrokes'] = (
                (challenge_stats['average_keystrokes'] * (challenge_stats['challenges_completed'] - 1) + total_keystrokes
            ) / challenge_stats['challenges_completed']
            challenge_stats['average_words'] = (
                (challenge_stats['average_words'] * (challenge_stats['challenges_completed'] - 1) + word_count
            ) / challenge_stats['challenges_completed']
            
            save_config()
            show_challenge_complete()
            cmdSave()
            return

        # Format the time as MM:SS
        minutes, seconds = divmod(int(time_left.total_seconds()), 60)
        timer_text = f"{minutes:02d}:{seconds:02d}"

        # Change color when under 5 minutes
        if minutes < 5:
            timer_label.config(foreground='red')
        else:
            timer_label.config(foreground='black')

        timer_label.config(text=timer_text)
        root.after(1000, update_timer)

def show_challenge_complete():
    completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats_text = (
        f"Challenge Completed!\n\n"
        f"Time: {completion_time}\n"
        f"Keystrokes: {total_keystrokes}\n"
        f"Words: {word_count}\n\n"
        f"Total Challenges Completed: {challenge_stats['challenges_completed']}\n"
        f"Average Keystrokes: {challenge_stats['average_keystrokes']:.1f}\n"
        f"Average Words: {challenge_stats['average_words']:.1f}"
    )
    messagebox.showinfo("Challenge Complete", stats_text)

def start_timer(minutes=None):
    global timer_running, time_left, last_activity_time, challenge_start_time, total_keystrokes, word_count
    
    # Reset statistics
    total_keystrokes = 0
    word_count = 0
    stats_label.config(text=f"Keystrokes: 0 | Words: 0")
    
    # Ask for save location before starting if not already saved
    if not fileName and not cmdSave():
        return  # User canceled save
    
    if minutes is None:
        minutes = DEFAULT_CHALLENGE_TIME
    
    timer_running = True
    last_activity_time = datetime.now()
    challenge_start_time = datetime.now()
    time_left = timedelta(minutes=minutes)
    update_timer()

def stop_timer():
    global timer_running
    timer_running = False
    timer_label.config(text="STOPPED", foreground='gray')

def restart_timer():
    global time_left
    if messagebox.askyesno("Restart Timer", "Are you sure you want to restart the timer?"):
        start_timer()

# Challenge templates
CHALLENGE_TEMPLATES = {
    "Algorithm Practice": "def solution(input):\n    # Your code here\n    return result\n\n# Test cases\nprint(solution(test_input))",
    "Data Structure": "class DataStructure:\n    def __init__(self):\n        pass\n\n    def method1(self):\n        pass\n\n    def method2(self):\n        pass",
    "Web Scraper": "import requests\nfrom bs4 import BeautifulSoup\n\nurl = 'https://example.com'\nresponse = requests.get(url)\nsoup = BeautifulSoup(response.text, 'html.parser')\n\n# Extract data here",
    "Data Analysis": "import pandas as pd\nimport numpy as np\n\n# Load data\ndata = pd.read_csv('data.csv')\n\n# Analyze data\n# Your code here"
}

def load_template(template_name):
    if messagebox.askyesno("Load Template", f"Load '{template_name}' template? This will overwrite current content."):
        notepad.delete("1.0", END)
        notepad.insert("1.0", CHALLENGE_TEMPLATES[template_name])

# Defining functions for commands
def cmdNew():     # file menu New option
    global fileName, total_keystrokes, word_count
    if len(notepad.get('1.0', END+'-1c')) > 0:
        if messagebox.askyesno("Notepad", "Do you want to save changes?"):
            cmdSave()
        notepad.delete(0.0, END)
    total_keystrokes = 0
    word_count = 0
    stats_label.config(text=f"Keystrokes: 0 | Words: 0")
    root.title("Pramod 30 Minutes Code Challenges")

def cmdOpen():     # file menu Open option
    global fileName, total_keystrokes, word_count
    fd = filedialog.askopenfile(parent=root, mode='r')
    if fd:
        t = fd.read()
        notepad.delete(0.0, END)
        notepad.insert(0.0, t)
        fileName = fd.name
        fd.close()
        total_keystrokes = 0
        word_count = len(t.split())
        stats_label.config(text=f"Keystrokes: 0 | Words: {word_count}")

def cmdSave():     # file menu Save option
    global fileName
    if fileName:
        try:
            with open(fileName, 'w') as fd:
                data = notepad.get('1.0', END)
                fd.write(data)
            return True
        except:
            messagebox.showerror(title="Error", message="Not able to save file!")
            return False
    else:
        return cmdSaveAs()

def cmdSaveAs():     # file menu Save As option
    global fileName
    fd = filedialog.asksaveasfile(mode='w', defaultextension='.txt',
                                 filetypes=[("Text files", "*.txt"),
                                            ("Python files", "*.py"),
                                            ("All files", "*.*")])
    if fd is not None:
        t = notepad.get(0.0, END)
        try:
            fd.write(t.rstrip())
            fileName = fd.name
            fd.close()
            return True
        except:
            messagebox.showerror(title="Error", message="Not able to save file!")
            return False
    return False

def cmdExit():     # file menu Exit option
    if messagebox.askyesno("Notepad", "Are you sure you want to exit?"):
        cmdSave()
        save_config()
        root.destroy()

def cmdCut():
    pass

def cmdCopy():
    pass

def cmdPaste():
    pass

def cmdClear():
    notepad.event_generate("<<Clear>>")

def cmdFind():
    notepad.tag_remove("Found", '1.0', END)
    find = simpledialog.askstring("Find", "Find what:")
    if find:
        idx = '1.0'
        while 1:
            idx = notepad.search(find, idx, nocase=1, stopindex=END)
            if not idx:
                break
            lastidx = '%s+%dc' % (idx, len(find))
            notepad.tag_add('Found', idx, lastidx)
            idx = lastidx
    notepad.tag_config('Found', foreground='white', background='blue')
    notepad.bind("<1>", click)

def click(event):
    notepad.tag_config('Found', background='white', foreground='black')

def cmdSelectAll():
    notepad.event_generate("<<SelectAll>>")

def cmdTimeDate():
    now = datetime.now()
    dtString = now.strftime("%d/%m/%Y %H:%M:%S")
    label = messagebox.showinfo("Time/Date", dtString)

def cmdAbout():
    about_text = (
        "Pramod 30 Minutes Code Challenges\n\n"
        "Version: 2.0\n"
        "Features:\n"
        "- 30-minute coding challenges with timer\n"
        "- Activity tracking and auto-pause\n"
        "- Challenge statistics and history\n"
        "- Multiple themes\n"
        "- Challenge templates\n"
        "- Keystroke and word count tracking"
    )
    label = messagebox.showinfo("About Notepad", about_text)

def show_stats():
    stats_text = (
        "Your Challenge Statistics:\n\n"
        f"Challenges Completed: {challenge_stats['challenges_completed']}\n"
        f"Total Time Spent: {challenge_stats['total_time_spent']} minutes\n"
        f"Average Keystrokes: {challenge_stats['average_keystrokes']:.1f}\n"
        f"Average Words: {challenge_stats['average_words']:.1f}"
    )
    messagebox.showinfo("Your Statistics", stats_text)

def open_documentation():
    docs_url = "https://github.com/yourusername/pramod-challenges/wiki"
    webbrowser.open_new_tab(docs_url)

def set_custom_time():
    minutes = simpledialog.askinteger("Set Timer", "Enter minutes for challenge:", 
                                     parent=root, minvalue=1, maxvalue=120)
    if minutes:
        global DEFAULT_CHALLENGE_TIME
        DEFAULT_CHALLENGE_TIME = minutes
        save_config()
        start_timer(minutes)

# Notepad menu items
notepadMenu = Menu(root)
root.configure(menu=notepadMenu)

# File menu
fileMenu = Menu(notepadMenu, tearoff=False)
notepadMenu.add_cascade(label='File', menu=fileMenu)

fileMenu.add_command(label='New', command=cmdNew, accelerator="Ctrl+N")
fileMenu.add_command(label='Open...', command=cmdOpen, accelerator="Ctrl+O")
fileMenu.add_command(label='Save', command=cmdSave, accelerator="Ctrl+S")
fileMenu.add_command(label='Save As...', command=cmdSaveAs, accelerator="Ctrl+Shift+S")
fileMenu.add_separator()
fileMenu.add_command(label='Start Timer (30 min)', command=lambda: start_timer(30))
fileMenu.add_command(label='Set Custom Time...', command=set_custom_time)
fileMenu.add_command(label='Stop Timer', command=stop_timer, accelerator="Esc")
fileMenu.add_command(label='Restart Timer', command=restart_timer)
fileMenu.add_separator()
fileMenu.add_command(label='Exit', command=cmdExit, accelerator="Alt+F4")

# Edit menu
editMenu = Menu(notepadMenu, tearoff=False)
notepadMenu.add_cascade(label='Edit', menu=editMenu)

editMenu.add_command(label='Cut (Disabled)', command=cmdCut)
editMenu.add_command(label='Copy (Disabled)', command=cmdCopy)
editMenu.add_command(label='Paste (Disabled)', command=cmdPaste)
editMenu.add_command(label='Delete', command=cmdClear)
editMenu.add_separator()
editMenu.add_command(label='Find...', command=cmdFind, accelerator="Ctrl+F")
editMenu.add_separator()
editMenu.add_command(label='Select All', command=cmdSelectAll, accelerator="Ctrl+A")
editMenu.add_command(label='Time/Date', command=cmdTimeDate)

# Challenge menu
challengeMenu = Menu(notepadMenu, tearoff=False)
notepadMenu.add_cascade(label='Challenge', menu=challengeMenu)

# Add templates submenu
templatesMenu = Menu(challengeMenu, tearoff=False)
challengeMenu.add_cascade(label='Load Template', menu=templatesMenu)
for template in CHALLENGE_TEMPLATES:
    templatesMenu.add_command(label=template, command=lambda t=template: load_template(t))

# Add themes submenu
themesMenu = Menu(challengeMenu, tearoff=False)
challengeMenu.add_cascade(label='Change Theme', menu=themesMenu)
for theme in themes:
    themesMenu.add_radiobutton(label=theme.capitalize(), variable=theme_var, 
                              value=theme, command=change_theme)

challengeMenu.add_separator()
challengeMenu.add_command(label='View Statistics', command=show_stats)

# Help menu
helpMenu = Menu(notepadMenu, tearoff=False)
notepadMenu.add_cascade(label='Help', menu=helpMenu)

helpMenu.add_command(label='Documentation', command=open_documentation)
helpMenu.add_command(label='About Notepad', command=cmdAbout)

notepad.pack()

# Keyboard shortcuts
root.bind('<Escape>', lambda e: stop_timer())
root.bind('<Control-n>', lambda e: cmdNew())
root.bind('<Control-o>', lambda e: cmdOpen())
root.bind('<Control-s>', lambda e: cmdSave())
root.bind('<Control-Shift-S>', lambda e: cmdSaveAs())
root.bind('<Control-f>', lambda e: cmdFind())
root.bind('<Control-a>', lambda e: cmdSelectAll())

# Start with light theme
change_theme()

# Start by asking for save location
if messagebox.askyesno("Pramod 30 Minutes Code Challenges",
                       "Welcome! You have 30 minutes to complete your challenge.\n"
                       "Would you like to select a save location now?"):
    if cmdSaveAs():
        start_timer()

root.mainloop()