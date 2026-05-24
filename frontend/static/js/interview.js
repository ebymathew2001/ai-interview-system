/* ── State ───────────────────────────────────────────────────── */
let sessionId         = null;
let totalQuestions    = 5;
let currentQIndex     = 0;
let mediaRecorder     = null;
let audioChunks       = [];
let isRecording       = false;
let currentTranscript = null;
let currentAudioB64   = null;   // stores latest question audio for replay

/* ── Init ────────────────────────────────────────────────────── */
async function init() {
  const params = new URLSearchParams(window.location.search);
  sessionId = params.get('session_id');
  if (!sessionId) { window.location.href = '/'; return; }

  // Load candidate details into left panel
  try {
    const res  = await fetch(`/session/${sessionId}`);
    const data = await res.json();
    document.getElementById('candidate-name').textContent          = data.name;
    document.getElementById('candidate-role').textContent          = data.role;
    document.getElementById('candidate-qualification').textContent = data.qualification;
    document.getElementById('candidate-experience').textContent    = data.experience;
    document.getElementById('candidate-skills').textContent        = data.skills;
    totalQuestions = data.total_questions;  // ← reads from DB
  } catch (_) {}

  // Start interview — first agent call
  await fetchNextQuestion(null);
}

/* ── Agent call ──────────────────────────────────────────────── */
async function fetchNextQuestion(answerText) {
  // Show typing indicator while waiting
  showTyping();

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

    removeTyping();

    if (data.is_complete) {
      addSystemMessage('✅ Interview complete! Redirecting to your report...');
      setTimeout(() => {
        window.location.href = `/report-page?session_id=${sessionId}`;
      }, 2500);
      return;
    }

    currentQIndex = data.question_index;
    updateProgress(currentQIndex);

    // Convert question text to audio via backend TTS
    const audioB64 = await getAudio(data.question_text);
    currentAudioB64 = audioB64;

    // Add AI bubble with question text + replay button
    addAIBubble(data.question_text, audioB64, currentQIndex);

    // Play audio automatically
    if (audioB64) playAudio(audioB64);

  } catch (err) {
    removeTyping();
    addSystemMessage('⚠️ Connection error. Please refresh.');
    console.error(err);
  }
}

/* ── TTS ─────────────────────────────────────────────────────── */
async function getAudio(text) {
  try {
    const res  = await fetch('/text-to-audio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    return data.audio_base64 || null;
  } catch (_) {
    return null;
  }
}

function playAudio(base64String) {
  if (!base64String) return;
  const audio = new Audio(`data:audio/mp3;base64,${base64String}`);
  audio.play();
}

/* ── Chat bubble rendering ───────────────────────────────────── */
function addAIBubble(text, audioB64, qIndex) {
  const window_ = document.getElementById('chat-window');

  // Remove welcome message if present
  const welcome = window_.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  const row = document.createElement('div');
  row.className = 'bubble-row ai';

  const replayId = `audio-${qIndex}`;

  row.innerHTML = `
    <div class="bubble-icon">🤖</div>
    <div>
      <div class="bubble">${text}</div>
      <div class="bubble-meta">
        <span class="bubble-label">Question ${qIndex}</span>
        ${audioB64 ? `<button class="replay-btn" onclick="playAudio('${audioB64}')">🔊 Replay</button>` : ''}
      </div>
    </div>
  `;

  window_.appendChild(row);
  scrollToBottom();
}
function addCandidateBubble(text) {
  const window_ = document.getElementById('chat-window');

  const row = document.createElement('div');
  row.className = 'bubble-row candidate';
  row.innerHTML = `
    <div class="bubble-icon">👤</div>
    <div style="display:flex; flex-direction:column; align-items:flex-end;">
      <div class="bubble">${text}</div>
      <div class="bubble-meta">
        <span class="bubble-label">You</span>
      </div>
    </div>
  `;

  window_.appendChild(row);
  scrollToBottom();
}

function addSystemMessage(text) {
  const window_ = document.getElementById('chat-window');
  const p = document.createElement('p');
  p.style.cssText = 'text-align:center;color:#94a3b8;font-size:0.85rem;margin:0.5rem 0';
  p.textContent = text;
  window_.appendChild(p);
  scrollToBottom();
}

function showTyping() {
  const window_ = document.getElementById('chat-window');
  const row = document.createElement('div');
  row.className = 'bubble-row ai typing-bubble';
  row.id = 'typing-indicator';
  row.innerHTML = `
    <div class="bubble-icon">🤖</div>
    <div class="bubble">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;
  window_.appendChild(row);
  scrollToBottom();
}

function removeTyping() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

function scrollToBottom() {
  const w = document.getElementById('chat-window');
  w.scrollTop = w.scrollHeight;
}

/* ── Progress ────────────────────────────────────────────────── */
function updateProgress(current) {
  document.getElementById('question-counter').textContent =
    `${current} / ${totalQuestions}`;
  const pct = ((current - 1) / totalQuestions) * 100;
  document.getElementById('progress-fill').style.width = `${pct}%`;
}

/* ── Recording ───────────────────────────────────────────────── */
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

    document.getElementById('mic-btn').classList.add('recording');
    document.getElementById('mic-label').textContent = 'Recording… click to stop';
    document.getElementById('recording-indicator').classList.remove('hidden');
  } catch (_) {
    alert('Microphone permission denied. Please allow access.');
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    isRecording = false;
    mediaRecorder.stop();
    document.getElementById('mic-btn').classList.remove('recording');
    document.getElementById('mic-label').textContent = 'Processing audio...';
    document.getElementById('recording-indicator').classList.add('hidden');
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

    // Show transcript preview at bottom
    document.getElementById('transcript-text').textContent = currentTranscript;
    document.getElementById('transcript-box').classList.remove('hidden');
    document.getElementById('send-btn').classList.remove('hidden');
    document.getElementById('mic-label').textContent = 'Press mic to record your answer';
  } catch (_) {
    alert('Transcription failed. Please try again.');
    document.getElementById('mic-label').textContent = 'Press mic to record your answer';
  }
}

function clearRecording() {
  currentTranscript = null;
  document.getElementById('transcript-box').classList.add('hidden');
  document.getElementById('send-btn').classList.add('hidden');
  document.getElementById('mic-label').textContent = 'Press mic to record your answer';
}

/* ── Submit answer ───────────────────────────────────────────── */
async function submitAnswer() {
  if (!currentTranscript) return;

  const answer = currentTranscript;

  // Add candidate bubble to chat
  addCandidateBubble(answer);

  // Clear input area
  clearRecording();

  // Fetch next question
  await fetchNextQuestion(answer);
}

document.addEventListener('DOMContentLoaded', init);