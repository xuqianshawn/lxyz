from lxml import html
from urlparse import urljoin

 
def getFormData(response, origin_url, usernameField, passwordField, username, password):
    doc = html.document_fromstring(response)
    loginFormData = None 
    action = None
    for form in doc.xpath('//form'):
        IsUserNameMatchedWithField = False
        IsPasswordMatchedWithField = False
        form_data = {}
        for form_input in form.inputs:
            if form_input.name and form_input.type != "submit" and not form_input.checkable:
                form_data[form_input.name] = form_input.value
            if form_input.name == usernameField:
                IsUserNameMatchedWithField = True
            if form_input.name == passwordField:
                IsPasswordMatchedWithField = True

        if IsUserNameMatchedWithField and IsPasswordMatchedWithField:
            loginFormData = form_data
            action = urljoin(origin_url, form.action)

    loginFormData[usernameField] = username
    loginFormData[passwordField] = password

    return loginFormData, action
