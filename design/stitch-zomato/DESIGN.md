# Design System Document: The Intelligent Epicurean

## 1. Overview & Creative North Star

**Creative North Star: The Digital Concierge**
This design system is engineered to move beyond the transactional nature of food delivery and into the realm of high-end editorial curation. We are not just building a recommendation engine; we are crafting a bespoke culinary advisor. 

To achieve this, the system breaks away from "template-driven" layouts by utilizing **intentional asymmetry** and **tonal depth**. We prioritize breathing room (white space) to let food photography shine, while using sophisticated glassmorphism to signal the underlying AI intelligence. The experience should feel like flipping through a premium gastronomic magazine—authoritative yet approachable.

---

## 2. Colors

The color palette is rooted in the heritage 'Cranberry' red, but evolved through a Material Design 3 logic to provide the necessary range for complex AI interactions.

### The "No-Line" Rule
**Strict Mandate:** 1px solid borders for sectioning are prohibited. Layout boundaries must be defined exclusively through background color shifts or subtle tonal transitions. 
*   *Implementation:* Use `surface-container-low` (#f4f4f2) for a side panel sitting against a `surface` (#f9f9f7) main stage.

### Surface Hierarchy & Nesting
We treat the UI as physical layers of fine paper and frosted glass.
*   **Surface Lowest (#ffffff):** Reserved for primary content cards and active states.
*   **Surface (#f9f9f7):** The default canvas level.
*   **Surface Container Low (#f4f4f2):** Used for subtle grouping and background sectioning.
*   **Surface Container Highest (#e2e3e1):** Reserved for inactive or recessed structural elements.

### The "Glass & Gradient" Rule
AI-driven recommendations must utilize **Glassmorphism**. 
*   *Token:* `surface-container-lowest` at 70% opacity with a 16px backdrop-blur. 
*   *Signature Texture:* For Hero CTAs, use a linear gradient transitioning from `primary` (#b7122a) to `primary_container` (#db313f) at a 135-degree angle to provide a "pulsing" organic energy to the AI's suggestions.

---

## 3. Typography

**Font Family:** Manrope (Geometric Sans-Serif)

Our typography is the backbone of our editorial voice. We use extreme scale differences to create a clear information hierarchy.

*   **Display-LG (3.5rem):** Used for "Hero Moments" and major AI breakthroughs. Tracking should be tightened to -0.02em for a high-fashion look.
*   **Headline-MD (1.75rem):** Used for category titles. This is the primary "editorial" voice.
*   **Body-LG (1rem):** The workhorse for restaurant descriptions. Increased line-height (1.6) is required to maintain the "premium magazine" feel.
*   **Label-MD (0.75rem):** Bold, all-caps, with +0.05em letter spacing. Used for technical AI metadata (e.g., "MATCH SCORE: 98%").

---

## 4. Elevation & Depth

We eschew traditional drop shadows in favor of **Tonal Layering**.

*   **The Layering Principle:** Depth is achieved by stacking tiers. A `surface-container-lowest` card placed on a `surface-container-low` section creates a natural, soft lift.
*   **Ambient Shadows:** Where floating is required (e.g., a sticky AI prompt bar), use a shadow with a 40px blur and 4% opacity, tinted with the `on-surface` color (#1a1c1b). 
*   **The "Ghost Border" Fallback:** If a container lacks sufficient contrast, use the `outline-variant` token (#e4bebc) at **15% opacity**. High-contrast, 100% opaque borders are strictly forbidden.
*   **Glassmorphism & Depth:** AI "Thought Bubbles" or floating cards must use backdrop blurs. This integrates the UI with the background photography, preventing the "pasted on" look of standard apps.

---

## 5. Components

### Buttons
*   **Primary:** `primary` (#b7122a) background with `on-primary` (#ffffff) text. 8px radius (`DEFAULT`).
*   **Secondary:** No background. Use a `Ghost Border` and `primary` text.
*   **AI Action:** A glassmorphic button with a subtle `primary` glow (8px blur) to signify intelligence.

### AI Cards & Lists
*   **Constraint:** Zero dividers. Separate list items using 16px of vertical whitespace or a subtle shift from `surface` to `surface-container-low`.
*   **AI Recommendations:** These should utilize the 1.5rem (`xl`) roundedness to feel distinct from standard restaurant cards (which use the 0.5rem `DEFAULT` radius).

### Input Fields (AI Search)
*   **Style:** Minimalist. No bottom line or full border. Use a `surface-container-high` fill with an 8px radius. 
*   **State:** On focus, the field should transition to a subtle `primary_fixed` (#ffdad8) glow.

### Signature Component: The "Match Gauge"
A custom circular progress component for AI match percentages. It uses a `tertiary` (#006762) stroke to provide a sophisticated "health/quality" contrast against the `primary` brand red.

---

## 6. Do's and Don'ts

### Do
*   **Do** embrace asymmetry. If you have a list of restaurants, try offseting the images to create a more dynamic, curated flow.
*   **Do** use `secondary_fixed_dim` (#c8c6c6) for "muted" text rather than just lowering the opacity of black.
*   **Do** ensure all "glass" elements have a 1px `Ghost Border` at 10% opacity to ensure the edges don't disappear on white backgrounds.

### Don't
*   **Don't** use pure black (#000000). Always use `Peppercorn` (#2D2D2D) or the `on-surface` token (#1a1c1b).
*   **Don't** use standard Material Design elevations (Shadow 1, Shadow 2, etc.). Stick to Tonal Layering.
*   **Don't** crowd the interface. If a screen feels full, increase the white space. The "Digital Concierge" never rushes the guest.