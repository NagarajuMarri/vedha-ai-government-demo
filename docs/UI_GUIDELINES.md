# UI Guidelines

## Scope and architecture reference

These standards govern the four responsive web interfaces defined in `ARCHITECTURE.md`. They implement the master UI and language rules without changing the architecture: HTML, CSS, and vanilla JavaScript remain separate; privileged logic and secrets remain server-side.

## Design principles

- Government-ready means credible, calm, precise, accessible, and data-responsible—not visually bureaucratic or crowded.
- Student experiences prioritize clarity, encouragement, and age appropriateness.
- Parent and teacher experiences prioritize understandable action.
- Government analytics prioritize trustworthy hierarchy, definitions, and privacy-aware aggregation.
- Use reusable design tokens and component patterns; do not make final screens look like placeholders.

## Color philosophy

Use a restrained foundation with one primary action color, semantic status colors, and interface-specific accents. Color never carries meaning alone.

| Token intent | Guidance |
|---|---|
| Primary | Deep blue/indigo suitable for trust and primary actions |
| Secondary | Teal/green accent used sparingly for learning/progress |
| Neutral | Cool grays for surfaces, borders, and text hierarchy |
| Success | Green with icon and text label |
| Warning | Amber with icon and text label |
| Error | Red with icon and plain-language message |
| Information | Blue with icon and contextual explanation |

Final values must pass WCAG contrast checks in both themes. Charts require distinguishable patterns, labels, or markers in addition to color.

## Spacing system

Use a 4px base grid with tokens: `4, 8, 12, 16, 24, 32, 48, 64`. Default component gaps are 8 or 12px; card padding is typically 16 or 24px; page-section spacing is 24–48px. Avoid arbitrary spacing values unless a documented visual reason exists.

## Typography

- Use a legible system-first font stack with verified Telugu glyph coverage; select a bundled/web font only after performance and licensing review.
- Body text target: 16px minimum; supporting text should normally remain at least 14px.
- Use a modular, restrained heading scale and no more than three primary weights.
- Body line height: approximately 1.5–1.7; Telugu may require more line height to prevent clipping.
- Never use all caps for Telugu or long English labels.
- Allow browser zoom and text resizing without truncation or horizontal page scrolling.

## Responsive breakpoints

Use mobile-first layout rules. Reference breakpoints are `480px`, `768px`, `1024px`, and `1280px`; components must respond to available space rather than assume a device. Test at boundary widths and at 320px minimum viewport width. Tables may transform to labeled rows/cards only when meaning and comparison remain clear.

## Buttons

- Variants: primary, secondary, tertiary/text, and destructive.
- Use one dominant primary action per region.
- Labels begin with a clear verb; icons supplement rather than replace text unless universally understood with an accessible name.
- Minimum touch target: 44×44 CSS pixels.
- Provide hover, focus-visible, active, disabled, and loading states.
- Disabled controls must explain prerequisites nearby; loading actions prevent duplicate submission without trapping the user.
- Destructive actions require clear consequence text and proportionate confirmation.

## Cards

Use cards only to group related content. Maintain consistent padding, border/radius, heading order, and action placement. Cards must not become nested visual containers without necessity. Clickable cards require an obvious focus state and semantic interactive element.

## Forms

- Every input has a persistent visible label; placeholders are examples, not labels.
- Mark required fields in text and explain requirements before submission.
- Validate at sensible times and repeat validation server-side.
- Place errors next to fields and provide a focused summary for multi-field failures.
- Preserve safe user input after errors; never reveal whether protected records exist.
- Group related controls with semantic fieldsets/legends.
- Support keyboard, autocomplete where safe, and suitable input modes.

## Tables

- Use tables for genuine comparison, with captions, header cells, scopes, and clear units.
- Provide filtering/sorting status accessibly and retain user context.
- Align numbers consistently and format missing values explicitly.
- Paginate large datasets through the API standards; do not load unbounded records.
- Government small-cohort/privacy suppression must be visible without revealing the suppressed value.
- Offer an accessible textual summary for complex charts and dashboards.

