

let service_url = "http://127.0.0.1:5000/";
// let service_url = "https://backend1-2f53ohkurq-ey.a.run.app";
//let errors = [["he", "hej", 0, "beskrivelse"], ["heder", "hedder", 2, "beskrivelse"], ["lucas", "Lucas", 3, "beskrivelse"]]


let errors = []
let originalText = "dette er din tekst"

async function get_text() {
  var text = await chrome.storage.local.get(["word"]).then((result) => {
    originalText = result.word;
  });
}

const copyButton = document.querySelector(".copy-button");

copyButton.addEventListener("click", () => {
  navigator.clipboard.writeText(document.querySelector(".text").innerText).then(() => {
    copyButton.innerText = "Kopieret";
    setTimeout(() => {
      copyButton.innerText = "Kopier tekst";
    }, 2000);
  }, (err) => {
    console.log('Failed to copy text: ', err);
  });
});

async function fetchData() {
  await get_text();
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
}

async function main() {


  await fetchData();
  console.log("Fetch is complete!");

  let corrected_errors = []

const words = originalText.split(" ");
const newLineIndices = [];
for (let i = 0; i < words.length - 1; i++) {
  if (words[i] === "" && words[i + 1] === "") {
    newLineIndices.push(i);
    words.splice(i, 2);
    i--;
  }
}

for (let i = 0; i < errors.length; i++) {
    const error = errors[i];
    const index = error[2];
    words[index] = `<span style="color: red">${words[index]}</span>`;
  }


console.log(newLineIndices)
function add_new_lines(words) {
  words_with_new_lines = words
  for (let i = newLineIndices.length - 1; i >= 0; i--) {
    const index = newLineIndices[i];
    words_with_new_lines.splice(index, 0, "<br>");
  }
  return words_with_new_lines.join(" ");
}

console.log(words)
const newSentence = add_new_lines(words);
const currentText = document.querySelector(".text")
currentText.innerHTML = newSentence

const rightColumn = document.querySelector(".right-column")

function checkClearMessage() {
    if (rightColumn.childElementCount === 0) {
        allClearText = document.createElement("div")
        allClearText.classList.add("allClearText")
        allClearText.textContent = "Det ser ud til, at din tekst er fejlfri 😊."
        rightColumn.appendChild(allClearText)
      }
}

if (errors.length === 0) {
    allClearText = document.createElement("div")
    allClearText.classList.add("allClearText")
    allClearText.textContent = "Det ser ud til, at din tekst er fejlfri 😊."
    rightColumn.appendChild(allClearText)
}

for (let i = 0; i < errors.length; i++) {
    const error = errors[i];
    
    const errorMessage = document.createElement("div");
    errorMessage.classList.add("error-message");

    const closeButton = document.createElement("div");
    closeButton.classList.add("close-button");
    closeButton.textContent = "X";
    errorMessage.append(closeButton)

    closeButton.addEventListener("click", function() {
        const index = errors[i][2];
        const words = currentText.textContent.split(" ");
        corrected_errors.push(i)
        for (let j = 0; j < errors.length; j++) {
            if (j !== i && !corrected_errors.includes(j)) {
              const errorIndex = errors[j][2];
              words[errorIndex] = `<span style="color: red">${words[errorIndex]}</span>`;
            }
          }
        const newSentence = add_new_lines(words);
        currentText.innerHTML = newSentence;
        errorMessage.remove();
        checkClearMessage();
      });

    const wrongWord = document.createElement("div");
    wrongWord.classList.add("wrongWord")
    wrongWord.textContent = error[0]
    errorMessage.append(wrongWord)

    const arrow = document.createElement("div");
    arrow.classList.add("arrow")
    arrow.innerHTML = "&#8594;"
    errorMessage.append(arrow)

    const correctWord = document.createElement("div");
    correctWord.classList.add("correctWord")
    correctWord.textContent = error[1]
    errorMessage.append(correctWord)

    correctWord.addEventListener("click", function() {
        const index = errors[i][2];
        const words = currentText.textContent.split(" ").filter(str => str !== "");
        words[index] = errors[i][1];
        console.log(words)
        corrected_errors.push(i)
        for (let j = 0; j < errors.length; j++) {
            if (j !== i && !corrected_errors.includes(j)) {
              const errorIndex = errors[j][2];
              words[errorIndex] = `<span style="color: red">${words[errorIndex]}</span>`;
            }
          }
        const newSentence = add_new_lines(words);
        console.log(newSentence)
        currentText.innerHTML = newSentence;
        errorMessage.remove();
        checkClearMessage();
      });

    const errorElement = document.createElement("div");
    errorElement.classList.add("description");
    errorElement.textContent = error[3]
    errorMessage.append(errorElement)

    rightColumn.appendChild(errorMessage)
}

}

main();

