var webPage = require('webpage');
var page = webPage.create();
var fs = require('fs');
var system = require('system');

var currentUrl = "";

page.settings.XSSAuditingEnabled = false;
page.settings.webSecurityEnabled = false;

page.onConsoleMessage = function (msg) {
  console.log(msg);
};
page.onAlert = function (msg) {

  console.log('ALERT: ' + msg + ", url: " + currentUrl);
  // phantom.exit();
};

page.onError = function () {
  // do nothing?
}

// page.onLoadStarted = function () {
//   console.log("load started");
// };

// page.onLoadFinished = function () {
//   console.log("load finished");
// };
var getUrls = [];
var args = system.args;
var config = fs.read('config.json');
var configObject = JSON.parse(config);
var logins = configObject["logins"];
if (args.length <= 1) {
  console.log('plesae provide app name');
  phantom.exit();
}
var app = args[1];
for (var i = 0; i < logins.length; i++) {
  var login = logins[i];
  var name = login["name"];
  if (name === app) {
    var username = login["username"];
    var password = login["password"];
    var loginurl = login["loginurl"];
    console.log(name + ", " + username + ", " + password + ", " + loginurl);
    run(name, username, password, loginurl);
  }
}

function run(appName, username, password, loginurl) {
  // var loginurl = "";
  var step2Result = fs.read('../Step2/results/result_' + appName + ".json");
  var resultObject = JSON.parse(step2Result);
  for (var i = 0; i < resultObject.length; i++) {
    var object = resultObject[i];
    var url = object['url'];
    var type = object['type'];
    var loginrequired = object['loginrequired'];
    var param = object['param'];

    if (loginrequired && loginurl && type === 'GET') {
      if (param) {
        url = url + "?";
        for (var p in param) {
          if (p == 'logout') {
            // some param is logout
            continue;
          }
          url = url + p + "=" + param[p] + "&";
        }
      }
      getUrls.push({
        url: url,
        type: type
      });
    } else if (loginrequired && loginurl && type === 'POST') {

      getUrls.push({
        url: url,
        type: type,
        data: param
      });
    }
    else{
      getUrls.push({
        url: url,
        type: type
      });
    }
  }
  console.log(loginurl);
  if (loginurl) {
    ll(loginurl, function () {
      attack();
    });
  }
  else {
    attack();
  }
}

function ll(loginurl, callback) {
  page.open(loginurl, function (status) {
    console.log("status: " + status);
    // login
    page.evaluate(function (username, password) {
      var arr = document.getElementsByTagName("form");
      var i;
      for (i = 0; i < arr.length; i++) {
        if (arr[i].getAttribute('method') == "post") {
          console.log('enter credentials');
          arr[i].elements["login"].value = username;
          arr[i].elements["password"].value = password;
          return;
        }
      }
    }, username, password);

    page.evaluate(function () {

      var arr = document.getElementsByTagName("form");
      var i;

      for (i = 0; i < arr.length; i++) {
        if (arr[i].getAttribute('method') == "post") {
          console.log('login');
          arr[i].submit();
          return;
        }
      }
    });

    callback();

  });
}

function attack() {
  setTimeout(function () {

    var count = 0;
    var interval = setInterval(function () {
      var urlInfo = getUrls[count];
      currentUrl = urlInfo.url;
      if (urlInfo.type === "POST") {
        page.open(urlInfo.url, 'post', urlInfo.data, function (status) {
          setTimeout(function () {
            page.sendEvent('mousemove', 90, 90);
          }, 100);
        });
      } else if (urlInfo.type === "GET") {
        page.open(urlInfo.url, function (status) {
          setTimeout(function () {
            page.sendEvent('mousemove', 90, 90);
          }, 100);
        });
      }

      count++;
      if (count >= getUrls.length) {
        console.log('end.');
        clearInterval(interval);
        phantom.exit();
      }
    }, 1000);

  }, 1000);
}