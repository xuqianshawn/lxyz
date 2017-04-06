import sys
import urllib
import json
import requests
import time
import copy
from pprint import pprint
from difflib import Differ
from copy import deepcopy
import os
import requests
import re
import urllib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException


success_payloads = {}

jsonform = []
loginPayloadDict = {}
vunlerableUrlWithParam = {}
appname = sys.argv[1:][0]
defaultHeader = {
    "Referer": "https://app5.com/www/index.php",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36"
}

def self_checkIfCanLogin(payload, loginurl, header):
	request = requests.post(loginurl, data=payload, headers=header, verify=False)
	content = request.content.lower().replace(" ", "")
	if ("logout" in content) and (request.status_code == 200):
		return True
	if "session expired" in content:
		return False
	for param in payload:
		print param
		if ("name='"+str(param)+"'" in content) or ('name="'+str(param)+'"' in content):
			return False
	return True

def self_checkIfCanLogin_withSession(s,payload, loginurl, header):
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

def self_checkIfCanLoginandAttack(payload, loginurl, header):
    response = requests.post(loginurl, data=payload, headers=header,
                            verify=False)
    if response.text.encode('utf-8').find('cs5331_g7'):
        return True


def self_checkStillLoggedIn(loginpayload, content):
    content = content.lower().replace(" ", "")
    # if ("logout" in content):
    if "session expired" in content:
        return False
    if ("logout" in content):
        return True
    for param in loginpayload:
        if ("name='" + str(param) + "'" in content) or (
                    'name="' + str(param) + '"' in content):
            if len(content) > 0:
                text_file = open("Output.txt", "w")
                text_file.write(content)
                text_file.close()
            return False
    return True


def self_post(load, url, header):
    request = requests.post(url, data=load, headers=header, verify=False)
    return request


def self_get(load, url, header):
    request = requests.get(url, params=load, headers=header, verify=False)
    return request


def self_parseURL(url):
	if "?" in url:
		index = int(url.find("?"))
		return url[0:index]


with open('../payloads.txt') as payload_file:
    payloads = payload_file.read().splitlines()
    print payloads
    print 'payloads', len(payloads)

with open('../config.json') as file:
    print "--------------loading login information--------------------"
    data = json.load(file)
    for loginurls in data["loginurls"]:
        if loginurls["name"] == appname:
            loginurl = loginurls["login_url"]
            loginPayload = loginurls["loginpayload"]

            loginPayloadDict[loginurl] = loginPayload
print loginPayloadDict


def verify(file_path, delay=3):
    success = False
    driver = webdriver.Firefox()
    try:
        print file_path
        driver.get('file://' + file_path)
        time.sleep(delay)
        alert = driver.switch_to_alert()
        alert.accept()
        success = True
    except:
        success = False
    finally:
        try:
            driver.close()
        except:
            pass
    return success


