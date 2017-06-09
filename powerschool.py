#!/usr/bin/env python3
import requests, re,io,json
from lxml import html
import hmac, hashlib, base64
from bs4 import BeautifulSoup

def hash(password,contextdata):
    return hmac.new(contextdata.encode('ascii'), base64.b64encode(hashlib.md5(password.encode('ascii')).digest()).replace(b"=", b""), hashlib.md5).hexdigest()

def login(user,pw):
    url="https://powerschool.sandi.net/guardian/home.html"
    s=requests.Session()
    result=s.get(url)
    tree = html.fromstring(result.text)
    pstoken = list(set(tree.xpath("//*[@id=\"LoginForm\"]/input[1]/@value")))[0]
    contextdata = list(set(tree.xpath("//input[@id=\"contextData\"]/@value")))[0]
    new_pw=hash(pw,contextdata)

    payload={
    'pstoken':pstoken,
    'contextData':contextdata,
    'dbpw':new_pw,
    'ldappassword':pw,
    'account':user,
    'pw':pw
    }
    p = s.post(url, data=payload)
    return p.content
def gradeextract(html):
    data=BeautifulSoup(html, "lxml")
    table = data.find('table',attrs={'class':'linkDescList'})
    grades=table.findAll("a", { "class" : "bold" })
    i=0
    while(i<len(grades)):
        classname=grades[i].parent.parent.find("span",{ "class" : "screen_readers_only" }).parent["title"].replace("Details about ","").split(", ")
        classname.reverse()
        
        classname=" ".join(classname).split(" ")
        del classname[1]
        classname=" ".join(classname)
        current_grade=list(grades[i].getText())
        letter_grade=current_grade[0]
        del current_grade[0]
        percent_grade="".join(current_grade)
        if(len(current_grade)>1):
            print(letter_grade, ": ",percent_grade, ": ",classname)
        
        i+=1

        
