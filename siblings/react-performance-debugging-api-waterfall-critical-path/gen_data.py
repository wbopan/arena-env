import json
import random

random.seed(1337)

POOL = ['auth', 'fetchUser', 'fetchConfig', 'fetchProfile', 'fetchCart',
        'fetchInventory', 'fetchPrices', 'fetchRecommendations', 'fetchReviews',
        'fetchShipping', 'fetchTax', 'fetchCoupons', 'logAnalytics', 'fetchFlags']
ROUTES = ['/api/checkout', '/api/products', '/api/cart', '/api/compare',
          '/api/orders', '/api/account', '/api/search']

data = {'routes': []}
for route in ROUTES:
    n = random.randint(5, 9)
    names = random.sample(POOL, n)
    ops = []
    for i, name in enumerate(names):
        k = min(i, random.choice([0, 1, 1, 2, 2, 3]))
        deps = random.sample(names[:i], k) if k else []
        ops.append({'name': name, 'duration_ms': random.randint(40, 700), 'depends_on': deps})
    data['routes'].append({'route': route, 'operations': ops})

with open('api_routes.json', 'w') as f:
    json.dump(data, f, indent=2)