with open("../step1results/" + appname + '.json') as data_file:
    # with open('phase1.json') as data_file:
    print "--------------loading url information--------------------"
    data = json.load(data_file)
    urlsToProcess = data["urls"]
    for urls in data["urls"]:
        url = urls["url"]
        if (url in loginPayloadDict) and (urls["type"] == "POST") and urls[
            "param"]:
            urlsToProcess.remove(urls)
            print urls
            # process login urls firstif url in loginPayloadDict:
            # it's a log in url
            # get all log in accounts and password
            crendentials = loginPayloadDict[url]
            initialLoad = copy.deepcopy(urls["param"])
            # get first log in credential to test is enough
            # assign param to crendentials
            for param in crendentials:
                initialLoad[param] = [crendentials[param]]
            credential = copy.deepcopy(initialLoad)
            print '----', credential

            # try to log in and get the response content
            loginStatus = self_checkIfCanLogin(credential, url, defaultHeader)
            if not loginStatus:
                print "Login fail, please check your credentials below"
                print url
                print credential
            else:
                # try different payload to test if login has vunlerbility
                for payload in payloads:
                    print payload
                    for param in credential:
                        # replace the login parameter with different payload, test if can log in
                        fakeCredential = copy.deepcopy(credential)
                        if param in loginPayloadDict[url]:
                            fakeCredential[param] = payload
                        # if self_checkIfCanLoginandAttack(fakeCredential, url, defaultHeader):
                        #     print 'url:', url, 'payload: ', payload
                loginPayloadDict[url] = credential

    data["urls"] = copy.deepcopy(urlsToProcess)

    # print"-------------Processing get and required log in-----------------------"
    # url_success_withoutlogin = {}
    # url_failed_withoutlogin = {}
    # # process those get parameter with login required
    # for urls in data["urls"]:
    #     url = urls["url"]
    #     if True: #(urls["loginrequired"] == "false"): # and (url not in loginPayloadDict):
    #         print url
    #         with requests.Session() as s:
    #             if (url, None) not in url_success_withoutlogin and (url, None) not in url_failed_withoutlogin:
    #                 success0 = False
    #                 for payload in payloads:
    #                     # url+payload attack:
    #                     full_url0 = url + payload
    #                     r = s.get(full_url0, verify=False)
    #                     file_path0 = ''
    #                     with open(appname + '.html', 'wb') as f20:
    #                         f20.write(r.text.encode('utf-8'))
    #                         file_path0 = os.path.realpath(f20.name)
    #                     success0 = verify(file_path0)
    #                     if success0:
    #                         print 'Attack Success0 =====', full_url0, url, None, payload,
    #                         url_success_withoutlogin[(url, None)] = (payload, full_url0)
    #                         break
    #                 if not success0:
    #                     # if none of the parload success ful, this usr + parameters are all failed
    #                     url_failed_withoutlogin[(url, None)] = None
    # pprint(url_success_withoutlogin)
    # print '-------/n'
    # pprint(url_failed_withoutlogin)

    # url_success = {}
    # url_failed = {}
    # # process those get parameter with login required
    # for urls in data["urls"]:
    #     if (urls["type"] == "GET") and (urls["loginrequired"] == "true") and (url not in loginPayloadDict):
    #         urlsToProcess.remove(urls)
    #         initialheader = defaultHeader
    #         loginurl = urls["loginurl"]
    #         # Log in first
    #         # get log in url from config file
    #         if loginurl in loginPayloadDict:
    #             # it's a log in url
    #             credential = loginPayloadDict[loginurl]
    #             loginpayload = credential
    #             with requests.Session() as s:
    #                 if self_checkIfCanLogin_withSession(s, loginpayload, loginurl, defaultHeader):
    #                     # attacking!
    #                     for ap in urls['param']:
    #                         if (url, ap) in url_success or (url, ap) in url_failed:
    #                             continue
    #
    #                         # # for url+payload(ignore parameters) attack
    #                         # # todo: before login attack once also
    #                         # if (url, None) not in url_success and (url, None) not in url_failed:
    #                         #     print url
    #                         #     success0 = False
    #                         #     for payload in payloads:
    #                         #         # url+payload attack:
    #                         #         full_url0 = url+payload
    #                         #         r = s.get(full_url0, verify=False)
    #                         #         file_path0 = ''
    #                         #         with open(appname + '.html', 'wb') as f20:
    #                         #             f20.write(r.text.encode('utf-8'))
    #                         #             file_path0 = os.path.realpath(f20.name)
    #                         #         success0 = verify(file_path0)
    #                         #         if success0:
    #                         #             print 'Attack Success0 =====', full_url0, url, None, payload,
    #                         #             url_success[(url, None)] = (payload, full_url0)
    #                         #             break
    #                         #     if not success0:
    #                         #         # if none of the parload success ful, this usr + parameters are all failed
    #                         #         url_failed[(url, None)] = None
    #
    #                         # for url+parameters change to payload get attack
    #                         success = False
    #                         for payload in payloads:
    #                             # get attack for get requests
    #                             attack_payloads = deepcopy(urls['param'])
    #                             attack_payloads[ap][0] = payload
    #                             full_url = url+'?'
    #                             attackStrings = []
    #                             for attack_param in attack_payloads:
    #                                 attackStrings.append(attack_param +"="+ attack_payloads[attack_param][0])
    #                             full_attackString = '&'.join(attackStrings)
    #                             full_url += full_attackString
    #                             print full_url
    #                             r = s.get(full_url, verify=False)
    #                             file_path = ''
    #                             with open(appname+'.html', 'wb') as f2:
    #                                 f2.write(r.text.encode('utf-8'))
    #                                 file_path = os.path.realpath(f2.name)
    #
    #                             success = verify(file_path)
    #                             if success:
    #                                 print 'Attack Success', full_url, url, ap, payload, '=================='
    #                                 url_success[(url, ap)] = (payload, full_url)
    #                                 break
    #                         # none of the payload can attack
    #                         if not success:
    #                             # if none of the parload success ful, this usr + parameters are all failed
    #                             url_failed[(url, ap)] = None
    #                 else:
    #                     print 'login failed ********************'
    #
    # pprint(url_success)
    # print '-------/n'
    # pprint(url_failed)

    url_success = {}
    url_failed = {}
    count = 0
    step3JsonForm = {}
    step3result_folder_name = './step3results/'
    # process those get parameter with login required
    for urls in data["urls"]:
        if count > 1000:
            break
        if (urls["type"] == "GET") and (urls["loginrequired"] == "true") and (url not in loginPayloadDict):
            urlsToProcess.remove(urls)
            initialheader = defaultHeader
            loginurl = urls["loginurl"]
            # Log in first
            # get log in url from config file
            if loginurl in loginPayloadDict:
                # it's a log in url
                credential = loginPayloadDict[loginurl]
                loginpayload = credential
                with requests.Session() as s:
                    if self_checkIfCanLogin_withSession(s,
                                                        loginpayload,
                                                        loginurl,
                                                        defaultHeader):
                        # attacking!
                        for ap in urls['param']:
                            step3JsonForm.setdefault((url+'_'+ap), [])
                            # for url+parameters change to payload get attack
                            success = False
                            for payload in payloads:
                                # get attack for get requests
                                attack_payloads = deepcopy(urls['param'])
                                attack_payloads[ap][0] = payload
                                full_url = url + '?'
                                attackStrings = []
                                for attack_param in attack_payloads:
                                    attackStrings.append(attack_param + "=" +
                                                         attack_payloads[
                                                             attack_param][0])
                                full_attackString = '&'.join(attackStrings)
                                full_url += full_attackString
                                print full_url
                                r = s.get(full_url, verify=False)
                                file_path = ''
                                print count
                                count += 1
                                if not os.path.exists(step3result_folder_name):
                                    os.makedirs(step3result_folder_name)

                                with open(step3result_folder_name + appname + str(count) + '.html', 'wb') as f2:
                                    f2.write(r.text.encode('utf-8'))
                                    file_path = os.path.realpath(f2.name)
                                    step3JsonForm[(url+'_'+ap)].append([appname + str(count) + '.html', 'GET', full_url, attack_payloads])
                    else:
                        print 'login failed ********************'
    step3result_1 = {'result': step3JsonForm}
    with open(step3result_folder_name + 'step3.json','wb') as fp:
            json.dump(step3result_1, fp)





    # print"-------------Processing get and not required log in-----------------------"
    # # process those get parameter with out login required
    # for urls in data["urls"]:
    #     url = urls["url"]
    #     if (urls["type"] == "GET") and (urls["loginrequired"] == "false") and (
    #         url not in loginPayloadDict):
    #         urlsToProcess.remove(urls)
    #         initialLoad = copy.deepcopy(urls["param"])
    #         initialheader = defaultHeader
    #         # An authorised request.
    #         initialLoad = copy.deepcopy(urls["param"])
    #         start = time.time()
    #         initialRequest = requests.get(url, params=initialLoad,
    #                                       headers=initialheader,
    #                                       verify=False)  # s.get(url,params = initialLoad, headers=header, verify = False)
    #         initialContent = initialRequest.content
    #         initialTrip = time.time() - start
    #         print "-------------------Initial Request---------------------"
    #         print initialRequest.headers
    #         print url
    #         print initialLoad
    #         print "----------------------------------------"
    #         initialLength = len(
    #             initialRequest.content)  # int(initialRequest.headers["Content-Length"])
    #         initialStatus = initialRequest.status_code
    #         initialEndingUrl = initialRequest.url
    #         parsedUrl = self_parseURL(initialEndingUrl)
    #         for param in initialLoad:
    #             if parsedUrl in vunlerableUrlWithParam:
    #                 listOfParam = vunlerableUrlWithParam[parsedUrl]
    #                 if param in listOfParam:
    #                     # this param with this url already identified as vunlerable, skip the rest of the test
    #                     continue
    #             load = copy.deepcopy(initialLoad)
    #             if (not load[param]) or (load[param][0] is None) or (
    #                 load[param][0] == "None"):
    #                 load[param] = ["'"]
    #             else:
    #                 load[param][0] = load[param][0] + "'"
    #             newurl = url + "?"
    #             for l in load:
    #                 newurl = newurl + l + "=" + load[l][0] + "&"
    #             newurl = newurl[0:-1]
    #             falseRequest = requests.get(newurl, headers=initialheader,
    #                                         verify=False)
    #             if self_gotsqlsyntaxerror(falseRequest.content):
    #                 # got sql syntax error hack successful
    #                 # break for loop
    #                 if parsedUrl in vunlerableUrlWithParam:
    #                     listOfParam = vunlerableUrlWithParam[parsedUrl]
    #                     if param not in listOfParam:
    #                         listOfParam.append(param)
    #                 else:
    #                     listOfParam = [param]
    #                     vunlerableUrlWithParam[parsedUrl] = listOfParam
    #
    #                     initialUrl = copy.deepcopy(urls)
    #                     initialUrl["param"] = load
    #                     initialUrl["newurl"] = newurl
    #                     jsonform.append(initialUrl)
    #                 continue
    #             for payload in payloads:
    #                 if payload.endswith('#'):
    #                     # do not do this for get request...
    #                     continue
    #                 ifisSleepCommand = False
    #                 if "sleep" in payload:
    #                     ifisSleepCommand = True
    #                 # replace each parameter with the payload to test
    #                 load = copy.deepcopy(initialLoad)
    #                 # print load[param]
    #                 # print param
    #                 # print type(load[param])
    #                 if (not load[param]) or (load[param][0] is None) or (
    #                     load[param][0] == "None"):
    #                     load[param] = [payload]
    #                 else:
    #                     load[param][0] = load[param][0] + payload
    #                 newurl = url + "?"
    #                 for l in load:
    #                     newurl = newurl + l + "=" + load[l][0] + "&"
    #                 newurl = newurl[0:-1]
    #                 start = time.time()
    #                 # r = s.get(url,params = load, headers=header, verify = False)
    #                 r = requests.get(newurl, headers=initialheader,
    #                                  verify=False)
    #                 newContent = r.content
    #                 trip = time.time() - start
    #                 if self_gotsqlsyntaxerror(r.content):
    #                     # got sql syntax error hack successful
    #                     # break for loop
    #                     parsedUrl = self_parseURL(initialRequest.url)
    #                     if parsedUrl in vunlerableUrlWithParam:
    #                         listOfParam = vunlerableUrlWithParam[parsedUrl]
    #                         if param not in listOfParam:
    #                             listOfParam.append(param)
    #                     else:
    #                         listOfParam = [param]
    #                         vunlerableUrlWithParam[parsedUrl] = listOfParam
    #                         initialUrl = copy.deepcopy(urls)
    #                         initialUrl["param"] = load
    #                         initialUrl["newurl"] = newurl
    #                         jsonform.append(initialUrl)
    #
    #                         text_file = open("Output.txt", "w")
    #                         text_file.write(newContent)
    #                         text_file.close()
    #                         text_file = open("OutputInitial.txt", "w")
    #                         text_file.write(initialContent)
    #                         text_file.close()
    #                     continue
    #                 print "-----------Result----------------"
    #                 try:
    #                     resultArray = self_hijackSuccessful(initialRequest, r,
    #                                                         falseRequest,
    #                                                         ifisSleepCommand,
    #                                                         payload, False,
    #                                                         initialTrip, trip,
    #                                                         {}, param)
    #                     issuccessful = resultArray[0]
    #                     print resultArray[1]
    #                 except:
    #                     issuccessful = False
    #                 print newurl
    #                 print issuccessful
    #                 if issuccessful:
    #                     initialUrl = copy.deepcopy(urls)
    #                     initialUrl["param"] = load
    #                     initialUrl["newurl"] = newurl
    #                     jsonform.append(initialUrl)
    #
    #                     text_file = open("Output.txt", "w")
    #                     text_file.write(newContent)
    #                     text_file.close()
    #                     text_file = open("OutputInitial.txt", "w")
    #                     text_file.write(initialContent)
    #                     text_file.close()
    #
    #         hackHeader = copy.deepcopy(initialheader)
    #         hackHeader["referer"] = "some random header"
    #         requestAfterHeaderChange = requests.get(url, params=initialLoad,
    #                                                 headers=hackHeader,
    #                                                 verify=False)
    #         hackContentLength = len(requestAfterHeaderChange.content)
    #         if abs(hackContentLength - initialLength) > 20:
    #             # header may be used to hack
    #             for payload in payloads:
    #                 hackHeader = copy.deepcopy(initialheader)
    #                 hackHeader["referer"] = "some random header"
    #                 requestAfterHeaderChange = requests.get(url,
    #                                                         params=initialLoad,
    #                                                         headers=hackHeader,
    #                                                         verify=False)
    #                 hackContentLength = len(requestAfterHeaderChange.content)
    #                 if hackContentLength == initialLength:
    #                     initialUrl = copy.deepcopy(urls)
    #                     initialUrl["param"] = load
    #                     initialUrl["newurl"] = newurl
    #                     initialUrl["headers"] = hackHeader
    #                     jsonform.append(initialUrl)
    # data["urls"] = copy.deepcopy(urlsToProcess)
    #
    # print"-------------Processing post and not required log in-----------------------"
    # # process those post parameter with out login required
    # for urls in data["urls"]:
    #     url = urls["url"]
    #     initialheader = defaultHeader
    #     if (urls["type"] == "POST") and (urls["loginrequired"] == "false") and (
    #         url not in loginPayloadDict):
    #         urlsToProcess.remove(urls)
    #         # An authorised request.
    #         initialLoad = copy.deepcopy(urls["param"])
    #         # put some initial value to the post
    #         for param in initialLoad:
    #             if (not initialLoad[param]) | (
    #                 initialLoad[param][0] is None) | (
    #                 initialLoad[param][0] == "") | (
    #                 initialLoad[param][0] == "None"):
    #                 initialLoad[param] = ["a"]
    #         start = time.time()
    #         initialRequest = requests.post(url, params=initialLoad,
    #                                        headers=defaultHeader, verify=False)
    #         initialContent = initialRequest.content
    #         initialTrip = time.time() - start
    #         print "-------------------Initial Request---------------------"
    #         print initialRequest.headers
    #         print url
    #         print initialLoad
    #         print "----------------------------------------"
    #         initialLength = len(
    #             initialRequest.content)  # int(initialRequest.headers["Content-Length"])
    #         initialStatus = initialRequest.status_code
    #         initialEndingUrl = initialRequest.url
    #         parsedUrl = self_parseURL(initialRequest.url)
    #         for param in initialLoad:
    #             if parsedUrl in vunlerableUrlWithParam:
    #                 listOfParam = vunlerableUrlWithParam[parsedUrl]
    #                 if param in listOfParam:
    #                     # this param with this url already identified as vunlerable, skip the rest of the test
    #                     continue
    #             load = copy.deepcopy(initialLoad)
    #             if (not load[param]) or (load[param][0] is None) or (
    #                 load[param][0] == "None"):
    #                 load[param] = ["'"]
    #             else:
    #                 load[param][0] = load[param][0] + "'"
    #             falseRequest = requests.post(url, data=load,
    #                                          headers=defaultHeader,
    #                                          verify=False)
    #
    #             if self_gotsqlsyntaxerror(falseRequest.content):
    #                 # got sql syntax error hack successful
    #                 # break for loop
    #                 parsedUrl = self_parseURL(initialRequest.url)
    #                 if parsedUrl in vunlerableUrlWithParam:
    #                     listOfParam = vunlerableUrlWithParam[parsedUrl]
    #                     if param not in listOfParam:
    #                         listOfParam.append(param)
    #                 else:
    #                     listOfParam = [param]
    #                     vunlerableUrlWithParam[parsedUrl] = listOfParam
    #
    #                     initialUrl = copy.deepcopy(urls)
    #                     initialUrl["param"] = load
    #                     jsonform.append(initialUrl)
    #                 continue
    #             for payload in payloads:
    #                 # replace each parameter with the payload to test
    #                 # only test blind
    #                 # only test blind sql for post
    #                 ifisSleepCommand = False
    #                 if "sleep" in payload:
    #                     ifisSleepCommand = True
    #                     load = copy.deepcopy(initialLoad)
    #                 # print load[param]
    #                 # print param
    #                 # print type(load[param])
    #                 if (not load[param]) or (load[param][0] is None) or (
    #                     load[param][0] == "None"):
    #                     load[param] = [payload]
    #                 else:
    #                     load[param][0] = load[param][0] + payload
    #                 start = time.time()
    #                 r = requests.post(url, data=load, headers=defaultHeader,
    #                                   verify=False)
    #                 newContent = r.content
    #                 if self_gotsqlsyntaxerror(r.content):
    #                     # got sql syntax error hack successful
    #                     # break for loop
    #                     parsedUrl = self_parseURL(initialRequest.url)
    #                     if parsedUrl in vunlerableUrlWithParam:
    #                         listOfParam = vunlerableUrlWithParam[parsedUrl]
    #                         if param not in listOfParam:
    #                             listOfParam.append(param)
    #                     else:
    #                         listOfParam = [param]
    #                         vunlerableUrlWithParam[parsedUrl] = listOfParam
    #                         initialUrl = copy.deepcopy(urls)
    #                         initialUrl["param"] = load
    #                         initialUrl["newurl"] = newurl
    #                         jsonform.append(initialUrl)
    #
    #                         text_file = open("Output.txt", "w")
    #                         text_file.write(newContent)
    #                         text_file.close()
    #                         text_file = open("OutputInitial.txt", "w")
    #                         text_file.write(initialContent)
    #                         text_file.close()
    #                     continue
    #                 trip = time.time() - start
    #                 length = len(r.content)
    #
    #                 print "-----------Result----------------"
    #                 try:
    #                     resultArray = self_hijackSuccessful(initialRequest, r,
    #                                                         falseRequest,
    #                                                         ifisSleepCommand,
    #                                                         payload, True,
    #                                                         initialTrip, trip,
    #                                                         {}, param)
    #                     issuccessful = resultArray[0]
    #                     print resultArray[1]
    #                 except:
    #                     issuccessful = False
    #                 print issuccessful
    #                 if issuccessful:
    #                     initialUrl = copy.deepcopy(urls)
    #                     initialUrl["param"] = load
    #                     jsonform.append(initialUrl)
    #
    #                     text_file = open("Output.txt", "w")
    #                     text_file.write(newContent)
    #                     text_file.close()
    #                     text_file = open("OutputInitial.txt", "w")
    #                     text_file.write(initialContent)
    #                     text_file.close()
    #
    #         hackHeader = copy.deepcopy(defaultHeader)
    #         hackHeader["referer"] = "some random header"
    #         requestAfterHeaderChange = requests.post(url, data=initialLoad,
    #                                                  headers=hackHeader,
    #                                                  verify=False)
    #         hackContentLength = len(requestAfterHeaderChange.content)
    #         if abs(hackContentLength - initialLength) > 20:
    #             # header may be used to hack
    #             for payload in payloads:
    #                 hackHeader = copy.deepcopy(initialheader)
    #                 hackHeader["referer"] = "some random header"
    #                 requestAfterHeaderChange = requests.post(url,
    #                                                          data=initialLoad,
    #                                                          headers=hackHeader,
    #                                                          verify=False)
    #                 hackContentLength = len(requestAfterHeaderChange.content)
    #                 if hackContentLength == initialLength:
    #                     initialUrl = copy.deepcopy(urls)
    #                     initialUrl["param"] = load
    #                     initialUrl["headers"] = hackHeader
    #                     jsonform.append(initialUrl)
    # data["urls"] = copy.deepcopy(urlsToProcess)
    #
    # print"-------------Processing post and required log in-----------------------"
    # # process those post parameter with login required
    # for urls in data["urls"]:
    #     url = urls["url"]
    #     initialheader = defaultHeader
    #     if (urls["type"] == "POST") and (urls["loginrequired"] == "true") and (
    #         url not in loginPayloadDict):
    #         urlsToProcess.remove(urls)
    #         loginurl = urls["loginurl"]
    #         # Log in first
    #         # get log in url from config file
    #         if loginurl in loginPayloadDict:
    #             # it's a log in url
    #             credential = loginPayloadDict[loginurl]
    #             loginpayload = credential
    #             with requests.Session() as s:
    #                 print loginpayload
    #                 p = s.post(loginurl, data=loginpayload, verify=False)
    #                 if p.status_code != 200:
    #                     print "Error while log in"
    #                 else:
    #                     # An authorised request.
    #                     initialLoad = copy.deepcopy(urls["param"])
    #                     # put some initial value to the post
    #                     for param in initialLoad:
    #                         print initialLoad
    #                         print param
    #                         print initialLoad[param]
    #                         if (not initialLoad[param]) | (
    #                             initialLoad[param][0] is None) | (
    #                             initialLoad[param][0] == "") | (
    #                             initialLoad[param][0] == "None"):
    #                             initialLoad[param] = ["a"]
    #                     start = time.time()
    #                     initialRequest = s.post(url, data=initialLoad,
    #                                             headers=defaultHeader,
    #                                             verify=False)
    #                     initialContent = initialRequest.content
    #                     initialTrip = time.time() - start
    #                     print "-------------------Initial Request---------------------"
    #                     print initialRequest.headers
    #                     print url
    #                     print initialLoad
    #                     print "----------------------------------------"
    #                     initialLength = len(
    #                         initialRequest.content)  # int(initialRequest.headers["Content-Length"])
    #                     initialStatus = initialRequest.status_code
    #                     initialEndingUrl = initialRequest.url
    #                     parsedUrl = self_parseURL(initialRequest.url)
    #                     for param in initialLoad:
    #                         if parsedUrl in vunlerableUrlWithParam:
    #                             listOfParam = vunlerableUrlWithParam[parsedUrl]
    #                             if param in listOfParam:
    #                                 # this param with this url already identified as vunlerable, skip the rest of the test
    #                                 continue
    #                         load = copy.deepcopy(initialLoad)
    #                         if (not load[param]) or (
    #                             load[param][0] is None) or (
    #                             load[param][0] == "None"):
    #                             load[param] = ["'"]
    #                         else:
    #                             load[param][0] = load[param][0] + "'"
    #                         falseRequest = s.post(url, data=load,
    #                                               headers=defaultHeader,
    #                                               verify=False)
    #                         if not self_checkStillLoggedIn(loginPayload,
    #                                                        falseRequest.content):
    #                             # if logged out after get, try to login again
    #                             p = s.post(loginurl, data=loginpayload,
    #                                        verify=False)
    #                         if self_gotsqlsyntaxerror(falseRequest.content):
    #                             # got sql syntax error hack successful
    #                             # break for loop
    #                             parsedUrl = self_parseURL(initialRequest.url)
    #                             if parsedUrl in vunlerableUrlWithParam:
    #                                 listOfParam = vunlerableUrlWithParam[
    #                                     parsedUrl]
    #                                 if param not in listOfParam:
    #                                     listOfParam.append(param)
    #                             else:
    #                                 listOfParam = [param]
    #                                 vunlerableUrlWithParam[
    #                                     parsedUrl] = listOfParam
    #
    #                                 initialUrl = copy.deepcopy(urls)
    #                                 initialUrl["param"] = load
    #                                 initialUrl["loginpayload"] = loginpayload
    #                                 jsonform.append(initialUrl)
    #                             continue
    #                         for payload in payloads:
    #                             # only test blind sql for post
    #                             ifisSleepCommand = False
    #                             if "sleep" in payload:
    #                                 ifisSleepCommand = True
    #                             # replace each parameter with the payload to test
    #                             load = copy.deepcopy(initialLoad)
    #                             # print load[param]
    #                             # print param
    #                             # print type(load[param])
    #                             if (not load[param]) or (
    #                                 load[param][0] is None) or (
    #                                 load[param][0] == "None"):
    #                                 load[param] = [payload]
    #                             else:
    #                                 load[param][0] = load[param][0] + payload
    #                             start = time.time()
    #                             r = s.post(url, data=load,
    #                                        headers=defaultHeader, verify=False)
    #
    #                             if not self_checkStillLoggedIn(loginPayload,
    #                                                            r.content):
    #                                 # if logged out after get, try to login again
    #                                 p = s.post(loginurl, data=loginpayload,
    #                                            verify=False)
    #                             if self_gotsqlsyntaxerror(r.content):
    #                                 # got sql syntax error hack successful
    #                                 # break for loop
    #                                 parsedUrl = self_parseURL(
    #                                     initialRequest.url)
    #                                 if parsedUrl in vunlerableUrlWithParam:
    #                                     listOfParam = vunlerableUrlWithParam[
    #                                         parsedUrl]
    #                                     if param not in listOfParam:
    #                                         listOfParam.append(param)
    #                                 else:
    #                                     listOfParam = [param]
    #                                     vunlerableUrlWithParam[
    #                                         parsedUrl] = listOfParam
    #                                     initialUrl = copy.deepcopy(urls)
    #                                     initialUrl["param"] = load
    #                                     initialUrl[
    #                                         "loginpayload"] = loginpayload
    #                                     initialUrl["newurl"] = newurl
    #                                     jsonform.append(initialUrl)
    #
    #                                     text_file = open("Output.txt", "w")
    #                                     text_file.write(newContent)
    #                                     text_file.close()
    #                                     text_file = open("OutputInitial.txt",
    #                                                      "w")
    #                                     text_file.write(initialContent)
    #                                     text_file.close()
    #                                 continue
    #                             newContent = r.content
    #                             trip = time.time() - start
    #                             length = len(r.content)
    #                             try:
    #                                 resultArray = self_hijackSuccessful(
    #                                     initialRequest, r, falseRequest,
    #                                     ifisSleepCommand, payload, True,
    #                                     initialTrip, trip, loginPayload, param)
    #                                 issuccessful = resultArray[0]
    #                                 print resultArray[1]
    #                             except:
    #                                 issuccessful = False
    #
    #                             print "-----------Result----------------"
    #                             print issuccessful
    #                             if issuccessful:
    #                                 initialUrl = copy.deepcopy(urls)
    #                                 initialUrl["param"] = load
    #                                 initialUrl["loginpayload"] = loginpayload
    #                                 jsonform.append(initialUrl)
    #
    #                                 text_file = open("Output.txt", "w")
    #                                 text_file.write(newContent)
    #                                 text_file.close()
    #                                 text_file = open("OutputInitial.txt", "w")
    #                                 text_file.write(initialContent)
    #                                 text_file.close()
    #
    #                     hackHeader = copy.deepcopy(defaultHeader)
    #                     hackHeader["referer"] = "some random header"
    #                     requestAfterHeaderChange = s.post(url, data=initialLoad,
    #                                                       headers=hackHeader,
    #                                                       verify=False)
    #                     hackContentLength = len(
    #                         requestAfterHeaderChange.content)
    #                     if abs(hackContentLength - initialLength) > 20:
    #                         # header may be used to hack
    #                         for payload in payloads:
    #                             hackHeader = copy.deepcopy(initialheader)
    #                             hackHeader["referer"] = "some random header"
    #                             requestAfterHeaderChange = s.post(url,
    #                                                               data=initialLoad,
    #                                                               headers=hackHeader,
    #                                                               verify=False)
    #                             hackContentLength = len(
    #                                 requestAfterHeaderChange.content)
    #                             if hackContentLength == initialLength:
    #                                 initialUrl = copy.deepcopy(urls)
    #                                 initialUrl["param"] = load
    #                                 initialUrl["loginpayload"] = loginpayload
    #                                 initialUrl["headers"] = hackHeader
    #                                 jsonform.append(initialUrl)
    # data["urls"] = copy.deepcopy(urlsToProcess)
#
# with open("../results/phase3_output_" + runname + ".json", 'w') as outfile:
#     json.dump(jsonform, outfile, indent=2)
# print "==========================Scan Finished========================================"