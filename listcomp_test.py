from pprint import pprint
import requests

projecturl="https://dpslackbotlistnr-dev.aexp.com/api/v1/tickroperations/projects?carid=200003973"
serviceurl="https://dpslackbotlistnr-dev.aexp.com/api/v1/tickroperations/services?projects={}"
podsurl="https://dpslackbotlistnr-dev.aexp.com/api/v1/tickroperations/pods?projects={}&services={}"
project=requests.get(url=projecturl).json()
p={}
s={}
for i in project:
    service=requests.get(serviceurl.format(i)).json()
    s={}
    for j in service:
        pods = requests.get(podsurl.format(i,j)).json()
        s.update({j:pods})
    print(s)
    p.update({i:s})
print(p)

pprint(p)