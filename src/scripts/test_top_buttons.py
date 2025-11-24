from django.test import Client
c=Client()
resp = c.post('/login/', {'company':'ACME','username':'tenantuser','password':'testpass123'}, follow=True)
d = c.get('/dashboard/mi-dashboard/')
print('tenantuser status', d.status_code)
print('tenantuser has top-buttons?', '<div class="top-buttons">' in d.content.decode('utf-8'))

c.logout()
resp = c.post('/login/', {'company':'ACME','username':'cajero1','password':'cajero123'}, follow=True)
d2 = c.get('/dashboard/mi-dashboard/')
print('cajero1 status', d2.status_code)
print('cajero1 has top-buttons?', '<div class="top-buttons">' in d2.content.decode('utf-8'))
