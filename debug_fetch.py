from app import app

with app.test_client() as c:
    for path in ['/', '/admin']:
        r = c.get(path)
        print('PATH', path, 'STATUS', r.status_code)
        data = r.get_data(as_text=True)
        print('LENGTH', len(data))
        print(data[:2000])
        print('\n' + ('='*80) + '\n')
