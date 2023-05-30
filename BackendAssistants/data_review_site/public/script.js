const feedbackContainer = document.getElementById('feedback-container');
const popupOverlay = document.getElementById('popup-overlay');
const popupText = document.getElementById('popup-text');
const closeButton = document.getElementById('close-button');

function fetchFeedback() {
  fetch('/feedback')
    .then(response => response.json())
    .then(feedbackData => loadFeedback(feedbackData))
    .catch(error => console.error('Error fetching feedback:', error));
}

function loadFeedback(feedbackData) {
  feedbackContainer.innerHTML = '';

  feedbackData.forEach((item, index) => {
    const square = document.createElement('div');
    square.classList.add('square', item.state);

    
    square.innerText = item.feedback;
    square.addEventListener('click', () => openPopup(item.text));

    const resolveButton = document.createElement('button');
    resolveButton.innerText = 'Resolve';
    resolveButton.addEventListener('click', () => resolveFeedback(square, index));

    square.appendChild(resolveButton);
    feedbackContainer.appendChild(square);
  });
}

function openPopup(text) {
  popupText.innerText = text;
  popupOverlay.style.display = 'block';
}

closeButton.addEventListener('click', () => {
    popupOverlay.style.display = 'none';
    popupText.innerText = '';
});

function resolveFeedback(square, index) {
fetch('/resolve-feedback', {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json',
    },
    body: JSON.stringify({ index }),
})
    .then(response => {
    if (response.ok) {
        square.classList.add('resolved');
    } else {
        console.error('Error resolving feedback');
    }
    })
    .catch(error => console.error('Error resolving feedback:', error));
}
  
fetchFeedback();
