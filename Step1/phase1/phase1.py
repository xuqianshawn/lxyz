import json
import os
import sys
from scrapy.crawler import CrawlerProcess
from project.spiders.test import TestSpider
from scrapy.utils.project import get_project_settings

output_urls = []



def loopThroughAppInConfig(appName):
    with open('./config.json') as config_file:
        configs = json.load(config_file)["loginurls"]
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        for config in configs:

            currentAppname = config["name"]
            if currentAppname == appName:
             output_file = "../results/" + config["name"] + ".json"
             removeFromLocal(output_file)
             TestSpider.name=currentAppname
             process.crawl(TestSpider,
                          start_url=config["start_url"],
                          domain=config["domain"],
                          login_page=config["login_page"],
                          login_url=config["login_url"],
                          username=config["loginpayload"][config["username_field"]],
                          password=config["loginpayload"][config["password_field"]],
                          username_field=config["username_field"],
                          password_field=config["password_field"],
                          ignore_params=config["ignore_params"])
             print('start crawling for' + config["name"] + ' ' + config["start_url"])
             process.start()
             print "-----------crawling finished------------"
             AvoidDuplicateEntry()
             print "-----------reformat finished------------"
             writeToLocal(output_file)




def writeToLocal(output_file):
    print "-----------total number of links------------"
    print len(output_urls)
    phase1_file = open(output_file, 'w')
    output = {"urls": output_urls}
    phase1_file.write(json.dumps(output))

def removeFromLocal(file):

    try:
        os.remove('tempitems.json')
        os.remove(file)
        pass
    except OSError:
        pass

def AvoidDuplicateEntry():
    print '_____________________'
    with open("tempitems.json") as my_file:
        urls = json.load(my_file)
        for item in urls:
            if 'logout' in item["url"]:
                continue
            if 'logout' in str(item["param"]):
                continue
            elif item not in output_urls:
                output_urls.append(item)
apptoRun=sys.argv[1:][0]
loopThroughAppInConfig(apptoRun)


