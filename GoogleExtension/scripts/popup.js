chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.text) {
      document.getElementById("selected-text").textContent = request.text;
    }
  });
  
function open_example() {
  console.log("this shit just god damn worked hell yeah boi")
}