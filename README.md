RUSH - Local development

Quick start

1. Create a virtual environment (optional but recommended) and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Database creation

The application will now create the SQLite database automatically on first run if the DB file
is missing. The project now uses a project-local `rush.db` (created in the `RUSH/` folder next
to the code). You can still create it manually with the included script if you prefer:

```powershell
python create_rush_db.py
```

3. Run the app:

```powershell
python app.py
```

4. Open in browser: http://127.0.0.1:5000/

Default admin credentials

When the DB is created automatically the following default admin is inserted (you can change
it later with `create_admin.py` or `insert_admin.py`):

- username: admin
- password: adminpass

Additionally, an admin account `leroleroo` with password `TUNÇ3031` has been added per project
request.

Notes
- Templates and static assets live in `templates/` and `static/`.
- CSRF protection is enabled; use the forms in the UI or ensure your test client sends the CSRF token and preserves session cookies.
Bu proje küçük bir Flask uygulaması içerir (RUSH spor salonu).

Gereksinimler:
- Python 3.8+
- dependencies: requirements.txt

Çalıştırma:
1) Sanal ortam oluşturun ve etkinleştirin (Windows PowerShell):

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Veritabanı dosyası `c:\Users\TUNÇ\Desktop\rush-app\rush.db` konumunda olmalıdır (orijinal projede bu yol kullanılıyor). Eğer yoksa, basit bir SQLite şeması oluşturun:

```sql
CREATE TABLE admins (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT);
CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, status TEXT, payment_status TEXT, payment_date TEXT, created_at TEXT, approved_at TEXT);
```

3) Uygulamayı başlatın:

```powershell
python app.py
```

Notlar:
- `app.py` kısa bir admin giriş mekanizması sunar; production için secret key ve güvenlik iyileştirmeleri yapılmalıdır.


Push to GitHub (ETUUNC)

If you want to push this repository to your GitHub account `ETUUNC`, run the commands below from
the `RUSH` folder. Replace the remote URL if you named the repository differently on GitHub.

```powershell
cd 'C:\Users\TUNÇ\Desktop\RUSH'
git init
git add .
git commit -m "Initial import of RUSH"
git remote add origin https://github.com/ETUUNC/rush-app.git
git branch -M main
git push -u origin main
```

If you have the GitHub CLI (`gh`) configured with your account, you can create & push in one step:

```powershell
gh repo create ETUUNC/rush-app --public --source=. --remote=origin --push
```