## Navigation

Each interface uses stable primary navigation, a clear current location, descriptive page titles, and predictable back behavior. Mobile navigation must be keyboard/screen-reader operable and close without focus loss. Role switching, if approved, must never broaden server authorization. Breadcrumbs are appropriate for deep administrative hierarchy, not simple student flows.

## Accessibility

Target WCAG 2.1 AA practices: semantic landmarks/headings, keyboard completion, visible focus, meaningful labels, sufficient contrast, alt text, caption/transcript strategy for voice/media, reduced-motion support, and accessible validation/status announcements. Run automated checks and manual keyboard/screen-reader review as specified in `TESTING_STANDARDS.md`.

## Dark mode

Dark mode is optional for the initial demo unless approved in scope. If implemented, follow system preference by default, allow a persistent user choice, use semantic tokens instead of inverted literals, and retest contrast, charts, shadows, focus, images, and print. Dark mode must not delay accessible light-mode completion.

## English and Telugu

- Store interface copy outside presentation logic and identify the active language programmatically.
- Telugu-selected journeys use primarily Telugu; technical/mathematical English terms may remain where helpful.
- Do not concatenate translated fragments or assume equal text length.
- Allow 30–50% expansion, wrap labels safely, and verify glyph shaping, line height, numerals, punctuation, and screen-reader pronunciation.
- Preserve user language across navigation and errors; fallback copy must be explicit and never silently return an entirely English Telugu request.
- Language controls use language names (for example, “English” and “తెలుగు”), not flags.

## Animation rules

Animation communicates state or spatial continuity, never decorates critical workflows. Prefer 150–250ms transitions, avoid blocking sequences, disable nonessential motion under `prefers-reduced-motion`, and never flash content. Learning celebration must be age-appropriate, brief, optional, and non-disruptive.

## Loading states

- Show progress immediately for actions likely to exceed perceptual delay.
- Use skeletons only when they match the eventual layout; otherwise use a clear status indicator.
- AI actions show plain-language progress, bounded waiting expectations, cancel/retry where feasible, and no fabricated streaming content.
- Preserve layout to prevent shifts and prevent accidental duplicate submissions.

## Empty states

Explain why content is empty, whether it is expected, and the next permitted action. Distinguish “no data yet,” “no filter results,” “not authorized,” and “temporarily unavailable.” Never invent demo metrics to fill a screen.

## Error states

Use concise, non-blaming language with recovery guidance and a correlation/reference ID when support is needed. Do not expose stack traces, internal identifiers, sensitive existence, or provider details. Preserve safe context, focus the error, and provide retry only when it is safe.

## Interface styling

### Government Dashboard

Use restrained colors, strong hierarchy, dated data context, metric definitions, source/demo labels, accessible charts, clear filters, privacy suppression, and comparison-ready tables. Avoid decorative gamification, misleading precision, or crowded executive screens.

### Student App

Use friendly but professional color accents, short steps, clear progress, supportive feedback, readable examples, and age-appropriate density. Teach before testing; mistakes are framed as learning opportunities. Younger-class experiences may use larger targets and simpler navigation without becoming childish.

### Parent Portal

Use plain language, calm progress summaries, trends with explanations, and actionable support suggestions. Avoid ranking or alarming labels without context. Make child identity and selected time period unambiguous.

### Teacher Portal

Optimize for scanning and intervention: practical filters, class/subject/concept context, accessible tables/charts, and prioritized signals with evidence. Avoid reducing student ability to a single score.

## UI review gate

A screen is review-ready only when all responsive sizes, English/Telugu variants, keyboard/focus behavior, loading/empty/error/permission states, API failure behavior, and applicable privacy constraints have been designed and tested against `ARCHITECTURE.md` and `TESTING_STANDARDS.md`.
