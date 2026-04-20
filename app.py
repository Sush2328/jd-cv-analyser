import streamlit as st
import anthropic

st.set_page_config(page_title="JD to CV Gap Analyser", layout="wide", page_icon="🎯")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=Instrument+Serif:ital@0;1&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .hero { background: #0e0e0d; padding: 48px 40px; border-radius: 4px; margin-bottom: 32px; }
  .hero h1 { font-family: 'Instrument Serif', serif; font-size: 2.4rem; color: #f7f4ee; letter-spacing: -1px; margin-bottom: 8px; }
  .hero p { color: rgba(247,244,238,0.55); font-size: 15px; font-weight: 300; margin-bottom: 4px; }
  .hero .origin { color: rgba(247,244,238,0.35); font-size: 13px; font-style: italic; }
  .score-banner { padding: 28px 32px; border-radius: 4px; margin-bottom: 24px; }
  .score-high { background: #e8f5f2; border-left: 4px solid #2d7d6f; }
  .score-mid { background: #fff3cd; border-left: 4px solid #f59e0b; }
  .score-low { background: #fee2e2; border-left: 4px solid #c13b20; }
  .score-n { font-family: 'Instrument Serif', serif; font-size: 4rem; letter-spacing: -2px; line-height: 1; }
  .score-high .score-n { color: #2d7d6f; }
  .score-mid .score-n { color: #b45309; }
  .score-low .score-n { color: #c13b20; }
  .score-label { font-size: 14px; color: #3a3a38; margin-top: 8px; }
  .result-section { background: #f7f4ee; border-left: 3px solid #c13b20; padding: 28px 32px; border-radius: 0 4px 4px 0; margin: 16px 0; line-height: 1.8; }
  .verdict-pass { background: #e8f5f2; border-left: 3px solid #2d7d6f; padding: 16px 20px; border-radius: 0 4px 4px 0; font-size: 15px; font-weight: 500; color: #1a3d36; }
  .verdict-fail { background: #fee2e2; border-left: 3px solid #c13b20; padding: 16px 20px; border-radius: 0 4px 4px 0; font-size: 15px; font-weight: 500; color: #5a1a1a; }
  .footer-line { font-size: 14px; font-style: italic; color: #3a3a38; text-align: center; padding: 16px; border-top: 1px solid rgba(14,14,13,0.1); margin-top: 32px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>JD to CV Gap Analyser</h1>
  <p>Paste a job description and your CV. Get a gap analysis, rewrite suggestions, and a tailored cover note in seconds.</p>
  <p class="origin">Built because I needed this tool in my own job search and it did not exist.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Job Description")
    jd = st.text_area(
        "Paste the full job description here",
        height=320,
        placeholder="Paste the job description you are applying for...",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("#### Your CV")
    cv = st.text_area(
        "Paste your CV or relevant experience here",
        height=320,
        placeholder="Paste your CV, LinkedIn summary, or work experience here...",
        label_visibility="collapsed"
    )

st.markdown("#### Optional context")
col1, col2 = st.columns(2)
with col1:
    role_level = st.selectbox("Role level you are targeting", [
        "Individual contributor",
        "Senior / Lead",
        "Manager",
        "Director / Head of",
        "VP / C-Suite"
    ])
with col2:
    tone = st.selectbox("Cover note tone", [
        "Confident and direct",
        "Warm and collaborative",
        "Strategic and analytical",
        "Concise and punchy"
    ])

extra_context = st.text_input(
    "Anything else the analyser should know?",
    placeholder="e.g. I am switching industries, I have a gap year, this role is a step up..."
)

if st.button("Analyse My Fit", type="primary"):
    if not jd.strip():
        st.warning("Please paste a job description.")
        st.stop()
    if not cv.strip():
        st.warning("Please paste your CV.")
        st.stop()

    with st.spinner("Analysing your fit..."):

        prompt = f"""You are a brutally honest but constructive senior recruiter and career advisor. You have reviewed thousands of CVs and you know exactly what gets candidates screened in and screened out.

Job Description:
{jd}

Candidate CV:
{cv}

Role level: {role_level}
Cover note tone requested: {tone}
{f'Additional context: {extra_context}' if extra_context else ''}

Provide your analysis in exactly this structure:

## Fit Score: [X/100]
One sentence explaining the score. Be direct.

## Screening Verdict
Either "LIKELY TO BE SCREENED IN" or "LIKELY TO BE SCREENED OUT" with a one-sentence rationale.

## What Is Working In Your Favour
3 to 4 specific strengths from the CV that match this JD well. Be concrete, not generic.

## Critical Gaps
3 to 5 specific gaps between the JD requirements and the CV. For each gap:
- What the JD requires
- What is missing or weak in the CV
- Severity: High / Medium / Low

## CV Rewrites
Pick the 3 CV bullets or sections that most need improvement for this specific role. For each:
- Current text (or paraphrase if long)
- Suggested rewrite
- Why this version is stronger

## Tailored Cover Note
Write a complete cover note paragraph (4 to 6 sentences) in the requested tone. It should:
- Reference something specific from the JD
- Lead with the candidate's strongest relevant experience
- Close with a clear signal of fit and interest
- Sound human, not templated

## One Thing Most Candidates Miss
One sharp, specific insight about what this particular role is really looking for that most applicants will not address.

Be honest. Be specific. Your goal is to help this candidate actually get the interview, not just feel good about their application."""

        try:
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            result = message.content[0].text

            # Extract score for banner
            score = 50
            verdict = "mid"
            lines = result.split('\n')
            for line in lines:
                if 'Fit Score:' in line:
                    try:
                        score_str = line.split(':')[1].strip().split('/')[0].strip().replace('*','')
                        score = int(score_str)
                    except:
                        pass
                if 'LIKELY TO BE SCREENED IN' in line:
                    verdict = "pass"
                elif 'LIKELY TO BE SCREENED OUT' in line:
                    verdict = "fail"

            # Score banner
            if score >= 70:
                banner_class = "score-high"
            elif score >= 50:
                banner_class = "score-mid"
            else:
                banner_class = "score-low"

            st.markdown(f"""
            <div class="score-banner {banner_class}">
              <div class="score-n">{score}/100</div>
              <div class="score-label">Fit score for this role</div>
            </div>
            """, unsafe_allow_html=True)

            if verdict == "pass":
                st.markdown("""
                <div class="verdict-pass">
                  Likely to be screened in — strong candidate profile for this role.
                </div>
                """, unsafe_allow_html=True)
            elif verdict == "fail":
                st.markdown("""
                <div class="verdict-fail">
                  Likely to be screened out — significant gaps to address before applying.
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="result-section">
            {result}
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                "Download Full Analysis",
                result,
                "jd_cv_gap_analysis.txt",
                "text/plain"
            )

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.markdown("""
<div class="footer-line">
  Most rejections happen before anyone reads your CV. Fit is not luck. It is language.
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; padding:12px 0 24px;'>
  <p style='font-size:13px; color:#7a7a76;'>Built by <strong>Bhavani Susmitha</strong> · IIM Ahmedabad · Ex-Revolut · <a href="https://www.linkedin.com/in/bhavanisusmitha" target="_blank" style="color:#c13b20;">LinkedIn</a></p>
</div>
""", unsafe_allow_html=True)