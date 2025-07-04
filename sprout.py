import tkinter as tk
from tkinter import simpledialog
import webbrowser
import json
import os



# Save/load urls.json in user's home directory (to avoid PyInstaller sandboxing issues)
URLS_FILE = os.path.expanduser("~/Sprout_urls.json")


print(f"Saving/reading URLs from: {URLS_FILE}")

# Load URLs from file OR create new .json file
def load_urls():
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, "r") as f:
            return json.load(f)
    else:
        with open(URLS_FILE, "w") as f:
            json.dump([], f)
        return []

# Save URLs to file
def save_urls(urls):
    with open(URLS_FILE, "w") as f:
        json.dump(urls, f, indent=2)

# Open all URLs in default browser
def open_all():
    for url in url_list:
        webbrowser.open(url)

# Add a new URL
def add_url():
    new_url = simpledialog.askstring("Add URL", "Enter a new URL:")
    if new_url:
        url_list.append(new_url)
        save_urls(url_list)


# GUI setup
root = tk.Tk()
root.title("Sprout")
root.geometry("400x300")
root.configure(bg="#1e1e1e")

url_list = load_urls()

# Open all URLs on launch
open_all()

# Settings window
def open_settings():
    settings = tk.Toplevel(root)
    settings.title("Edit URLs")
    settings.geometry("400x300")
    settings.configure()

    listbox = tk.Listbox(settings, selectmode=tk.SINGLE, width=50, height=10)
    listbox.pack(pady=10)

    for url in url_list:
        listbox.insert(tk.END, url)

    def refresh():
        listbox.delete(0, tk.END)
        for url in url_list:
            listbox.insert(tk.END, url)

    def add():
        new_url = simpledialog.askstring("Add URL", "Enter a new URL:")
        if new_url:
            url_list.append(new_url)
            save_urls(url_list)
            refresh()

    def remove():
        selected = listbox.curselection()
        if selected:
            del url_list[selected[0]]
            save_urls(url_list)
            refresh()

    tk.Button(settings, text="Add 🍃", command=add, width=10).pack(pady=5)
    tk.Button(settings, text="Remove 🍂", command=remove, width=10).pack()

# Minimal Settings window
tk.Button(
    root, text="Settings ⚙️", command=open_settings,
    width=20
).pack(pady=100)

# Run GUI
root.mainloop()