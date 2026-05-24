/* ── State ──────────────────────────────────────────────────── */
let sessionId         = null;
let totalQuestions    = 5;
let currentQIndex     = 0;
let mediaRecorder     = null;
let audioChunks       = [];
let isRecording       = false;
let currentTranscript = null;

/* ── Speech synthesis ───────────────────────────────────────── */
function speakText(text) {
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.rate = 0.92;
  utt.pitch = 1.0;
  window.speechSynthesis.speak(utt);
}

/* ── Initialise ─────────────────────────────────────────────── */
async function init() {
  const params = new URLSearchParams(window.location.search);
  sessionId = params.get('session_id');
  if (!sessionId) { window.location.href = '/'; return; }

  try {
    const res  = await fetch(`/session/${sessionId}`);
    const data = await res.json();
    if (data.total_questions) totalQuestions = data.total_questions;
  } catch (_) {}

  await fetchNextQuestion(null);
}

/* ── Agent call ─────────────────────────────────────────────── */
async function fetchNextQuestion(answerText) {
  showState('loading');

  const body = {
    session_id:     sessionId,
    answer_text:    answerText ?? null,
    question_index: answerText ? currentQIndex : null,
  };

  try {
    const res  = await fetch('/agent/respond', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();

    if (data.is_complete) {
      showState('complete');
      setTimeout(() => { window.location.href = `/report-page?session_id=${sessionId}`; }, 2800);
      return;
    }

    currentQIndex = data.question_index;
    updateProgress(currentQIndex);
    displayQuestion(data.question_text, currentQIndex);
    speakText(data.question_text);
    showState('question');
  } catch (err) {
    alert('Connection error. Please refresh the page.\n\n' + err.message);
  }
}

/* ── UI helpers ─────────────────────────────────────────────── */
function displayQuestion(text, idx) {
  document.getElementById('q-num').textContent = idx;
  document.getElementById('question-text').textContent = text;
  document.getElementById('transcript-preview').classList.add('hidden');
  document.getElementById('submit-area').classList.add('hidden');
  resetMicUI();
  currentTranscript = null;
}

function updateProgress(current) {
  document.getElementById('question-counter').textContent =
    `Question ${current} of ${totalQuestions}`;
  const pct = ((current - 1) / totalQuestions) * 100;
  document.getElementById('progress-fill').style.width = `${pct}%`;
}

function showState(name) {
  ['loading', 'question', 'evaluating', 'complete'].forEach(s => {
    document.getElementById(`${s}-state`).classList.add('hidden');
  });
  document.getElementById(`${name}-state`).classList.remove('hidden');
}

/* ── Recording ──────────────────────────────────────────────── */
async function toggleRecording() {
  isRecording ? stopRecording() : await startRecording();
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      await processAudio();
    };
    mediaRecorder.start();
    isRecording = true;

    const btn = document.getElementById('record-btn');
    btn.textContent = '⏹ Stop Recording';
    btn.classList.add('recording');
    document.getElementById('mic-label').textContent = 'Recording… click to stop';
    document.getElementById('mic-status').className = 'mic-status recording';
  } catch (_) {
    alert('Microphone permission denied. Please allow access and try again.');
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    isRecording = false;
    mediaRecorder.stop();
    const btn = document.getElementById('record-btn');
    btn.textContent = 'Processing…';
    btn.disabled = true;
    document.getElementById('mic-label').textContent = 'Processing audio…';
  }
}

async function processAudio() {
  const blob     = new Blob(audioChunks, { type: 'audio/webm' });
  const formData = new FormData();
  formData.append('audio', blob, 'recording.webm');

  try {
    const res  = await fetch('/audio-to-text', { method: 'POST', body: formData });
    if (!res.ok) throw new Error();
    const data = await res.json();

    currentTranscript = data.transcript;
    document.getElementById('transcript-text').textContent = currentTranscript;
    document.getElementById('transcript-preview').classList.remove('hidden');
    document.getElementById('submit-area').classList.remove('hidden');
  } catch (_) {
    alert('Transcription failed. Please try recording again.');
  } finally {
    resetMicUI();
  }
}

function resetMicUI() {
  isRecording = false;
  const btn = document.getElementById('record-btn');
  btn.textContent = '🎤 Start Recording';
  btn.classList.remove('recording');
  btn.disabled = false;
  document.getElementById('mic-label').textContent = 'Press to speak your answer';
  document.getElementById('mic-status').className = 'mic-status idle';
}

function clearAnswer() {
  currentTranscript = null;
  document.getElementById('transcript-preview').classList.add('hidden');
  document.getElementById('submit-area').classList.add('hidden');
  resetMicUI();
}

async function submitAnswer() {
  if (!currentTranscript) return;
  const answer = currentTranscript;
  currentTranscript = null;
  showState('evaluating');
  await fetchNextQuestion(answer);
}

document.addEventListener('DOMContentLoaded', init);