import os
from app import app

print('cwd=', os.getcwd())
print('app.root_path=', app.root_path)
print('app.template_folder=', app.template_folder)
print('templates dir exists?', os.path.isdir(os.path.join(app.root_path, app.template_folder)))
print('list templates:')
try:
    print(os.listdir(os.path.join(app.root_path, app.template_folder)))
except Exception as e:
    print('list error', e)

with app.app_context():
    try:
        t = app.jinja_env.get_template('index.html')
        src = t.render(admin_logged_in=False)
        print('rendered length:', len(src))
        print('first 2000 chars:\n', src[:2000])
    except Exception as e:
        import traceback
        traceback.print_exc()
