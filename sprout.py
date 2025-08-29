import customtkinter as ctk
import tkinter as tk  # at top of file
import webbrowser
import json
import os
import subprocess
import difflib
import re
import datetime

current_page = "main"

# App aliases for fuzzy matching and natural language launching
app_aliases = {
    "vs code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
    "discord": "Discord",
    "spotify": "Spotify",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "safari": "Safari",
    "terminal": "Terminal",
}

# Helper: Fuzzy match app names to aliases
def resolve_app_name(user_input):
    keys = app_aliases.keys()
    matches = difflib.get_close_matches(user_input.lower(), keys, n=1, cutoff=0.6)
    if matches:
        return app_aliases[matches[0]]
    return user_input  # fallback

# Helper: Parse Spotify playlist/album/track/song commands
def parse_spotify_command(command):
    # Match phrases like "<name> playlist", "<name> album", "<name> track", "<name> song"
    pattern = r"(.*)\s+(playlist|album|track|song)"
    m = re.search(pattern, command, re.IGNORECASE)
    if m:
        name = m.group(1).strip()
        # Build a spotify search URI, spaces replaced with %20
        spotify_uri = f"spotify:search:{name.replace(' ', '%20')}"
        return spotify_uri
    return None

# Workspace opener with smart launcher
def open_workspace(ws):
    for app_entry in ws.get("apps", []):
        app_name = app_entry.lower()

        # Handle Spotify special commands
        if "spotify" in app_name:
            spotify_uri = parse_spotify_command(app_entry)
            if spotify_uri:
                subprocess.run(["open", spotify_uri])
                continue

        # Resolve app alias with fuzzy matching
        resolved_app = resolve_app_name(app_entry)

        # If resolved app is a Spotify URI, open directly
        if isinstance(resolved_app, str) and resolved_app.startswith("spotify:"):
            subprocess.run(["open", resolved_app])
            continue

        # For known apps, open with "open -a"
        known_apps = app_aliases.values()
        if resolved_app in known_apps:
            subprocess.run(["open", "-a", resolved_app])
        else:
            # fallback: try to open as a file path or url (if it looks like one)
            if app_entry.startswith("http://") or app_entry.startswith("https://") or app_entry.startswith("spotify:"):
                webbrowser.open(app_entry)
            else:
                subprocess.run(["open", "-a", app_entry])
    for url in ws.get("urls", []):
        webbrowser.open(url)

CONFIG_FILE = os.path.expanduser("~/Sprout_config.json")
print(f"Saving/reading config from: {CONFIG_FILE}")

# Load config from file OR create new .json file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            if "workspaces" not in data:
                # Wrap old urls and apps into a default workspace
                default_ws = {
                    "name": "Default",
                    "urls": data.get("urls", []),
                    "apps": data.get("apps", [])
                }
                data = {"workspaces": [default_ws]}
            return data
    else:
        default_config = {"workspaces": []}
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config

# Save config to file
def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)



# CustomTkinter appearance and theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Main window setup
root = ctk.CTk()
root.title("Sprout")
root.geometry("400x540")
root.resizable(False, False)

container = ctk.CTkFrame(root, fg_color="#e6f0d4")
container.pack(fill="both", expand=True)

config = load_config()

# Render functions for pages

def render_main_page():
    global current_page
    current_page = "main"
    for widget in container.winfo_children():
        widget.destroy()

    title_label = ctk.CTkLabel(container, text="Sprout 🌱", 
                               font=ctk.CTkFont(family="Helvetica Neue", size=24, weight="bold"),
                               text_color="#1a3d1a")
    title_label.pack(pady=(20, 10))


    ws_frame = ctk.CTkScrollableFrame(container, width=360, height=250, fg_color="transparent")
    ws_frame.pack(pady=(10, 30))

    for ws in config["workspaces"]:
        index = config["workspaces"].index(ws)
        btn = ctk.CTkButton(ws_frame, text=f"{index + 1}. {ws.get('name', 'Workspace')}", width=320, height=40,
                            fg_color="#b4d6a9", hover_color="#a3c895",
                            text_color="#1a3d1a", font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
                            corner_radius=12,
                            command=lambda w=ws: open_workspace(w))
        btn.pack(pady=6)

    settings_btn = ctk.CTkButton(container, text="Settings ⚙️", width=120, height=40,
                                 fg_color="#b4d6a9", hover_color="#a3c895",
                                 text_color="#1a3d1a", font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
                                 corner_radius=12,
                                 command=render_settings_page)
    settings_btn.pack(pady=(10, 40))

    hotkey_label = ctk.CTkLabel(container, text="Press 1-9 to open workspaces", font=ctk.CTkFont(size=12, weight="normal"))
    hotkey_label.pack(pady=(0, 20))

    # --- Live date/time label at bottom right ---
    datetime_label = ctk.CTkLabel(container, font=ctk.CTkFont(size=11), text_color="#4b634b")
    datetime_label.pack(anchor="se", padx=10, pady=6)

    def update_datetime():
        now = datetime.datetime.now().strftime("%A, %B %d • %I:%M %p")
        datetime_label.configure(text=now)
        root.after(10000, update_datetime)  # update every 10 seconds

    update_datetime()


