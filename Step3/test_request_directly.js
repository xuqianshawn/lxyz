var webPage = require('webpage');
var page = webPage.create();
var fs = require('fs');

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

// page.onLoadStarted = function () {
//   console.log("load started");
// };

// page.onLoadFinished = function () {
//   console.log("load finished");
// };


run = function (appName, username, password, loginurl) {

  var getUrls = [];
  // var loginurl = "";
  var step2Result = fs.read('../Step2/step2results/result_' + appName + ".json");
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
      getUrls.push(url);
    }
  }
  console.log(loginurl);
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

    setTimeout(function () {

      var count = 0;
      var interval = setInterval(function () {
        // console.log(getUrls[count]);
        page.open(getUrls[count], function (status) {
          // console.log("status: " + status);
          currentUrl = getUrls[count];
          setTimeout(function () {
            page.sendEvent('mousemove', 90, 90);
          }, 100);
        });
        count++;
        if (count >= getUrls.length) {
          console.log('end.');
          clearInterval(interval);
          phantom.exit();
        }
      }, 1000);

    }, 1000);

  });
}



var config = fs.read('config.json');
var configObject = JSON.parse(config);
var logins = configObject["logins"];
for (var i = 0; i < 1; i++) {
  var login = logins[i];
  var name = login["name"];
  var username = login["username"];
  var password = login["password"];
  var loginurl = login["loginurl"];
  console.log(name + ", " + username + ", " + password + ", " + loginurl);
  run(name, username, password, loginurl);
}