# Vedha AI Government Demo — Master Rules

## Project name

Vedha AI Government Demo

## Project purpose

Create a polished, working demonstration of the Vedha AI Learning Platform for presentation to government officials, education departments, schools, investors, teachers, parents, and students.

## Core product principle

A student must be able to learn and prepare independently at home without requiring continuous help from a school or teacher.

## Target users

- Students from Classes 1 to 12
- Parents
- Teachers
- School administrators
- Government education officials

## Demo interfaces

1. Student App
2. Teacher Portal
3. Parent Portal
4. Government Dashboard

## Demo technology

- Frontend: HTML5, CSS3, and vanilla JavaScript
- Backend: Python and FastAPI
- Demo database: SQLite
- AI integration: OpenAI API
- Testing: pytest
- Responsive web design
- Git and GitHub for version control

## Student App requirements

- Student profile
- Class selection
- Subject selection
- Concept selection
- English and Telugu language selection
- AI Tutor chat
- Text explanation
- Voice explanation
- Image or visual explanation
- Follow-up questions
- Practice generation
- Answer submission
- Image and PDF answer upload
- AI answer evaluation
- Progress dashboard

## Practice rule

Every concept must generate exactly 15 practice questions:

- 5 Easy
- 5 Medium
- 5 Hard

## Language rule

- Telugu-selected responses must primarily be in Telugu.
- Mathematical and technical terminology may remain in English where useful.
- Do not return a Telugu request entirely in English.
- Explanations must be age-appropriate.

## Educational rules

- Teach the concept before testing.
- Use simple examples.
- Show step-by-step explanations.
- Identify the student's mistake.
- Provide corrective guidance.
- Do not only reveal the final answer.
- Adapt the explanation based on student performance.

## UI rules

- Use a professional, government-ready appearance.
- Keep the design clean and modern.
- Make all interfaces mobile responsive.
- Provide clear navigation.
- Maintain consistent spacing and alignment.
- Use accessible text sizes.
- Support English and Telugu.
- Avoid clutter.
- Do not use placeholder-looking layouts in final demo screens.

## Code rules

- Keep frontend HTML, CSS, and JavaScript in separate files.
- Provide complete files rather than partial fragments.
- Use clear names.
- Avoid duplicated code.
- Validate all user inputs.
- Never hard-code API keys or secrets.
- Keep secrets in environment variables.
- Include error handling.
- Add tests for backend functionality.
- Do not modify unrelated files.
- Inspect existing files before changing them.

## Security rules

- Never expose the OpenAI API key in frontend JavaScript.
- Validate uploaded files.
- Reject unsafe file types.
- Do not allow one user to access another user's data.
- Do not perform destructive actions without explicit human approval.

## Agent workflow

For every feature:

1. Inspect relevant files.
2. State the implementation plan.
3. Implement only the approved scope.
4. Run relevant tests.
5. Fix test failures.
6. Review the final diff.
7. Summarize files changed and tests run.

## Human approval

Codex must not take any of the following actions without explicit human approval:

- Delete major project folders.
- Deploy to production.
- Expose secrets.
- Perform destructive database changes.
- Rewrite the entire architecture.

## Definition of done

A feature is complete only when:

- The requested behaviour works.
- UI alignment is correct.
- English and Telugu paths are considered.
- Error cases are handled.
- Relevant tests pass.
- No secrets are exposed.
- Changed files are summarized.
