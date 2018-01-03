#!/usr/bin/env python3
import requests, re,io,json
from lxml import html
import hmac, hashlib, base64
from bs4 import BeautifulSoup
import urllib.request
from tabulate import tabulate
s=requests.Session()
def hash(password,contextdata):
    return hmac.new(contextdata.encode('ascii'), base64.b64encode(hashlib.md5(password.encode('ascii')).digest()).replace(b"=", b""), hashlib.md5).hexdigest()
def login(user,pw):
    url="https://powerschool.sandi.net/guardian/home.html"
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
    p=s.post(url, data=payload)
    return p
def createSmallClass(teacher, grade):
    data={}
    data["teacher"]=teacher
    data["grade"]=grade
    return data
def getRawClass(p):
    x={}
    data=BeautifulSoup(p.content, "lxml")
    grades=data.findAll("a", { "class" : "bold" })
    tr=data.findAll('tr', {"id":re.compile("^ccid_\d+")})
    for i in range (0,6):
        td=tr[i].findAll('td')
        grade=td[len(td)-3]
        a=list(grade.find("a").getText())
        del a[0]
        a="".join(a)
        teacher=tr[i].find("span",{ "class" : "screen_readers_only" }).parent["title"].strip("Details about ").replace(",","").split(" ")
        teacher.reverse()
        if(len(teacher)==3):
            del teacher[0]
        teacher= " ".join(teacher)
        x["{}".format(i+1)]=createSmallClass(teacher, a)
    return x
def createSmallAssignment(date, category, name, score, percent):
    data={}
    data["date"]=date
    data["category"]=category
    data["name"]=name
    data["score"]=score
    data["percent"]=percent
    return data
def getRawAssignments(p,period):
    data=BeautifulSoup(p.content, "lxml")
    grades=data.findAll("a", { "class" : "bold" })
    tr=data.findAll('tr', {"id":re.compile("^ccid_\d+")})
    td=tr[period-1].findAll('td')
    grade=td[len(td)-3]
    a=list(grade.find("a").getText())
    href="https://powerschool.sandi.net/guardian/"+grade.find("a")['href']

    p=s.get(href, headers = {'Accept-Encoding': 'identity'})
    data=BeautifulSoup(p.content, "lxml")
    table=data.find("table", { "align" : "center" })
    tr=table.findAll("tr")
    assignments={}
    for i in range (1,len(tr)):
        td=tr[i].findAll("td")
        assignments["{}".format(hex(i))]=createSmallAssignment(td[0].getText(),td[1].getText(),td[2].getText(),td[8].getText(),td[9].getText())
    return assignments
    return all
def getAllClass(p,period):
    data={}
    data["{}".format(period)]=getRawAssignments(p,period)
    data["assignments"]=data.pop("{}".format(period))
    data["info"]=getRawClass(p)["{}".format(period)]
    return data
def getAllAssignments(p):
    data={}
    for i in range(1,7):
        data["{}".format(i)]=getRawAssignments(p,i)
    return data
def getAllGrades(p):
    data={}
    for i in range(1,7):
        data["{}".format(i)]=getAllClass(p,i)
    return data
def printJSON(data):
    print(json.dumps(data))
