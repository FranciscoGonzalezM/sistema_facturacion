from django.test import Client
c = Client()
# login cajero
c.post('/login/', {'company':'ACME', 'username':'cajero1', 'password':'cajero123'}, follow=True)
r = c.get('/dashboard/mi-dashboard/')
s = r.content.decode('utf-8')
start = s.find('<ul class="nav flex-column">')
if start != -1:
    end = s.find('</ul>', start)
    print(s[start:end+5])
else:
    print('no ul found')
