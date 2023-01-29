let errors = [["he", "Hej", 0, "beskrivelse"], ["heder", "hedder", 2, "beskrivelse"], ["lucas", "Lucas.", 3, "beskrivelse"]]
//let errors = []
let service_url = "https://backend1-2f53ohkurq-ey.a.run.app";

async function fetchData() {
  var activeDoc = DocumentApp.getActiveDocument();
  var originalText = activeDoc.getBody().getText();
  var object = {"sentence": originalText};
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(object)
  };
  var response = UrlFetchApp.fetch(service_url, options);
  var data = response.getContentText();
  var errors = JSON.parse(data.replace(/\\u([a-f0-9]{4})/gi, (match, group) => String.fromCharCode(parseInt(group, 16))));
  return errors;
}

function replaceWord(i){
  var errors = JSON.parse(PropertiesService.getScriptProperties().getProperty('errors'));
  var activeDoc = DocumentApp.getActiveDocument();
  var text = activeDoc.getBody().getText();
  var words = text.split(" ");
  Logger.log(errors)
  words[errors[i][2]] = errors[i][1];
  var newText = words.join(" ");
  Logger.log(newText)
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

  // Get correct errors:
  errors = await fetchData();
  PropertiesService.getScriptProperties().setProperty('errors', JSON.stringify(errors));
  // Logger.log(errors)

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
