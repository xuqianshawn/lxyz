import scrapy
from scrapy.linkextractors import LinkExtractor
import urlparse
from project.items import ProjectItem
from scrapy.http import Request
from scrapy.spiders.init import InitSpider
import fill_form
from find_login_form import getFormData

class TestSpider(InitSpider): 
    name = "test"
    login_required = False

    link_extractor = {
        'next_page': LinkExtractor(allow=(), restrict_css=('a'))
    }

    login_item = None

    def __init__(self, *args, **crawler):
        super(TestSpider, self).__init__(*args, **crawler)

        self.start_urls = [crawler.get('start_url')]
        self.allowed_domains = [crawler.get('domain')]
        self.login_page = crawler.get('login_page')
        self.username = crawler.get('username')
        self.password = crawler.get('password')
        self.username_field = crawler.get('username_field')
        self.password_field = crawler.get('password_field')
        self.ignore_params = crawler.get('ignore_params')

    def init_request(self):
        print "----init-----"
        if self.username != "" and self.password != "":
            return Request(url=self.login_page, callback=self.login)
        return self.initialized()

    def login(self, response):
        form_data, action = getFormData(response.body, response.url, self.username_field, self.password_field, self.username, self.password)
        self.login_item = self.generateLoginItem(form_data, action)

        return scrapy.FormRequest(action,
                                  formdata=form_data,
                                  callback=self.checkLoginResponse)

    def checkLoginResponse(self, response):
        if "logout" in response.body.lower():
            self.log("Successful log in")

            self.login_required = True
            return self.initialized()
        else:
            self.log("Failed")


    def parse(self, response):
        if self.login_item:
            yield self.login_item

        post_forms = fill_form.fetchForm(response.url, response.body)
        for post_form in post_forms:
            ItemPost = self.generatePostItem(post_form)
            if ItemPost is not None:
                yield ItemPost


        yield self.generateTempitemForGet(response)

        # Find links to the next page
        for link in self.link_extractor['next_page'].extract_links(response):
            if "http" not in link.url:
                continue
            if "logout" in link.url or "delete" in link.url:
                yield self.generateTempitemForGetNoResp(link.url)
                continue
            if link.url.endswith(".jpg"):
                continue

            yield Request(url=link.url, meta={'ignore_params': self.ignore_params}, callback=self.parse)

    def generateTempitemForGet(self, response):
        parsed = urlparse.urlparse(response.url)
        parameters = urlparse.parse_qs(parsed.query)

        item = ProjectItem()
        url = parsed.geturl()
        if "?" in url:
            item['url'] = url[:url.find('?')]
        else:
            item['url'] = url

        item['param'] = parameters
        item['type'] = "GET"
        if self.login_required:
            item["loginrequired"] = "true"
            item["loginurl"] = self.login_url
        else:
            item["loginrequired"] = "false"
            item["loginurl"] = ""

        referer = None
        if "Referer" in response.request.headers.keys():
            referer = response.request.headers["Referer"]
        item["headers"] = {
            "referer": referer,
            "user-agent": response.request.headers["User-Agent"]
        }
        return item


    def generateTempitemForGetNoResp(self, response_url):
        parsed = urlparse.urlparse(response_url)
        parameters = urlparse.parse_qs(parsed.query)

        item = ProjectItem()
        url = parsed.geturl()
        if "?" in url:
            item['url'] = url[:url.find('?')]
        else:
            item['url'] = url

        item['param'] = parameters
        item['type'] = "GET"
        if self.login_required:
            item["loginrequired"] = "true"
            item["loginurl"] = self.login_url
        else:
            item["loginrequired"] = "false"
            item["loginurl"] = ""

        item["headers"] = {}
        return item
    def generateLoginItem(self, form_data, action):
        self.login_url = action
        ItemPost = ProjectItem()
        ItemPost["url"] = self.login_url

        output_form_data = {}
        for key in form_data.keys():
            output_form_data[key] = [form_data[key]]
        ItemPost["param"] = output_form_data

        ItemPost["type"] = "POST"
        ItemPost["loginrequired"] = "false"
        ItemPost["loginurl"] = ""
        return ItemPost

    def generatePostItem(self, post_form):
        ItemPost = ProjectItem()
        ItemPost["url"] = post_form["url"]
        ItemPost["param"] = post_form["fields"]
        ItemPost["type"] = "POST"
        if self.login_required:
            ItemPost["loginrequired"] = "true"
            ItemPost["loginurl"] = self.login_url
        else:
            ItemPost["loginrequired"] = "false"
            ItemPost["loginurl"] = ""

        if bool(ItemPost["param"]):
            return ItemPost
        return None


