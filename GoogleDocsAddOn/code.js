let errors = [["he", "hej", 0, "beskrivelse"], ["heder", "hedder", 2, "beskrivelse"], ["lucas", "Lucas", 3, "beskrivelse"]]
//let errors = []
let service_url = "http://127.0.0.1:5000/";

async function fetchData() {
  var activeDoc = DocumentApp.getActiveDocument();
  var originalText = activeDoc.getBody().getText();
  let object = {"sentence": originalText};
  const response = await fetch(service_url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(object)
  });
  const data = await response.text();
  errors = JSON.parse(data.replace(/\\u([a-f0-9]{4})/gi, (match, group) => String.fromCharCode(parseInt(group, 16))));;
  return errors
}

function replaceWord(i){
  var activeDoc = DocumentApp.getActiveDocument();
  var text = activeDoc.getBody().getText();
  var words = text.split(" ");
  words[errors[i][2]] = errors[i][1];
  var newText = words.join(" ");
  activeDoc.getBody().setText(newText);
}

// Create a menu item
function onOpen(e) {
  DocumentApp.getUi().createAddonMenu()
      .addItem('Ret min tekst', 'showErrors')
      .addToUi();
}

// This function will be called when the script is run
async function showErrors() {
  errors = await fetchData();
  Logger.log(errors)
  // Check if there are any errors
  if (errors.length == 0) {
    // Show a message indicating that the text is error-free
    const no_error_message = "Det ser ud til, at din tekst er fejlfri 😊."
    var no_errors = HtmlService.createHtmlOutput("<p>" + no_error_message + "</p>");
    DocumentApp.getUi().showSidebar(no_errors);
  } else {
    var errorTemplate = HtmlService.createTemplateFromFile('errors');
    var errorOutput = errorTemplate.evaluate().setTitle('Errors');
    var errorContainer = errorOutput.getContent();
    // Show the errors in the sidebar
    var errorHtml = "<div>";
    for (var i = 0; i < errors.length; i++) {
      errorHtml +=  "<div class='error-message'>" + 
                      "<span class='close-button'>X</span>" + 
                      "<span class='wrongWord'>" + errors[i][0] + "</span>" + 
                      "<span class='arrow'>&#8594;</span>" + 
                      `<span class='correctWord' data-index='${i}'>` + errors[i][1] + "</span>" + 
                      "<span class='description'>" + errors[i][3] + "</span>" + 
                    "</div>";
  }
    errorHtml += "<script>$('.correctWord').click(function(){const index = $(this).data('index'); google.script.run.replaceWord(index)});</script>"
    errorHtml += "<script>$('.correctWord').click(function(){$(this).parent().remove();});</script>"
    errorHtml += "<script>$('.close-button').click(function(){$(this).parent().remove();});</script>"

    errorHtml += "</div>";
    errorContainer += errorHtml
    errorOutput.setContent(errorContainer);

    DocumentApp.getUi().showSidebar(errorOutput);
  }
}
