const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3001;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Change path?
const feedbackDataPath = './datastore/Feedback.json';

function loadFeedback() {
  const feedbackData = fs.readFileSync(feedbackDataPath, 'utf8');
  return JSON.parse(feedbackData);
}

function saveFeedback(feedback) {
  const jsonContent = JSON.stringify(feedback, null, 4);
  fs.writeFileSync(feedbackDataPath, jsonContent, 'utf8');
}

app.post('/resolve-feedback', (req, res) => {
  const { index } = req.body;
  const feedback = loadFeedback();

  if (index >= 0 && index < feedback.length) {
    feedback[index].state = 'resolved';
    saveFeedback(feedback);
    res.sendStatus(200);
  } else {
    res.sendStatus(400);
  }
});

app.get('/feedback', (req, res) => {
  const feedback = loadFeedback();
  res.json(feedback);
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
