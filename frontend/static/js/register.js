async function startInterview() {
  const fields = ['name', 'role', 'qualification', 'experience', 'skills'];
  const values = Object.fromEntries(fields.map(f => [f, document.getElementById(f).value.trim()]));

  if (Object.values(values).some(v => !v)) {
    showError('Please fill in all fields.');
    return;
  }

  const btn = document.getElementById('start-btn');
  btn.disabled = true;
  btn.textContent = 'Creating session...';
  hideError();

  try {
    const res = await fetch('/session/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(values),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    window.location.href = `/interview?session_id=${data.session_id}`;
  } catch (err) {
    showError('Failed to start interview. Check your connection and try again.');
    btn.disabled = false;
    btn.textContent = 'Start Interview →';
  }
}

function showError(msg) {
  const el = document.getElementById('error-msg');
  el.textContent = msg;
  el.classList.remove('hidden');
}
function hideError() {
  document.getElementById('error-msg').classList.add('hidden');
}