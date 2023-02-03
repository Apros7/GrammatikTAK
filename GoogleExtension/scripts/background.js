chrome.runtime.onInstalled.addListener(function() {
  chrome.contextMenus.create({
      "title": 'Ret min tekst',
      "contexts": ["selection"],
      "id": "myContextMenuId"
  });
});

  
chrome.contextMenus.onClicked.addListener(function(info, tab) {
  chrome.tabs.executeScript({
    code: "window.getSelection().toString();"
  }, function(selectedText) {
    chrome.storage.local.set({word: selectedText[0]}, function () {console.log("Background: " + selectedText[0]);});
  });

  chrome.windows.create({url: "index.html"});
});


