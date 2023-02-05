let errors = [["he", "Hej", 0, "beskrivelse"], ["heder", "hedder", 2, "beskrivelse"], ["lucas", "Lucas.", 3, "beskrivelse"]]
//let errors = []
let service_url = "https://backend1-2f53ohkurq-ey.a.run.app";

async function fetchData() {
  var originalText = DocumentApp.getActiveDocument().getBody().getText();
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

function addNewLines(strings, newLinesIndex) {
  let result = [];
  for (let i = 0; i < strings.length; i++) {
    let newLines = '';
    if (newLinesIndex[i] !== undefined) {
      for (let j = 0; j < newLinesIndex[i]; j++) {
        newLines += '\n';
      }
    }
    result.push(strings[i] + newLines);
  }
  return result;
}

function addOneToMaxKey(obj) {
  let maxKey = Math.max(...Object.keys(obj).map(Number));
  let maxValue = obj[maxKey];
  delete obj[maxKey];
  obj[maxKey + 1] = maxValue;
  return obj;
}

function joinWords(words) {
  let result = "";
  for (let i = 0; i < words.length; i++) {
    let word = words[i];
    if (result[result.length - 1] !== "\n") {
      result += (i !== 0 ? " " : "") + word;
    } else {
      result += word;
    }
  }
  return result;
}

function splitNewLines(new_lines) {
  let words = [];
  let new_lines_index = {}
  let length_index = 0

  for (let i = 0; i < new_lines.length; i++) {
    length_index += new_lines[i].split(" ").length
    length_index -= 1
    if (new_lines_index[length_index] === undefined) {
      new_lines_index[length_index] = 1;
    } else {
      new_lines_index[length_index] += 1;
    }
    if (new_lines[i] !== "") {
      words.push(...new_lines[i].split(" "));
    }
  }

  return [words, new_lines_index]
}

function replaceWord(i){
  var errors = JSON.parse(PropertiesService.getScriptProperties().getProperty('errors'));
  var activeDoc = DocumentApp.getActiveDocument();
  var text = activeDoc.getBody().getText();

  let new_lines = text.split("\n");
  let [words, new_lines_index] = splitNewLines(new_lines);
  Logger.log(words);

  new_lines_index = addOneToMaxKey(new_lines_index)
  words.filter(string => string !== '');
  words[errors[i][2]] = errors[i][1];
  const new_text = joinWords(addNewLines(words, new_lines_index));
  Logger.log(new_text);
  activeDoc.getBody().setText(new_text);
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
