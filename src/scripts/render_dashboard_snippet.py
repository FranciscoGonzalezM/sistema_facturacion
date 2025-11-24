from django.test import Client
c=Client()
c.post('/login/', {'company':'ACME','username':'cajero1','password':'cajero123'}, follow=True)
dash=c.get('/dashboard/mi-dashboard/')
txt=dash.content.decode('utf-8')
start=txt.find('<div class="top-buttons">')
if start==-1:
    print('no top-buttons')
else:
    end=txt.find('</div>', start)
    print(txt[start:end+6])
    # also print sidebar block
    sb_start = txt.find('<nav id="sidebar">')
    if sb_start!=-1:
        sb_end = txt.find('</nav>', sb_start)
        print('\n--- SIDEBAR ---')
        print(txt[sb_start:sb_end+6])
