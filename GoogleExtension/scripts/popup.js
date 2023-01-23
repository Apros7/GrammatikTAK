chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.text) {
      document.getElementById("selected-text").textContent = request.text;
    }
  });