def render_settings_page():
    global current_page
    current_page = "settings"
    for widget in container.winfo_children():
        widget.destroy()

    label = ctk.CTkLabel(container, text="Workspaces", font=ctk.CTkFont(size=18, weight="bold"))
    label.pack(pady=(10, 5))

    listbox_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=10)
    listbox_frame.pack(pady=5)

    ws_box = tk.Listbox(
        listbox_frame,
        width=40,
        height=8,
        font=("Helvetica Neue", 12),
        activestyle='dotbox',
        bg="white",
        fg="#1a3d1a",
        highlightthickness=0,
        selectbackground="#a3c895",
        selectforeground="#1a3d1a",
        relief="flat",
        borderwidth=0
    )
    ws_box.pack(padx=10, pady=5)

    def edit_workspace_name(event):
        idx = get_selected_index()
        if idx is not None:
            old_name = config["workspaces"][idx]["name"]
            new_name = ctk.CTkInputDialog(text=f"Edit name for '{old_name}':", title="Edit Workspace Name").get_input()
            if new_name:
                config["workspaces"][idx]["name"] = new_name
                save_config()
                refresh_workspaces()

    ws_box.bind("<Double-Button-1>", edit_workspace_name)

    def refresh_workspaces():
        ws_box.delete(0, tk.END)
        for ws in config["workspaces"]:
            ws_box.insert(tk.END, ws["name"])

    refresh_workspaces()

    def get_selected_index():
        sel = ws_box.curselection()
        return sel[0] if sel else None

    def add_workspace():
        name = ctk.CTkInputDialog(text="Enter workspace name:", title="New Workspace").get_input()
        if name:
            config["workspaces"].append({"name": name, "urls": [], "apps": []})
            save_config()
            refresh_workspaces()

    def remove_workspace():
        idx = get_selected_index()
        if idx is not None:
            del config["workspaces"][idx]
            save_config()
            refresh_workspaces()

    def edit_workspace():
        idx = get_selected_index()
        if idx is None:
            return
        ws = config["workspaces"][idx]
        render_edit_workspace_page(ws)

    btn_frame = ctk.CTkFrame(container, fg_color="transparent")
    btn_frame.pack(pady=20)

    add_btn = ctk.CTkButton(
        btn_frame, text="Add Workspace", width=180, command=add_workspace,
        fg_color="#b4d6a9",
        hover_color="#a3c895",
        text_color="#1a3d1a",
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        corner_radius=12
    )
    add_btn.pack(pady=5)
    remove_btn = ctk.CTkButton(
        btn_frame, text="Remove Workspace", width=180, command=remove_workspace,
        fg_color="#b4d6a9",
        hover_color="#a3c895",
        text_color="#1a3d1a",
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        corner_radius=12
    )
    remove_btn.pack(pady=5)
    edit_btn = ctk.CTkButton(
        btn_frame, text="Edit Workspace", width=180, command=edit_workspace,
        fg_color="#b4d6a9",
        hover_color="#a3c895",
        text_color="#1a3d1a",
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        corner_radius=12
    )
    edit_btn.pack(pady=5)

    back_btn = ctk.CTkButton(
        container, text="Back", width=120, height=40, command=render_main_page,
        fg_color="#b4d6a9",
        hover_color="#a3c895",
        text_color="#1a3d1a",
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        corner_radius=12
    )
    back_btn.pack(pady=10)


