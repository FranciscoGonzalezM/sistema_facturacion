from django.test import Client
c=Client()
c.post('/login/', {'company':'ACME','username':'cajero1','password':'cajero123'}, follow=True)
dash=c.get('/dashboard/mi-dashboard/')
print('/mi-dashboard/ status', dash.status_code)
html=dash.content.decode('utf-8')
print('--- NAVBAR SNIPPET ---')
nb_start = html.find('<nav class="navbar')
if nb_start!=-1:
    nb_end = html.find('</nav>', nb_start)
    print(html[nb_start:nb_end+6])
else:
    print('no navbar')

print('\n--- SIDEBAR SNIPPET ---')
sb_start = html.find('<nav id="sidebar">')
if sb_start!=-1:
    sb_end = html.find('</nav>', sb_start)
    print(html[sb_start:sb_end+6])
else:
    print('no sidebar')

print('\ncontains /mi-dashboard/?', '/mi-dashboard/' in html)
print('contains company logo url?', 'organizaciones' in html and 'logo' in html)
