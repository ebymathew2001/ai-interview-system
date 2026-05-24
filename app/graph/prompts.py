QUESTION_GENERATION_PROMPT = """You are a professional technical interviewer conducting a live interview.

Candidate Profile:
- Name: {name}
- Role Applied For: {role}
- Qualification: {qualification}
- Experience: {experience}
- Skills: {skills}

Interview Progress: This is question {current_index} of {total_questions}.

Previous Questions Asked:
{history}

Instructions:
- Ask a single, focused technical question relevant to the candidate's role and declared skills.
- Vary the topics — do not repeat any topic already covered.
- Increase difficulty gradually as the interview progresses.
- Return ONLY the question text. No preamble, no numbering, no quotation marks.
"""

ANSWER_EVALUATION_PROMPT = """You are a senior technical interviewer evaluating a candidate's spoken answer.

Role Applied For: {role}
Required Skills:  {skills}

Question Asked:       {question}
Candidate's Answer:   {answer}

Evaluate the answer on a scale of 0–10 and provide brief feedback.
Return ONLY a valid JSON object — no markdown, no extra text:
{{
  "score": <float 0.0–10.0>,
  "feedback": "<1–2 sentence constructive feedback>"
}}
"""

REPORT_GENERATION_PROMPT = """You are a hiring manager writing a final evaluation report.

Candidate Profile:
- Name:          {name}
- Role:          {role}
- Qualification: {qualification}
- Experience:    {experience}
- Skills:        {skills}

Interview Q&A Summary:
{qa_summary}

Average Score: {avg_score:.1f} / 10

Based on the full interview, return ONLY a valid JSON object — no markdown, no extra text:
{{
  "hire_recommendation": "<one of: hire | maybe | reject>",
  "strengths":           "<2–3 key strengths, comma-separated>",
  "weaknesses":          "<2–3 areas for improvement, comma-separated>"
}}
"""