import sys
sys.path.insert(0, '.')
from app import app

with app.test_client() as client:
    # Test Nike
    print('Nike (3 links)...')
    resp = client.post('/scrape', json={
        'marca': 'Nike',
        'links': [
            'https://www.nike.com/es/w/nike-court-vision-low-next-nature-shoes-3q2xfq045',
            'https://www.amazon.com/-/es/Zapatos-Vision-Nature-hombre-Blanco/dp/B0983LWFXT',
            'https://www.ebay.com/sch/i.html?_nkw=nike+court+vision&rt=nc'
        ]
    })
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        print(f'Success: {resp.get_json().get("success", "?")}')
    else:
        print(f'Response: {resp.get_json()}')
