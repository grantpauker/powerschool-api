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
    'translator_username':'',
    'translator_password':'',
    'translator_ldappassword':'',
    'returnUrl':'',
    'serviceName':'PS Parent Portal',
    'serviceTicket':'',
    'pcasServerUrl':'\/',
    'credentialType':'User Id and Password Credential',
    'ldappassword':pw,
    'account':user,
    'pw':pw,
    'translatorpw':''
    }
    p = s.post(url, data=payload)
    data=BeautifulSoup(p.content, "lxml")
    table = data.find('table',attrs={'class':'linkDescList'})
    return toparagraph(str(table), ' ')

def toparagraph(txt, method):
    rawarr = txt.split(method)
    outstr = ""
    newvar = 0
    while(newvar < len(rawarr)):
        outstr += rawarr[newvar] + "\n"
        newvar += 1
    return outstr
