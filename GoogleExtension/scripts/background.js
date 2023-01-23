chrome.runtime.onInstalled.addListener(function() {
  chrome.contextMenus.create({
      "title": 'Ret min tekst',
      "contexts": ["selection"],
      "id": "myContextMenuId"
  });
});

  
chrome.contextMenus.onClicked.addListener(function(info, tab) {
  let word = info.selectionText
  console.log(info.selectionText);
  chrome.storage.local.set({word: word}, function () {console.log("Value is set to " + word);});
  chrome.windows.create({url: "index.html"});
});


