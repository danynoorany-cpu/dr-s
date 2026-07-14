#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dr. S — Simaneyah Content System
Desktop application: sources library, website sync, message archive, suggestions.

Version 0.1 — UI skeleton + local sources library (JSON storage).
FTP sync and GitHub integration arrive in the next versions.

Requirements: Python 3.9+ (Tkinter is included with standard Windows Python).
Run: python dr_s.py
"""

import json
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog, scrolledtext

# ---------------------------------------------------------------------------
# Paths: the app lives in <repo>/app/, data lives in the repo folders.
# ---------------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(APP_DIR)
SOURCES_DIR = os.path.join(REPO_DIR, "sources")
WEBSITE_DIR = os.path.join(REPO_DIR, "website")
DB_FILE = os.path.join(SOURCES_DIR, "sources_db.json")

CHANNELS = ["facebook", "x", "whatsapp", "telegram", "tiktok", "website", "seminar", "note", "diary"]
STATUSES = ["raw", "refined", "published"]


# ---------------------------------------------------------------------------
# Data layer — deliberately simple: one JSON file, human-readable,
# lives inside the repo so every change is versioned by Git.
# ---------------------------------------------------------------------------
class SourcesDB:
    def __init__(self, path):
        self.path = path
        self.items = []
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                messagebox.showerror("Dr. S", f"Could not read sources DB:\n{e}")
                self.items = []
        else:
            self.items = []

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

    def add(self, title, channel, status, tags, body):
        item = {
            "id": max([i["id"] for i in self.items], default=0) + 1,
            "title": title,
            "channel": channel,
            "status": status,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "body": body,
            "created": datetime.now().isoformat(timespec="seconds"),
            "updated": datetime.now().isoformat(timespec="seconds"),
        }
        self.items.append(item)
        self.save()
        return item

    def update(self, item_id, **fields):
        for it in self.items:
            if it["id"] == item_id:
                it.update(fields)
                it["updated"] = datetime.now().isoformat(timespec="seconds")
                self.save()
                return it
        return None

    def delete(self, item_id):
        self.items = [i for i in self.items if i["id"] != item_id]
        self.save()


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
class DrSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dr. S — Simaneyah Content System  v0.1")
        self.geometry("1000x640")
        self.minsize(820, 520)

        self.db = SourcesDB(DB_FILE)

        # Status bar — created FIRST because tab builders write to it
        self.status = tk.StringVar(value=f"Sources DB: {DB_FILE}")
        tk.Label(self, textvariable=self.status, anchor="w",
                 bg="#efeaf7", fg="#2d1b4e").pack(fill="x", side="bottom")

        # Header
        header = tk.Frame(self, bg="#2d1b4e")
        header.pack(fill="x")
        tk.Label(header, text="Dr. S", font=("Segoe UI", 20, "bold"),
                 fg="#c9a7ff", bg="#2d1b4e").pack(side="left", padx=16, pady=8)
        tk.Label(header, text="Simaneyah Content System", font=("Segoe UI", 11),
                 fg="#e8ddff", bg="#2d1b4e").pack(side="left", pady=8)

        # Tabs
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=6, pady=6)

        self.tab_sources = ttk.Frame(self.nb)
        self.tab_website = ttk.Frame(self.nb)
        self.tab_messages = ttk.Frame(self.nb)
        self.tab_suggest = ttk.Frame(self.nb)
        self.nb.add(self.tab_sources, text="  Sources  ")
        self.nb.add(self.tab_website, text="  Website Sync  ")
        self.nb.add(self.tab_messages, text="  Messages Archive  ")
        self.nb.add(self.tab_suggest, text="  Suggestions  ")

        self._build_sources_tab()
        self._build_placeholder(self.tab_website,
            "Website Sync (coming in v0.2)",
            "This tab will compare the local website/ folder with the live site\n"
            "and upload changed files over FTP — replacing FileZilla.\n\n"
            f"Local website folder: {WEBSITE_DIR}")
        self._build_placeholder(self.tab_messages,
            "Messages Archive (coming in v0.3)",
            "Browse and search everything Dany posted on Facebook, X, WhatsApp,\n"
            "Telegram and TikTok — organized under sources/messages/.")
        self._build_placeholder(self.tab_suggest,
            "Suggestions (coming in v0.4)",
            "AI-assisted analysis of past sources to propose new messages\n"
            "and strategy, in Dany's voice.")



    # ----------------------------- Placeholder tabs -----------------------
    def _build_placeholder(self, parent, title, text):
        box = ttk.Frame(parent)
        box.pack(expand=True)
        ttk.Label(box, text=title, font=("Segoe UI", 15, "bold")).pack(pady=(40, 10))
        ttk.Label(box, text=text, justify="center",
                  font=("Segoe UI", 11)).pack(padx=20)

    # ----------------------------- Sources tab ----------------------------
    def _build_sources_tab(self):
        left = ttk.Frame(self.tab_sources)
        left.pack(side="left", fill="both", expand=True, padx=(4, 2), pady=4)
        right = ttk.Frame(self.tab_sources, width=380)
        right.pack(side="right", fill="y", padx=(2, 4), pady=4)
        right.pack_propagate(False)

        # Search
        srch = ttk.Frame(left)
        srch.pack(fill="x", pady=(0, 4))
        ttk.Label(srch, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_list())
        ttk.Entry(srch, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=4)

        # List
        cols = ("id", "title", "channel", "status", "updated")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        widths = {"id": 40, "title": 260, "channel": 90, "status": 80, "updated": 140}
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Editor
        ttk.Label(right, text="Title").pack(anchor="w")
        self.e_title = ttk.Entry(right)
        self.e_title.pack(fill="x")

        row = ttk.Frame(right); row.pack(fill="x", pady=4)
        ttk.Label(row, text="Channel").pack(side="left")
        self.e_channel = ttk.Combobox(row, values=CHANNELS, width=12, state="readonly")
        self.e_channel.set("note")
        self.e_channel.pack(side="left", padx=4)
        ttk.Label(row, text="Status").pack(side="left")
        self.e_status = ttk.Combobox(row, values=STATUSES, width=10, state="readonly")
        self.e_status.set("raw")
        self.e_status.pack(side="left", padx=4)

        ttk.Label(right, text="Tags (comma separated)").pack(anchor="w")
        self.e_tags = ttk.Entry(right)
        self.e_tags.pack(fill="x")

        ttk.Label(right, text="Body (Hebrew supported)").pack(anchor="w", pady=(4, 0))
        self.e_body = scrolledtext.ScrolledText(right, height=14, wrap="word", font=("Segoe UI", 11))
        self.e_body.pack(fill="both", expand=True)

        btns = ttk.Frame(right); btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="New / Clear", command=self.clear_editor).pack(side="left")
        ttk.Button(btns, text="Save", command=self.save_source).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete", command=self.delete_source).pack(side="left")
        ttk.Button(btns, text="Import file...", command=self.import_file).pack(side="right")

        self.current_id = None
        self.refresh_list()

    def refresh_list(self):
        q = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        for it in sorted(self.db.items, key=lambda x: x["updated"], reverse=True):
            hay = " ".join([it["title"], it["channel"], it["status"],
                            " ".join(it.get("tags", [])), it.get("body", "")]).lower()
            if q and q not in hay:
                continue
            self.tree.insert("", "end", iid=str(it["id"]),
                             values=(it["id"], it["title"], it["channel"],
                                     it["status"], it["updated"].replace("T", " ")))
        self.status.set(f"{len(self.db.items)} sources in library — {DB_FILE}")

    def on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = int(sel[0])
        it = next((i for i in self.db.items if i["id"] == item_id), None)
        if not it:
            return
        self.current_id = item_id
        self.e_title.delete(0, "end"); self.e_title.insert(0, it["title"])
        self.e_channel.set(it["channel"])
        self.e_status.set(it["status"])
        self.e_tags.delete(0, "end"); self.e_tags.insert(0, ", ".join(it.get("tags", [])))
        self.e_body.delete("1.0", "end"); self.e_body.insert("1.0", it.get("body", ""))

    def clear_editor(self):
        self.current_id = None
        self.e_title.delete(0, "end")
        self.e_channel.set("note")
        self.e_status.set("raw")
        self.e_tags.delete(0, "end")
        self.e_body.delete("1.0", "end")
        self.tree.selection_remove(self.tree.selection())

    def save_source(self):
        title = self.e_title.get().strip()
        if not title:
            messagebox.showwarning("Dr. S", "A source needs a title.")
            return
        body = self.e_body.get("1.0", "end").rstrip()
        if self.current_id is None:
            it = self.db.add(title, self.e_channel.get(), self.e_status.get(),
                             self.e_tags.get(), body)
            self.current_id = it["id"]
        else:
            self.db.update(self.current_id, title=title, channel=self.e_channel.get(),
                           status=self.e_status.get(),
                           tags=[t.strip() for t in self.e_tags.get().split(",") if t.strip()],
                           body=body)
        self.refresh_list()

    def delete_source(self):
        if self.current_id is None:
            return
        if messagebox.askyesno("Dr. S", "Delete this source? (It stays in Git history.)"):
            self.db.delete(self.current_id)
            self.clear_editor()
            self.refresh_list()

    def import_file(self):
        path = filedialog.askopenfilename(
            title="Import text file as source",
            filetypes=[("Text files", "*.txt *.md *.html"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except (UnicodeDecodeError, OSError) as e:
            messagebox.showerror("Dr. S", f"Could not read file:\n{e}")
            return
        self.clear_editor()
        self.e_title.insert(0, os.path.basename(path))
        self.e_body.insert("1.0", content)


if __name__ == "__main__":
    app = DrSApp()
    app.mainloop()
