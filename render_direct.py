from app import app
import os

print('cwd=', os.getcwd())
print('template_folder=', os.path.join(app.root_path, app.template_folder))
print('templates exist?', os.path.isdir(os.path.join(app.root_path, app.template_folder)))
print('files:', os.listdir(os.path.join(app.root_path, app.template_folder)))

with app.app_context():
    tmpl = app.jinja_env.get_template('index.html')
    rendered = tmpl.render(admin_logged_in=False)
    print('rendered len =', len(rendered))
    print(rendered[:1200])
