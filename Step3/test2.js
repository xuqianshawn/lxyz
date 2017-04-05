var webPage = require('webpage');
var page = webPage.create();
var fs = require('fs');
page.settings.XSSAuditingEnabled = false;
page.settings.webSecurityEnabled = false;

// page.onLoadStarted = function () {
//   console.log("load started");
// };

// page.onLoadFinished = function () {
//   console.log("load finished");
// };

page.onAlert = function (msg) {
  console.log('ALERT: ' + msg);
  if (msg === 'cs5331_g7') {
    console.log('attack succeed.==============================');
  }
};

var step2Result = fs.read('./step3results/step3.json');
var resultObject = JSON.parse(step2Result);
var result = resultObject['result'];

var fileNames = [];
for (var a in result) {
  var object = result[a];
  for (var b in object) {
    fileNames.push(object[b][0]);
    // console.log(object[b][0]);
    // page.open('./step3results/' + object[b][0], function () {
    //   setTimeout(function () {
    //     page.sendEvent('mousemove', 90, 90);
    //     // phantom.exit();
    //   }, 500);
    // });
  }
}

console.log("test");
console.log(fileNames.length);
var count = 0;
var interval = setInterval(function () {
  console.log(fileNames[count]);
  page.open('./step3results/' + fileNames[count], function () {
    setTimeout(function () {
      page.sendEvent('mousemove', 90, 90);
    }, 500);
  });
  count++;
  if(count >= fileNames.length){
    clearInterval(interval);
  }
}, 700);