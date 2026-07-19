# Vedha AI Government Demo Runbook

## Purpose

This runbook presents one connected, controlled demonstration for the Chief Minister, IT Minister, education leaders and invited officials. All learner, class, family and dashboard data is synthetic. Do not describe demo records as live government data.

## Target duration

**12 minutes presentation + 3 minutes questions**

| Time | Interface | Outcome |
|---|---|---|
| 0:00–0:45 | Gateway | Explain one platform and four connected roles |
| 0:45–4:45 | Student | Demonstrate bilingual lesson, synchronized animation and answer guidance |
| 4:45–6:45 | Parent | Show weekly/monthly progress and exam preparation support |
| 6:45–9:45 | Teacher | Identify a weak concept and assign targeted remediation |
| 9:45–12:00 | Government | Show aggregate district insight without student-level drill-down |

## Pre-demo checklist

1. Pull `feature/sprint-4i-integrated-demo-journey`.
2. Activate the virtual environment and start the backend:
   ```powershell
   .venv\Scripts\activate
   python -m uvicorn backend.app.main:app --reload
   ```
3. Start the frontend in a second terminal:
   ```powershell
   python -m http.server 5500 --bind 127.0.0.1 --directory frontend
   ```
4. Open `http://127.0.0.1:5500/` in Chrome. Use Edge when demonstrating an installed Telugu system voice.
5. Confirm `http://127.0.0.1:8000/api/v1/health` responds.
6. Confirm the server reports `key_configured: true`; never display or share the API key.
7. Test microphone permission, English narration and Telugu narration.
8. Keep one prepared JPG/PNG phone photo of a handwritten answer below 5 MB.
9. Close unrelated windows and disable browser notifications.
10. Keep the typed fallback questions below ready in a private presenter note.

## Demonstration script

### 1. Gateway — one connected platform

Say: “Vedha supports the learner directly, helps the family act, gives teachers timely intervention signals, and gives government leaders privacy-conscious aggregate insight.”

Point out the synthetic-data boundary and open **Student App**.

### 2. Student — independent bilingual learning

1. Select Class 9, Mathematics, Fractions.
2. Choose one language profile:
   - English
   - Pure Telugu
   - Telugu with necessary English terms
3. Ask by voice: “Explain fractions from scratch using a pizza.”
4. Select narrated animation mode.
5. Show that each narrated sentence changes the visual scene.
6. Generate practice.
7. Answer the first question incorrectly once to show corrective guidance.
8. Answer incorrectly a second time to show the worked solution.
9. Demonstrate one voice answer or handwritten phone-photo answer.

Presenter safeguard: if the provider is unavailable, explain that Vedha uses the safe fallback lesson. Do not imply fallback content is a live AI response.

### 3. Parent — support at home

1. Open **Parent Portal**.
2. Select Ananya and the same language profile.
3. Switch between weekly and monthly reports.
4. Show subject completion and exam-readiness percentage.
5. Show completed and remaining exam topics.
6. Ask by voice: “Where does my child need help?”
7. Play the spoken insight.
8. Point to the recommended home activity.

### 4. Teacher — targeted intervention

1. Open **Teacher Portal**.
2. Select Class 9 · Section A.
3. Filter Mathematics.
4. Show Geometry as a weak concept and the prioritised student signals.
5. Assign guided remedial work to one student.
6. Review the AI-generated question and select **Approve**.
7. Ask by voice: “What should I assign today?”
8. Play the spoken class insight.

State clearly that assignments and approvals are simulated in this controlled demo; persistence and production authorization remain future work.

### 5. Government — aggregate decision support

1. Open **Government Dashboard**.
2. Select the same language profile.
3. Ask: “Show Guntur” or “గుంటూరు వివరాలు చూపించు”.
4. Play the generated spoken aggregate insight.
5. Compare mastery, practice completion and improvement after corrective guidance.
6. Emphasize: the Government Dashboard intentionally contains no student-level drill-down.

Closing line: “Vedha connects personal learning to timely family support, actionable teaching and responsible system-level insight—without exposing the learner.”

## Bilingual rehearsal matrix

| Journey | English | Pure Telugu | Telugu + English terms |
|---|---:|---:|---:|
| Student voice input and editable transcript | Required | Required | Required |
| Lesson narration and animation caption sync | Required | Required | Required |
| Practice voice/photo answer and second-attempt solution | Required | Required | Required |
| Parent dynamic report and spoken insight | Required | Required | Required |
| Teacher filters, actions and spoken insight | Required | Required | Required |
| Government district request and spoken aggregate insight | Required | Required | Required |

## Recovery plan

- **Microphone unavailable:** type the prepared request; explain that the editable transcript is the same submission path.
- **Telugu voice unavailable:** move to Edge with the Telugu system voice installed; keep Telugu text visible.
- **OpenAI timeout/provider failure:** retry once; if fallback appears, describe it accurately as the safe continuity path.
- **Browser cache shows older UI:** press `Ctrl+Shift+R`.
- **CORS error:** confirm the backend is running and the frontend origin is included in `VEDHA_CORS_ORIGINS`.
- **Unexpected secret or personal data appears:** stop the demo immediately; never proceed by hiding the screen region.

## Completion gate

The demo is ready only after both GitHub Actions workflows pass and one full English plus one full Telugu rehearsal completes without a critical blocker.
