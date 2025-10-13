from flask import Flask, g, render_template, render_template_string, request, redirect, url_for, flash, session
import os
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, generate_csrf
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Optional
import sqlite3
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta


# Use a project-relative SQLite DB so the repo is portable.
# Default file will be RUSH/rush.db next to this file.
DB = os.path.join(os.path.dirname(__file__), 'rush.db')

# Use an environment variable for secret key in deployments; fallback to a dev key.
def _get_secret_key():
    return os.environ.get('RUSH_SECRET_KEY', 'dev-fallback-key')


def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


class LoginForm(FlaskForm):
    username = StringField('Kullanıcı', validators=[DataRequired()])
    password = PasswordField('Parola', validators=[DataRequired()])
    submit = SubmitField('Giriş')


class RegisterForm(FlaskForm):
    name = StringField('Ad Soyad', validators=[DataRequired()])
    email = StringField('E-Posta', validators=[DataRequired(), Email()])
    phone = StringField('Telefon', validators=[DataRequired()])
    submit = SubmitField('Kaydet')


class EditForm(FlaskForm):
    # For admin editing we allow leaving name/email empty (they will fall back to DB values)
    name = StringField('Ad Soyad')
    email = StringField('E-Posta', validators=[Optional(), Email()])
    phone = StringField('Telefon')
    payment_status = SelectField('Ödeme Durumu', choices=[('', ''), ('Bekliyor', 'Bekliyor'), ('Ödendi', 'Ödendi'), ('İptal', 'İptal')])
    payment_date = StringField('Ödeme Tarihi')
    submit = SubmitField('Kaydet')


app = Flask(__name__)
app.secret_key = _get_secret_key()
# Initialize CSRF protection so manual csrf_token() calls in templates work
csrf = CSRFProtect()
csrf.init_app(app)
app.teardown_appcontext(close_db)


@app.template_filter('format_datetime')
def format_datetime(value):
    if not value:
        return ''
    try:
        # stored as ISO string
        dt = datetime.fromisoformat(value)
        return dt.strftime('%Y-%m-%d %H:%M')
    except Exception:
        return str(value)


def admin_housekeeping():
    """Update members older than 30 days and return count of approved members whose payment_status != 'Ödendi'."""
    db = get_db()
    try:
        cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()
        # set payment_status to Bekliyor for old records that are not Ödendi
        db.execute("UPDATE members SET payment_status = 'Bekliyor' WHERE created_at < ? AND (payment_status IS NULL OR payment_status NOT LIKE '%Öden%')", (cutoff,))
        db.commit()
    except Exception:
        pass

    try:
        cur = db.execute("SELECT COUNT(*) as cnt FROM members WHERE status='approved' AND (payment_status IS NULL OR payment_status NOT LIKE '%Öden%')")
        row = cur.fetchone()
        return row['cnt'] if row else 0
    except Exception:
        return 0


@app.route('/')
def index():
    # Try normal render first. If the Jinja loader returns an empty template
    # (some filesystems/encodings can cause loader issues), fall back to
    # reading the template file directly and rendering from that string.
    try:
        # clear Jinja loader cache to avoid stale/empty template source issues
        try:
            app.jinja_env.cache.clear()
        except Exception:
            pass
        out = render_template('index.html', admin_logged_in=session.get('admin_logged_in'))
        if out and len(out) > 0:
            return out
    except Exception:
        # swallow and try fallback
        pass

    # Fallback: read the template file directly and render it as a template string.
    tpl_path = None
    try:
        tpl_path = os.path.join(app.root_path, app.template_folder, 'index.html')
        with open(tpl_path, 'r', encoding='utf-8') as f:
            src = f.read()
        # only render if file had content
        if src and len(src) > 0:
            return render_template_string(src, admin_logged_in=session.get('admin_logged_in'))
    except Exception as e:
        # If reading the file fails, we'll fall through to the final fallback below
        pass

    # Final fallback: return a minimal static HTML so the site is visible.
    FALLBACK_INDEX_HTML = '''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RUSH</title><link rel="stylesheet" href="/static/style.css"></head><body><div class="container"><h1>RUSH</h1><p>Uygulama çalışıyor — şablon yüklenemedi, bu bir yedek gösterimdir.</p><p><a href="/register">Kayıt</a> · <a href="/login">Admin Girişi</a></p></div></body></html>'''
    return FALLBACK_INDEX_HTML, 200


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db = get_db()
        try:
            db.execute(
                'INSERT INTO members (name, email, phone, status, created_at) VALUES (?,?,?,?,?)',
                (form.name.data, form.email.data, form.phone.data, 'pending', datetime.utcnow().isoformat()),
            )
            db.commit()
            flash('Kayıt başarıyla oluşturuldu. Admin onayı bekleniyor.')
            return redirect(url_for('index'))
        except Exception as e:
            flash('Kayıt eklenirken hata oluştu: ' + str(e))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Restrict admin login to the single allowed username for now
        if form.username.data != 'leroleroo':
            flash('Kullanıcı adı veya parola hatalı')
            return render_template('login.html', form=form)

        db = get_db()
        cur = db.execute('SELECT id, username, password_hash FROM admins WHERE username = ?', (form.username.data,))
        row = cur.fetchone()
        if row and check_password_hash(row['password_hash'], form.password.data):
            session['admin_logged_in'] = True
            session['admin_user'] = row['username']
            # run housekeeping tasks and flash notifications
            try:
                cnt = admin_housekeeping()
                if cnt:
                    flash(f"Dikkat: {cnt} kayıtlı üyenin ödeme durumu 'Ödendi' değil.")
            except Exception:
                # don't block login on housekeeping errors
                pass
            flash('Giriş başarılı')
            return redirect(url_for('admin'))
        flash('Kullanıcı adı veya parola hatalı')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    flash('Çıkış yapıldı')
    return redirect(url_for('index'))


