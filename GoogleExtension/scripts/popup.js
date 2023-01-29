chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.text) {
      document.getElementById("selected-text").textContent = request.text;
    }
  });

let word = "Stavefejl og andre grammatiske fejl kan påvirke din troværdighed. \
GrammatikTAK hjælper dig med at finde din stavefejl, og andre grammatiske fejl .\
Vi retter også egenavne som københavn og erik. \
Så er du sikker på at din tekst er grammatisk korrekt og at du dermed giver den bedste indtryk på din læser."
  
document.getElementById("showDemo").addEventListener("click", function(event) {
  chrome.storage.local.set({word: word}, function () {console.log("Value is set to " + word);});
  chrome.windows.create({url: "index.html"});
});

document.getElementById("linkToDocs").addEventListener("click", function(event) {

  // window.open()
});