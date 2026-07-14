# Dr. S — Simaneyah Content System

Desktop application + content repository for [simaneyah.co.il](https://simaneyah.co.il).

## Repository structure

```
dr-s/
├── app/                  # The Dr. S desktop application (Python/Tkinter)
│   └── dr_s.py
├── website/              # Static HTML files of simaneyah.co.il (deployed via FTP)
├── sources/
│   ├── sources_db.json   # The sources library (managed by the app)
│   ├── messages/         # Archive of posted content, by channel
│   │   ├── facebook/  x/  whatsapp/  telegram/  tiktok/
│   └── suggestions/      # Draft messages & strategy proposals
└── README.md
```

## Running the app (Windows)

1. Install Python 3.9+ from [python.org](https://www.python.org/downloads/) — tick **"Add Python to PATH"** during install.
2. Double-click `app/dr_s.py`, or from a terminal:

```
python app/dr_s.py
```

No extra packages needed for v0.1.

## Roadmap

| Version | Feature |
|---------|---------|
| v0.1 ✅ | Sources library UI (create / edit / tag / search / import) |
| v0.2    | Website Sync — FTP upload of changed files in `website/` |
| v0.3    | Messages archive browser |
| v0.4    | AI-assisted suggestions engine |

## Rules of the house

- **No credentials in this repo, ever.** FTP passwords go in a local `config.ini` that is listed in `.gitignore`.
- **No private/personal material in this repo while it is public** (diary entries, unpublished strategy). Those get a separate private repo.
- Every change to sources or website files is committed to Git — that's our backup and history.
