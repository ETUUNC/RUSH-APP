from app import app

with app.test_client() as c:
    r = c.get('/login')
    html = r.get_data(as_text=True)
    print(html)