def require_admin():
    if not session.get('admin_logged_in'):
        flash('Admin girişi gerekli')
        return False
    # enforce specific allowed admin username
    if session.get('admin_user') != 'leroleroo':
        flash('Admin girişi gerekli')
        return False
    return True


@app.route('/admin', methods=['GET'])
def admin():
    if not require_admin():
        return redirect(url_for('login'))
    db = get_db()
    # try to query expected columns; if schema differs, return empty lists gracefully
    try:
        pending = db.execute("SELECT * FROM members WHERE status = 'pending' ORDER BY id DESC").fetchall()
    except Exception:
        pending = []
    try:
        approved = db.execute("SELECT * FROM members WHERE status = 'approved' ORDER BY approved_at DESC").fetchall()
    except Exception:
        approved = []
    try:
        rejected = db.execute("SELECT * FROM members WHERE status = 'rejected' ORDER BY id DESC").fetchall()
    except Exception:
        rejected = []
    # translate payment_status values to Turkish for display
    def _translate_status(val):
        if not val:
            return 'Bekliyor'
        low = str(val).lower()
        if 'ödendi' in low or 'paid' in low:
            return 'Ödendi'
        if 'iptal' in low or 'cancel' in low:
            return 'İptal'
        if 'ödenmedi' in low or 'unpaid' in low:
            return 'Ödenmedi'
        if 'bekliyor' in low or 'pending' in low:
            return 'Bekliyor'
        # default
        return val

    def _rows_to_list(rows):
        out = []
        for r in rows:
            try:
                d = dict(r)
            except Exception:
                # if it's already a dict-like
                d = r
            d['payment_status'] = _translate_status(d.get('payment_status'))
            out.append(d)
        return out

    pending = _rows_to_list(pending)
    approved = _rows_to_list(approved)
    rejected = _rows_to_list(rejected)

    return render_template('admin.html', pending=pending, approved=approved, rejected=rejected, admin_logged_in=True)


@app.route('/admin/action', methods=['POST'])
def admin_action():
    if not require_admin():
        return redirect(url_for('login'))
    action = request.form.get('action')
    member_id = request.form.get('member_id')
    db = get_db()
    if not member_id:
        flash('Geçersiz istek')
        return redirect(url_for('admin'))
    try:
        if action == 'approve':
            db.execute("UPDATE members SET status = 'approved', approved_at = ? WHERE id = ?", (datetime.utcnow().isoformat(), member_id))
            db.commit()
            flash('Üye onaylandı')
        elif action == 'reject':
            db.execute("UPDATE members SET status = 'rejected' WHERE id = ?", (member_id,))
            db.commit()
            flash('Üye reddedildi')
        elif action == 'unreject':
            db.execute("UPDATE members SET status = 'pending' WHERE id = ?", (member_id,))
            db.commit()
            flash('Üye geri alındı')
        elif action == 'update_status':
            new_status = request.form.get('new_status')
            # if setting to Ödendi and no payment_date provided, fill with local now
            payment_date = request.form.get('payment_date') or None
            if new_status and str(new_status).lower().startswith('öden') and not payment_date:
                payment_date = datetime.now().isoformat()
                db.execute("UPDATE members SET payment_status = ?, payment_date = ? WHERE id = ?", (new_status, payment_date, member_id))
            else:
                db.execute("UPDATE members SET payment_status = ? WHERE id = ?", (new_status, member_id))
            db.commit()
            flash('Ödeme durumu güncellendi')
        elif action == 'delete':
            db.execute("DELETE FROM members WHERE id = ?", (member_id,))
            db.commit()
            flash('Kayıt silindi')
    except Exception as e:
        flash('İşlem sırasında hata: ' + str(e))
    return redirect(url_for('admin'))


@app.route('/admin/edit/<int:member_id>', methods=['GET', 'POST'])
def admin_edit(member_id):
    if not require_admin():
        return redirect(url_for('login'))
    db = get_db()
    row = db.execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()
    if not row:
        flash('Üye bulunamadı')
        return redirect(url_for('admin'))
    form = EditForm(obj=row)
    # ensure a CSRF token is available in the session/template
    try:
        generate_csrf()
    except Exception:
        pass
    if form.validate_on_submit():
            name = form.name.data.strip() if form.name.data else ''
            email = form.email.data.strip() if form.email.data else ''
            phone = form.phone.data.strip() if form.phone.data else ''
            payment_status = form.payment_status.data
            payment_date = form.payment_date.data

            # If marked as paid but no date provided, set local current datetime
            if (not payment_date) and payment_status and str(payment_status).lower().startswith('öden'):
                payment_date = datetime.now().isoformat()

            # If phone left empty, keep existing
            if not phone:
                phone = row['phone']

            # Only update fields that are provided (name/email are kept if empty)
            update_fields = {
                'name': name or row['name'],
                'email': email or row['email'],
                'phone': phone,
                'payment_status': payment_status,
                'payment_date': payment_date
            }

            db = get_db()
            db.execute(
                """
                UPDATE members SET name=?, email=?, phone=?, payment_status=?, payment_date=? WHERE id=?
                """,
                (update_fields['name'], update_fields['email'], update_fields['phone'], update_fields['payment_status'], update_fields['payment_date'], member_id)
            )
            db.commit()
            flash('Güncellendi', 'success')
            # After saving, redirect back to admin panel per request
            return redirect(url_for('admin'))
    # convert row to dict-like for template
    member = dict(row)
    return render_template('admin_edit.html', form=form, member=member)


if __name__ == '__main__':
    app.run(debug=True)