def render_edit_workspace_page(ws):
    global current_page
    current_page = "edit"
    for widget in container.winfo_children():
        widget.destroy()

    label = ctk.CTkLabel(container, text=f"Edit {ws['name']}", font=ctk.CTkFont(size=18, weight="bold"))
    label.pack(pady=(10, 5))

    # URLs section
    url_label = ctk.CTkLabel(container, text="URLs", font=ctk.CTkFont(size=16, weight="bold"))
    url_label.pack(pady=(10, 5))

    url_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=10)
    url_frame.pack(pady=5)

    url_box = tk.Listbox(
        url_frame,
        width=40,
        height=6,
        font=("Helvetica Neue", 12),
        activestyle='dotbox',
        bg="white",
        fg="#1a3d1a",
        highlightthickness=0,
        selectbackground="#a3c895",
        selectforeground="#1a3d1a",
        relief="flat",
        borderwidth=0
    )
    url_box.pack(padx=10, pady=5)

    def refresh_urls():
        url_box.delete(0, tk.END)
        for u in ws.get("urls", []):
            url_box.insert(tk.END, u)

    refresh_urls()

    def get_selected_url_index():
        sel = url_box.curselection()
        return sel[0] if sel else None

    def add_url():
        new_url = ctk.CTkInputDialog(text="Enter URL:", title="Add URL").get_input()
        if new_url:
            ws["urls"].append(new_url)
            save_config()
            refresh_urls()

    def remove_url():
        idx = get_selected_url_index()
        if idx is not None:
            del ws["urls"][idx]
            save_config()
            refresh_urls()

    url_box.bind("<Delete>", lambda e: remove_url())

    # --- Double-click to edit URL ---
    def edit_url(event):
        idx = get_selected_url_index()
        if idx is not None:
            old_url = ws["urls"][idx]
            new_url = ctk.CTkInputDialog(text=f"Edit URL:", title="Edit URL").get_input()
            if new_url:
                ws["urls"][idx] = new_url
                save_config()
                refresh_urls()

    url_box.bind("<Double-Button-1>", edit_url)

    url_btn_frame = ctk.CTkFrame(container, fg_color="transparent")
    url_btn_frame.pack(pady=5)
    add_url_btn = ctk.CTkButton(
        url_btn_frame, text="Add URL", width=80, command=add_url,
        fg_color="#b4d6a9",
        hover_color="#a3c895",
        text_color="#1a3d1a",
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        corner_radius=12
    )
    add_url_btn.pack(side="left", padx=10)
    remove_url_btn = ctk.CTkButton(
        url_btn_frame, text="Remove URL", width=100, command=remove_url,
        fg_color="#b4d6a9",
        hover_color="#a3c895",
        text_color="#1a3d1a",
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        corner_radius=12
    )
    remove_url_btn.pack(side="left", padx=10)

    # Drag-and-drop support for URLs
    drag_data_url = {"dragging": False, "start_index": None}

    def on_url_button_press(event):
        drag_data_url["start_index"] = url_box.nearest(event.y)
        drag_data_url["dragging"] = True

    def on_url_button_release(event):
        if not drag_data_url["dragging"]:
            return
        drag_data_url["dragging"] = False
        end_index = url_box.nearest(event.y)
        start = drag_data_url["start_index"]
        if end_index != start and 0 <= start < len(ws["urls"]) and 0 <= end_index < len(ws["urls"]):
            ws["urls"].insert(end_index, ws["urls"].pop(start))
            save_config()
            refresh_urls()
            url_box.selection_clear(0, tk.END)
            url_box.selection_set(end_index)
            url_box.see(end_index)

    def on_url_motion(event):
        if drag_data_url["dragging"]:
            # Optionally, highlight the position or do visual feedback
            pass

    url_box.bind("<Button-1>", on_url_button_press)
    url_box.bind("<ButtonRelease-1>", on_url_button_release)
    url_box.bind("<B1-Motion>", on_url_motion)

    # Apps section
    app_label = ctk.CTkLabel(
        container,
        text="Apps",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    app_label.pack(pady=(15, 5))

    # Add a tooltip/help label for fuzzy/natural language support
    app_help_label = ctk.CTkLabel(
        container,
        text="Tip: You can enter fuzzy app names (e.g. 'vs code') or commands like \"Summer 25' playlist on spotify\".",
        font=ctk.CTkFont(size=11, weight="normal"),
        text_color="#4b634b",
        wraplength=340,
        anchor="w",
        justify="left"
    )
    app_help_label.pack(pady=(0, 2))

    app_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=10)
    app_frame.pack(pady=5)

    app_box = tk.Listbox(
        app_frame,
        width=40,
        height=6,
        font=("Helvetica Neue", 12),
        activestyle='dotbox',
        bg="white",
        fg="#1a3d1a",
        highlightthickness=0,
        selectbackground="#a3c895",
        selectforeground="#1a3d1a",
        relief="flat",
        borderwidth=0
    )
    app_box.pack(padx=10, pady=5)

    def refresh_apps():
        app_box.delete(0, tk.END)
        for a in ws.get("apps", []):
            app_box.insert(tk.END, a)

    refresh_apps()

    def get_selected_app_index():
        sel = app_box.curselection()
        return sel[0] if sel else None

    def add_app():
        new_app = ctk.CTkInputDialog(text="Enter app name:", title="Add App").get_input()
        if new_app:
            ws["apps"].append(new_app)
            save_config()
            refresh_apps()

    def remove_app():
        idx = get_selected_app_index()
        if idx is not None:
            del ws["apps"][idx]
            save_config()
            refresh_apps()

    app_box.bind("<Delete>", lambda e: remove_app())

    # --- Double-click to edit App/Command ---
    def edit_app(event):
        idx = get_selected_app_index()
        if idx is not None:
            old_app = ws["apps"][idx]
            new_app = ctk.CTkInputDialog(text=f"Edit app/command:", title="Edit App").get_input()
            if new_app:
                ws["apps"][idx] = new_app
                save_config()
                refresh_apps()

    app_box.bind("<Double-Button-1>", edit_app)

    app_btn_frame = ctk.CTkFrame(container, fg_color="transparent")
    app_btn_frame.pack(pady=5)
    add_app_btn = ctk.CTkButton(
        app_btn_frame, text="Add App", width=80, command=add_app,
        fg_color="#b4d6a9",
        hover_color="#a3c895",
        text_color="#1a3d1a",
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        corner_radius=12
    )
    add_app_btn.pack(side="left", padx=10)
    remove_app_btn = ctk.CTkButton(
        app_btn_frame, text="Remove App", width=100, command=remove_app,
        fg_color="#b4d6a9",
        hover_color="#a3c895",
        text_color="#1a3d1a",
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        corner_radius=12
    )
    remove_app_btn.pack(side="left", padx=10)

    # Drag-and-drop support for Apps
    drag_data_app = {"dragging": False, "start_index": None}

    def on_app_button_press(event):
        drag_data_app["start_index"] = app_box.nearest(event.y)
        drag_data_app["dragging"] = True

    def on_app_button_release(event):
        if not drag_data_app["dragging"]:
            return
        drag_data_app["dragging"] = False
        end_index = app_box.nearest(event.y)
        start = drag_data_app["start_index"]
        if end_index != start and 0 <= start < len(ws["apps"]) and 0 <= end_index < len(ws["apps"]):
            ws["apps"].insert(end_index, ws["apps"].pop(start))
            save_config()
            refresh_apps()
            app_box.selection_clear(0, tk.END)
            app_box.selection_set(end_index)
            app_box.see(end_index)

    def on_app_motion(event):
        if drag_data_app["dragging"]:
            # Optional visual feedback here
            pass

    app_box.bind("<Button-1>", on_app_button_press)
    app_box.bind("<ButtonRelease-1>", on_app_button_release)
    app_box.bind("<B1-Motion>", on_app_motion)

    back_btn = ctk.CTkButton(
        container, text="Back", width=120, height=40, command=render_settings_page,
        fg_color="#b4d6a9",
        hover_color="#a3c895",
        text_color="#1a3d1a",
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        corner_radius=12
    )
    back_btn.pack(pady=10)


# Key binding for number keys to open workspaces
def on_key_press(event):
    if current_page == "main" and event.char.isdigit():
        idx = int(event.char) - 1
        if 0 <= idx < len(config["workspaces"]):
            open_workspace(config["workspaces"][idx])

root.bind("<Key>", on_key_press)

render_main_page()

# Run GUI
root.mainloop()