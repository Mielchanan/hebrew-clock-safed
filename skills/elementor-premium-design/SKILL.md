---
name: elementor-premium-design
description: Design and build Elementor/WordPress sites (Hebrew RTL or English) that look premium, not AI-generic, with GSAP and Lenis motion. Use for landing pages, redesigns, polish, animation or design review.
---

# Elementor Premium Design

A merged playbook for building websites in Elementor that do not look AI-generated. It distills three open-source design skills (Emil Kowalski's design-engineering skill, Impeccable by Paul Bakaus, and Taste Skill by Leon Lin) and adapts them to Elementor, WordPress, Hebrew/RTL and GSAP + Lenis.

Reply to the user in the language they write in (usually Hebrew).

## 0. Before designing: read the brief

1. **Pick the mode** from the surface, not the business:
   - **Persuade**: landing page, campaign, pricing. Design is the product; earn attention and one action.
   - **Operate**: forms, client areas, dashboards, booking. Scanability and consistency beat expression.
   - **Read**: articles, blog, docs, book pages. Measure, rhythm and comprehension first.
   - **Experience**: portfolio, gallery, showcase. The work leads; the interface recedes.
2. **State a one-line design read** before building: audience, mood, and the three dials:
   - `DESIGN_VARIANCE` 1-10 (symmetric grid to asymmetric/editorial)
   - `MOTION_INTENSITY` 1-10 (hover states only to scroll choreography)
   - `VISUAL_DENSITY` 1-10 (gallery-airy to cockpit-dense)
3. **The brief wins.** If the client names fonts, colors or a style, honor them even when they hit a rule below. The rules are defaults to override with a reason, not taste to impose.
4. **Refinement preserves; redesign replaces.** Polishing an existing site keeps its identity, copy and structure. If the concept itself is wrong, say so and recommend a redesign instead of smuggling one in.
5. If the brief is ambiguous on something expensive (brand direction, page structure), ask one question. Otherwise decide and say what you decided.

## 1. AI tells to refuse by default

These are the signatures that make a site read as "built by AI." Each can be earned back only by the brief's own words.

**Color and surface**
- Purple/blue gradient heroes, neon glows, glow halos, gradient text on headings.
- More than one accent color. Lock one accent for the whole page; no blue CTA appearing in section 7 of an orange site.
- Pure `#000` / `#fff`. Use off-black and off-white.
- The "premium" cliché: warm cream background + brass/clay accent + espresso text. Pick a less predictable family (cold silver, forest + amber, cobalt + one neutral, terracotta + slate, monochrome + one saturated pop).
- Glassmorphism as decoration, side-stripe borders (`border-left: 4px` accent on cards), hard offset "brutalist" shadows outside a brutalist brief.
- Pure black drop shadows on light backgrounds. Tint shadows to the background hue; give them offset and soft blur.

**Layout**
- Three identical icon + heading + text cards as the page structure. Nested cards are always wrong.
- An eyebrow label above every section heading. At most one per three sections; usually zero.
- Section numbers (01 / 02 / 03), "Step 1 / Step 2" labels, scroll cues ("Scroll to explore"), decorative status dots, vertical rotated text, decorative grid lines.
- The same layout family repeated: each section layout type appears once; a long page uses at least four different families. Max two image/text zigzags in a row.
- Hero problems: more than 4 text elements, headline over 2 lines on desktop, subtext over ~20 words, CTA below the fold, huge top padding, logo walls or trust strips inside the hero (they go directly below).
- Centered hero by reflex when variance is above 4. Prefer split, start-aligned with asset on the end side, or asymmetric whitespace.
- Fake product screenshots built from divs, hand-drawn decorative SVG illustrations, emoji or unicode glyphs as icons. Use real images, a real icon library (Phosphor, Tabler, Remix) and one stroke weight.
- A text-only page is not minimalism. Ship real imagery, or leave labeled placeholders and tell the user exactly which images are needed and at what size.

**Copy**
- Filler verbs: elevate, seamless, unleash, revolutionize, next-gen. In Hebrew too: "לקחת לשלב הבא", "חוויה ייחודית", "פתרון מקצה לקצה", "מהפכה".
- Fake-precise numbers (99.9%, 4.1x) that the client never gave you. Label sample data as sample.
- Generic names (John Doe, Acme, Nexus). Use realistic, locale-appropriate names.
- Two CTAs with the same intent but different labels. One label per intent across nav, hero and footer. CTA text fits on one line, ideally 1-3 words.
- **No em-dash (—) or en-dash (–) anywhere on the page.** Use a period, comma, colon or parentheses. Ranges use a hyphen.
- Cute AI copy is worse than plain copy. Reread every visible string before finishing.

## 2. Typography

- Use the fewest families that make hierarchy unmistakable; usually one, at most two with a clear role each. 3-4 sizes, 2-3 weights.
- Body text at least 16px, measure 45-75 characters (`max-width: 65ch`). Display type up to ~6rem; plan headline size and hero image size together.
- Emphasis inside a headline uses weight of the same family, never a random second family.
- Avoid the model-favorite defaults (Inter for Latin; Fraunces / Instrument Serif as display). Serif only when the brand is genuinely editorial, luxury or heritage.
- Theme browser surfaces too: `::selection`, caret, focus ring, link underline offset, tabular numerals for data.

**Hebrew typography (essential)**
- Hebrew has no uppercase and no true italics. Never set Hebrew in `text-transform: uppercase` styles, never letter-space it (keep tracking at 0), and never fake italic. Emphasis comes from weight or color.
- Hebrew reads smaller than Latin at the same px. Body around 17-18px, line-height 1.6-1.75. Headlines line-height 1.15-1.25 (Hebrew needs more than Latin display).
- Choose a real Hebrew face, not the browser fallback. Free options: Heebo, Assistant, Rubik, Noto Sans Hebrew, IBM Plex Sans Hebrew, Frank Ruhl Libre (serif, editorial), Secular One / Suez One (display). For premium work suggest a licensed face from an Israeli foundry instead of defaulting to Heebo on every project.
- Pair the Hebrew face with a Latin face whose x-height and weight match, and set it as part of the same font stack.
- Mixed Hebrew/English/numbers: wrap Latin strings, phone numbers and prices in `<bdi>` or `unicode-bidi: isolate` so punctuation lands on the correct side.
- Avoid widows: `text-wrap: balance` on headings, `text-wrap: pretty` on paragraphs.

## 3. Color, shape, spacing

- One palette per project; neutrals of one temperature; one accent, saturation under ~80%.
- Contrast: body and placeholder text at least 4.5:1, large text at least 3:1, in every state, including buttons over photos (add a scrim).
- One corner-radius system for the page (all sharp, all soft 12-16px, or pill only for small controls) applied everywhere.
- Cards only when elevation carries real hierarchy. Otherwise group with spacing, a single divider or a background tint.
- Spacing rhythm: tight inside groups, generous between groups, more space above a heading than below it. One spacing scale.
- One page theme. Do not drop a cream section into a dark page unless it is one deliberate theme switch.

## 4. Elementor implementation

**Set the system first, in Site Settings**
- Define Global Colors (background, surface, text, muted text, accent, border) and Global Fonts (display, heading, body, small) before building. Every widget uses globals, never hand-picked hex values.
- Set Layout > content width and the breakpoints, plus default container padding and gap, so spacing is systematic.
- Build with Flexbox/Grid containers, not legacy sections and columns. Keep nesting shallow.
- Check every multi-column container at tablet and mobile and set its stacking order and spacing explicitly. Asymmetric desktop layouts collapse to one clean column on mobile.

**RTL**
- Use logical properties in custom CSS (`margin-inline-start`, `padding-inline-end`, `inset-inline-start`, `text-align: start`) so styles survive language switches.
- Mirror directional icons (arrows, chevrons, "next") in RTL. Do not mirror logos, media controls or checkmarks.
- Slider and carousel direction must follow RTL.

**Custom CSS and classes**
- Give animated or custom-styled elements a class in Advanced > CSS Classes (e.g. `js-reveal`, `js-hero-title`). Hook all JS to classes, never to Elementor's generated `elementor-element-xxxx` IDs.
- Put shared CSS in Site Settings > Custom CSS (or the child theme), not scattered across widgets.

**Motion: do not use Elementor's built-in Entrance Animations across the page.** The same fadeInUp on every section is the most recognizable template tell. Use one authored motion system with GSAP.

## 5. Motion with GSAP + Lenis

### Principles (from Emil Kowalski)
- Every animation needs a purpose: hierarchy, storytelling, feedback, or state change. "It looks cool" on something seen often means no animation.
- One authored moment per page beats scattered effects. Never the same entrance on every section.
- Easing: entering or exiting uses ease-out; moving on screen uses ease-in-out; never ease-in for UI. Use strong custom curves: `cubic-bezier(0.23, 1, 0.32, 1)` (out), `cubic-bezier(0.77, 0, 0.175, 1)` (in-out). GSAP equivalents: `power3.out`, `expo.out`, `power3.inOut`.
- Durations: button press 100-160ms, tooltips 125-200ms, dropdowns 150-250ms, modals 200-500ms. UI under 300ms. Scroll and marketing reveals can run 0.6-1.2s.
- Never animate from `scale(0)`. Start from `scale(0.95)` with opacity 0. Popovers scale from their trigger; modals from center.
- Buttons respond to press: `transform: scale(0.97)` on `:active`.
- Exit faster than enter. Stagger 30-80ms between items; never block interaction while it plays.
- Animate `transform`, `opacity`, `clip-path`, `filter: blur()` (under 20px). Never `top/left/width/height/margin`. Avoid `transition: all`.
- Hover effects only for real pointers: wrap in `@media (hover: hover) and (pointer: fine)`.
- `prefers-reduced-motion: reduce` keeps opacity/color fades and removes movement, parallax, pinning and smooth scroll.
- Never use `window.addEventListener('scroll', ...)`. Use ScrollTrigger or IntersectionObserver.

### Loading (Elementor Custom Code, or WPCode / child theme)
Load once, site-wide, in the footer:

```html
<link rel="stylesheet" href="https://unpkg.com/lenis@1.3.26/dist/lenis.css">
<script src="https://unpkg.com/lenis@1.3.26/dist/lenis.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/ScrollTrigger.min.js"></script>
<!-- Optional: SplitText.min.js for line/word reveals (GSAP and all its plugins are free) -->
```

### Base setup

```html
<script>
document.addEventListener('DOMContentLoaded', () => {
  // Do not run inside the Elementor editor
  if (document.body.classList.contains('elementor-editor-active')) return;

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isRTL = document.documentElement.dir === 'rtl';
  const fromStart = isRTL ? 1 : -1; // x sign for "coming from the reading-start side"

  gsap.registerPlugin(ScrollTrigger);

  // Smooth scroll (skip on reduced motion)
  let lenis = null;
  if (!reduce) {
    lenis = new Lenis({ lerp: 0.1, smoothWheel: true, anchors: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  if (reduce) return; // content stays visible and static

  // Reveal: elements with class js-reveal, grouped per container
  gsap.utils.toArray('.js-reveal').forEach((el) => {
    gsap.from(el, {
      y: 24, opacity: 0, duration: 0.9, ease: 'expo.out',
      scrollTrigger: { trigger: el, start: 'top 85%', once: true }
    });
  });

  // Recalculate after images and fonts settle
  window.addEventListener('load', () => ScrollTrigger.refresh());
});
</script>
```

Rules for this setup:
- Content must be visible without JS. Use `gsap.from()` (or set hidden states from JS), never hide elements in CSS waiting for JS.
- In RTL, horizontal offsets flip: multiply x values by `fromStart`, and horizontal-scroll sections translate in the positive direction.
- Elementor sticky headers, popups and nested scroll areas: add `data-lenis-prevent` to scrollable popups, menus and off-canvas panels.
- Mobile: Lenis leaves touch scrolling native by default; keep it that way. Reduce or disable pinned and scrubbed sections under 768px with `gsap.matchMedia()`.
- Use pin/scrub (ScrollTrigger) only for real storytelling: a product walkthrough, a process, a horizontal gallery. Simple "appear on scroll" does not need pinning.

## 6. Mobile that feels native

Most "it feels cheap on the phone" problems are platform details, not design. Add this baseline once, in Site Settings > Custom CSS (or the child theme):

```css
html {
  -webkit-tap-highlight-color: transparent; /* no gray flash on tap */
  -webkit-text-size-adjust: 100%;
}
input, textarea, select { font-size: 16px; } /* below 16px iOS zooms into the field and stays zoomed */
a, button, .elementor-button, [role="button"] { touch-action: manipulation; }
.elementor-button, .e-n-tab-title, [role="button"] { -webkit-user-select: none; user-select: none; }
.elementor-button:active { transform: scale(0.97); } /* press feedback for touch */
.js-hero { min-height: 100svh; } /* use on the hero container instead of 100vh */
```

And in the page head (Elementor Custom Code, location `<head>`):

```html
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#ffffff">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0a0a0a">
```

Set both values to the header's actual background color, not the brand color.

Rules:
- **Never disable zoom.** No `user-scalable=no` or `maximum-scale=1`. The 16px input rule fixes the zoom problem instead.
- **Hover only for mouse.** In custom CSS, put every `:hover` style inside `@media (hover: hover) and (pointer: fine)` so taps don't leave elements stuck in their hover state. Touch users get feedback through `:active`.
- **Full-height sections:** `100svh` for heroes (stable while scrolling), `100dvh` only for app-like full screens. Plain `100vh` hides the bottom of the section under the mobile browser bar.
- **Fixed bottom bars and floating buttons** (WhatsApp, call, cart) need `padding-bottom: env(safe-area-inset-bottom)` so they clear the iPhone home indicator.
- **Carousels:** in RTL the swipe direction must match reading direction; a horizontal carousel gets `touch-action: pan-y` so the page can still scroll vertically over it.
- **Form fields:** set the right keyboard (`type="tel"` for phone, `type="email"`, `inputmode="numeric"` for codes). Elementor Forms supports these field types; use them instead of plain text.
- Touch targets at least 44x44px, including menu items and icons.
- Device emulation in Chrome does not reproduce any of this. Say what was verified in code and ask the user to confirm on a real phone.

## 7. Commands

The user may ask for these by name. Each one is a focused pass.

- **polish**: final quality pass, preserving the current design. Order: broken tasks and inaccessible paths, then missing states (hover, focus, disabled, loading, empty, error, success), then hierarchy and responsive drift, then visual and motion inconsistency, then cleanup. Check desktop, tablet and mobile.
- **bolder**: amplify one named section that reads flat, and touch nothing else. Bring it up to the strongest moves the rest of the page already makes (its display type at full strength, its signature motif) instead of adding new effects, colors or fonts. Make one decisive move, then quiet everything around it. The result must look like the same brand, more sure of itself.
- **quieter**: tone down a loud design without making it generic. Lower saturation (70-85%), fewer colors with neutrals doing the work, lighter weights (900 to 600, 700 to 500), more whitespace, thinner or no borders, shorter motion distances (10-20px), no bounce. Keep a few anchors bold; hierarchy must survive.
- **audit**: technical report, no fixes. Score 0-4 each: Accessibility, Performance, Theming (globals vs hard-coded values), Responsive, Implementation integrity. Total out of 20. List issues by severity (P0 blocks a task, P1 major or WCAG AA failure, P2 minor, P3 polish) with location, impact and the command that fixes it. Include what works well.
- **break**: stress-test with realistic worst-case content, then report. See section 8.
- **distill**: strip to the essence. One primary goal and one primary action per page. Cut redundant sections, decoration, colors (1-2 plus neutrals), font sizes (3-4) and copy ("cut every sentence in half, then again"). Never remove information users need to decide.
- **clarify**: rewrite UI copy so users know what happened, what matters and what to do next. Buttons name the action ("שליחת הטופס" / "Send request", not "OK"). Labels above inputs, never placeholder-as-label. Errors state what failed and how to fix it.
- **typeset**: audit and fix the type system: roles, scale, measure, line height, Hebrew/Latin pairing, font loading.
- **animate**: add purposeful motion per section 5. Name the one authored moment first.
- **review**: report issues as a single table with columns `| Before | After | Why |`, one row per issue.

## 8. Break it before the client does

Templates are designed against kind demo content. Real clients paste in a 9-word business name, a long Gmail address, or a team section with one person. Before handing over, test the page with realistic worst-case content, never nonsense like "aaaaaaa".

Try, on the actual widgets:
- **Long Hebrew text:** a business or product name of 6-9 words, a long headline, a button label of 4 words, a long menu item.
- **Unbreakable strings:** a long email (`office.yerushalmi.accounting@gmail.com`), a URL, a long English word inside Hebrew text.
- **Mixed direction:** a phone number, a price with a currency sign, and an English brand name inside a Hebrew sentence. Punctuation must land on the correct side.
- **Short and missing:** a 2-letter name, an empty optional field, a missing image, a testimonial without a photo.
- **Counts:** exactly 1 item ("1 פריטים" is wrong), zero items, many items (a gallery of 40 images, a loop grid with 1 post).
- **Environment:** 320px width, the real container width (a sidebar is not full width), browser zoom at 200%.

Common breaks and fixes:

| What you see | Fix |
| --- | --- |
| Email or URL runs past the edge | `overflow-wrap: anywhere` on that element |
| Text overflows its flex box | `min-width: 0` on the text container |
| Icon or avatar squished into an oval | `flex-shrink: 0` on the icon/image |
| Button label wraps or overflows | Shorten the label, or let width come from content (no fixed width) |
| Phone number or price reversed in RTL | Wrap in `<bdi>` or `unicode-bidi: isolate` |
| Hebrew letters clipped top or bottom | Looser line-height, no `overflow: hidden` on text |
| Empty line or stray dash where a field was empty | Hide the element when empty instead of rendering a placeholder |
| Truncated text with no way to read it | Add a `title` or show the full text elsewhere |

Report as a table: `| # | Severity | Element | Worst-case content | What happens | Fix |`, where severity is **Broken** (unreadable or unreachable), **Ugly** (readable but visibly wrong) or **Fragile** (fine now, one realistic step from breaking). Then list decisions that are the user's to make (truncate or wrap, what an empty field shows) with a recommendation, and what held up. Fix only after the user says which items to fix.

## 9. Finish checklist

Run once, fix everything in one batch, confirm once. Do not loop endlessly.

- [ ] Desktop, tablet and mobile all checked; nothing overflows; nav fits one line on desktop.
- [ ] Contrast passes in every state, including buttons on images and form placeholders.
- [ ] One accent color, one radius system, one theme, globals used everywhere.
- [ ] No AI tells from section 1: no em-dashes, no eyebrow on every section, no identical card rows, no filler copy.
- [ ] Hebrew: no letter-spacing, no uppercase styling, no fake italics, correct bidi on numbers and Latin.
- [ ] Every interactive element has hover, focus, active and disabled states; forms have labels, errors and a success state.
- [ ] Motion has a reason, honors reduced motion, does not run in the Elementor editor, and never hides content when JS fails.
- [ ] Images are real (or clearly listed as needed), sized, lazy-loaded below the fold; hero image preloaded. No layout shift.
- [ ] Mobile baseline in place: 16px inputs, no tap flash, hover gated, hero on `100svh`, theme-color set, nothing under the home indicator.
- [ ] Worst-case content tried (section 8): long Hebrew names, long email, mixed direction, empty fields, 1 item, 320px, 200% zoom.
- [ ] Every brief requirement is present and findable within seconds.
