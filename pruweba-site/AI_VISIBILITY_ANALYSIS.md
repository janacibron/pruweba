# RankFixer / AI Visibility Analysis
## Why AI search engines currently won't recommend Pruweba well

Before this update, pruweba.com had a RankFixer score of 38/100. After the first schema pass, score improved to 61/100. Remaining gaps are entity strength and cross-page consistency.

## Diagnosis: why recommendation still fails above 61

### 1. No unified entity graph
Homepage JSON-LD had `ProfessionalService`, `FAQPage`, and `Person`, but without explicit `Organization` and stable node IDs. RankFixer and AI crawlers infer less confidence from fragmented entities than from one connected graph.

### 2. Thin external identity signals
The earlier schema used only one `sameAs`. RankFixer-style scoring benefits from multiple verifiable external profiles that co-reference the same brand/person pair.

### 3. No explicit entity definition on-page
Crawlers need a clear textual entity definition in page copy, not only metadata. Without it, the page can be classified as generic agency prose.

### 4. Inconsistent routing/branding
Audit path existed as an in-page anchor before, not a first-class route. Dedicated `/audit` with its own schema strengthens topical authority and crawl depth.

## Fixes applied in this pass

### index.html
- Added `Organization` JSON-LD with canonical `@id` and cross-references.
- Added `Person` JSON-LD for Jan Michael Acibron with `worksFor` linkage.
- Kept `ProfessionalService` JSON-LD, now tied to `Organization` and `Person` via stable IDs.
- Added `BreadcrumbList` JSON-LD to reinforce site structure.
- Strengthened `sameAs` arrays with GitHub and LinkedIn.
- Added explicit About/Entity section near the top of visible content.
- Kept FAQ JSON-LD aligned with rendered FAQ content.

### audit.html
- Added the same unified schema block so `/audit` reinforces the same entity graph instead of a disconnected leaf page.

### llms.txt
- Rewrote to emphasize entity definition, external identity, and anti-misclassification guidance.

## Expected outcome
- Stronger entity resolution and cross-reference validation.
- Improved topical authority for founder/brand queries.
- Cleaner crawl structure with dedicated `/audit` page and breadcrumb signals.

## Required manual verification after deploy
1. Re-run RankFixer on `https://pruweba.com` and `https://pruweba.com/audit`. Target: 70+.
2. Run Google Rich Results Test on the homepage URL. Expect `FAQPage` eligible; `Organization`/`ProfessionalService` should parse as valid entities.
3. Confirm `/audit` still resolves and retains schema after production deploy.
