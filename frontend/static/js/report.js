async function loadReport() {
  const params    = new URLSearchParams(window.location.search);
  const sessionId = params.get('session_id');
  if (!sessionId) { window.location.href = '/'; return; }

  try {
    const res = await fetch(`/report/${sessionId}`);
    if (!res.ok) throw new Error('Report not available');
    renderReport(await res.json());
  } catch (err) {
    document.getElementById('report-content').innerHTML =
      `<div class="card"><p class="error">${err.message}. Please go back and try again.</p></div>`;
  }
}

function scoreClass(s) { return s >= 7 ? 'score-high' : s >= 4 ? 'score-mid' : 'score-low'; }
function recClass(r)   { return { hire: 'rec-hire', maybe: 'rec-maybe', reject: 'rec-reject' }[r] || ''; }

function renderReport(d) {
  const recLabel = { hire: '✅ Hire', maybe: '⚠️ Consider', reject: '❌ Reject' }[d.hire_recommendation]
                   || d.hire_recommendation;

  const qaHTML = d.answers.map(a => `
    <div class="qa-item">
      <div class="qa-question">
        <span class="q-num">Q${a.question_index}</span>
        <p>${a.question_text}</p>
      </div>
      <div class="qa-answer">
        <p><strong>Answer:</strong> ${a.answer_text || '<em>No answer recorded</em>'}</p>
        <div class="qa-meta">
          <span class="score-badge ${scoreClass(a.score)}">${a.score}/10</span>
          <span class="feedback">${a.feedback}</span>
        </div>
      </div>
    </div>
  `).join('');

  document.getElementById('report-content').innerHTML = `
    <div class="report-header card">
      <h2>Interview Report</h2>
      <p class="candidate-meta">${d.candidate_name} &mdash; ${d.role}</p>
      <div class="report-summary">
        <div class="summary-item">
          <div class="summary-label">Overall Score</div>
          <div class="summary-value ${scoreClass(d.overall_score)}">${d.overall_score}<span style="font-size:1rem;font-weight:400">/10</span></div>
        </div>
        <div class="summary-item">
          <div class="summary-label">Recommendation</div>
          <div class="summary-value ${recClass(d.hire_recommendation)}" style="font-size:1.2rem">${recLabel}</div>
        </div>
      </div>
      <div class="strengths-weaknesses">
        <div class="sw-item">
          <h4>💪 Strengths</h4>
          <p>${d.strengths}</p>
        </div>
        <div class="sw-item">
          <h4>📈 Areas to Improve</h4>
          <p>${d.weaknesses}</p>
        </div>
      </div>
    </div>
    <div class="qa-section card">
      <h3>Detailed Q&amp;A Review</h3>
      ${qaHTML}
    </div>
    <div class="actions">
      <a href="/" class="btn btn-primary">Start New Interview</a>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', loadReport);