var webPage = require('webpage');
var page = webPage.create();

page.onAlert = function (msg) {
  console.log('ALERT: ' + msg);
};

page.open('tmp04.html', function(){

});