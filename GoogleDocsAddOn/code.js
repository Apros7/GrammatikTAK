// named as code.gs in the google script editor

let errors = [["he", "hej", 0, "beskrivelse"], ["heder", "hedder", 2, "beskrivelse"], ["lucas", "Lucas", 3, "beskrivelse"]]
//let errors = []

// Create a menu item
function onOpen(e) {
  DocumentApp.getUi().createAddonMenu()
      .addItem('Ret min tekst', 'showErrors')
      .addToUi();
}

// This function will be called when the script is run
function showErrors() {
  // Get the text of the current document
  var text = DocumentApp.getActiveDocument().getBody().getText();
  
  // Show the text in the sidebar
  // var html = HtmlService.createHtmlOutput("<p>" + text + "</p>");
  // DocumentApp.getUi().showSidebar(html);
  
  // Check if there are any errors
  if (errors.length == 0) {
    // Show a message indicating that the text is error-free
    const no_error_message = "Det ser ud til, at din tekst er fejlfri 😊."
    var no_errors = HtmlService.createHtmlOutput("<p>" + no_error_message + "</p>");
    DocumentApp.getUi().showSidebar(no_errors);
  } else {
    // Show the errors in the sidebar
    var errorHtml = "<div>";
    for (var i = 0; i < errors.length; i++) {
      errorHtml +=  "<div class='error-message'>" + 
                      "<span class='close-button'>X</span>" + 
                      "<span class='wrongWord'>" + errors[i][0] + "</span>" + 
                      "<span class='arrow'>&#8594;</span>" + 
                      "<span class='correctWord'>" + errors[i][1] + "</span>" + 
                      "<span class='description'>" + errors[i][3] + "</span>" + 
                    "</div>";;
    }
    errorHtml += "</div>";
    var errorOutput = HtmlService.createHtmlOutput(errorHtml);
    DocumentApp.getUi().showSidebar(errorOutput);
  }
}
