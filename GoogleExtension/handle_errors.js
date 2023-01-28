//let service_url = "https://backend1-2f53ohkurq-ey.a.run.app";
//let errors = [["he", "hej", 0, "beskrivelse"], ["heder", "hedder", 2, "beskrivelse"], ["lucas", "Lucas", 3, "beskrivelse"]]


let errors = []
let originalText = "dette er din tekst"

async function get_text() {
  var text = await chrome.storage.local.get(["word"]).then((result) => {
    console.log("Value currently is " + result.word);
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

let service_url = "http://127.0.0.1:5000/";

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

for (let i = 0; i < errors.length; i++) {
    const error = errors[i];
    const index = error[2];
    words[index] = `<span style="color: red">${words[index]}</span>`;
  }

const newSentence = words.join(" ");

const currentText = document.querySelector(".text")
currentText.innerHTML = newSentence

const rightColumn = document.querySelector(".right-column")

function checkClearMessage() {
    if (rightColumn.childElementCount === 0 || errors.length === 0) {
        allClearText = document.createElement("div")
        allClearText.classList.add("allClearText")
        allClearText.textContent = "Det ser ud til, at din tekst er fejlfri 😊."
        rightColumn.appendChild(allClearText)
      }
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
        words[index] = errors[i][0]
        corrected_errors.push(i)
        for (let j = 0; j < errors.length; j++) {
            if (j !== i && !corrected_errors.includes(j)) {
              const errorIndex = errors[j][2];
              words[errorIndex] = `<span style="color: red">${words[errorIndex]}</span>`;
            }
          }
        const newSentence = words.join(" ");
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
        const words = currentText.textContent.split(" ");
        words[index] = errors[i][1];
        corrected_errors.push(i)
        for (let j = 0; j < errors.length; j++) {
            if (j !== i && !corrected_errors.includes(j)) {
              const errorIndex = errors[j][2];
              words[errorIndex] = `<span style="color: red">${words[errorIndex]}</span>`;
            }
          }
        const newSentence = words.join(" ");
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

