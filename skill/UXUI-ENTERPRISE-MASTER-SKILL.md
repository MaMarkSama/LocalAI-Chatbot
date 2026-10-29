# UX/UI Enterprise Master Skill — Integrated Edition

> **วัตถุประสงค์:** รวม `UX/UI Master Brief` + `enterprise-design-system` ให้เป็นแนวทางเดียวสำหรับ AI agent ที่ทำ UX/UI audit, redesign, tokenization, component engineering และ migration ในระบบจริง  
> **ขอบเขต:** ใช้กับ dashboard, internal tools, data-dense products, AI/ML interfaces และเว็บ/แอปทั่วไป โดยปรับตาม stack และข้อจำกัดของโปรเจกต์  
> **วิธีใช้:** วางไฟล์นี้ไว้ที่ root ในชื่อ `UXUI-MASTER-BRIEF.md` และอ้างจาก `AGENTS.md` / `CLAUDE.md` จากนั้นกรอก Project Context และสั่งเริ่มเฟสที่ต้องการ

## A. Unified Operating Contract

### A1. การแบ่งความรับผิดชอบของ skill

| ส่วน | เจ้าของ | ขอบเขต |
|---|---|---|
| Product context & project constraints | `PRODUCT.md`, `DESIGN.md`, Project Context และผู้ใช้ | เป้าหมาย ผู้ใช้ แบรนด์ ข้อจำกัด และสิ่งที่ห้ามเปลี่ยน |
| Design-system integrity | `enterprise-design-system` (หรือ `enterprise-uxui-cto` หากโปรเจกต์ใช้ skill นี้) | token architecture, component contract, accessibility/performance gates, governance, migration safety |
| Visual craft & UX judgment | `impeccable` | hierarchy, typography, composition, visual taste, critique, polish และ anti-pattern review |
| Implementation | AI coding agent + repository conventions | แก้โค้ดอย่างจำกัดขอบเขต ทดสอบ และรายงานหลักฐาน |

**หลักการ:** Impeccable เป็นผู้เสนอและวิจารณ์คุณภาพภาพ/UX; Enterprise Design System เป็นผู้คุมความสอดคล้อง ความปลอดภัยของระบบ และ quality gates. ทุกข้อเสนอด้านภาพต้องแปลงผ่าน token และ component contract ก่อนลงโค้ด

### A2. ลำดับอำนาจเมื่อข้อกำหนดขัดแย้งกัน

1. ข้อจำกัดที่ผู้ใช้ยืนยันและ `Project Context` รวมถึง out-of-scope
2. Accessibility และข้อกำหนดที่เกี่ยวข้องกับความปลอดภัย/การเข้าถึง — ห้ามลดเพื่อความสวย
3. `DESIGN_SYSTEM.md` และ token files เป็น source of truth ของระบบออกแบบ; `PRODUCT.md` / `DESIGN.md` เป็น source of truth ด้านผลิตภัณฑ์ แบรนด์ และทิศทาง
4. หลัก design-system integrity, component contract, migration และ governance ในเอกสารนี้
5. ข้อเสนอ visual craft จาก Impeccable
6. convention เดิมของ repository ในส่วนที่ไม่ขัดข้อข้างต้น

หาก `DESIGN_SYSTEM.md` ไม่มี ให้ **หยุดก่อนงาน UI ขนาดใหญ่** และเสนอสร้างจาก skeleton ด้านล่าง; งาน bug/fix เล็กที่จำเป็นทำได้โดยระบุช่องว่างนี้ในรายงาน หาก `PRODUCT.md` ไม่มี ให้แนะนำ `/impeccable init` หรือ workflow setup ที่เวอร์ชันจริงรองรับ หาก `DESIGN.md` ไม่มี ให้สร้าง/ร่างจากระบบที่มีและให้ผู้ใช้ตรวจ

### A3. กฎป้องกันการเดาและการขยายขอบเขต

- ห้ามเดา stack, metrics, component inventory, commands, test result, baseline หรือ brand values; สิ่งที่ไม่ทราบให้ระบุ `UNKNOWN`.
- ตรวจคำสั่ง Impeccable ที่ติดตั้งจริงก่อนใช้ ชื่อ/รูปแบบ command อาจเปลี่ยนตามเวอร์ชัน
- ห้ามเปลี่ยน business logic, API contract, data model หรือ auth semantics ในงาน UI โดยไม่ได้รับอนุมัติ
- ห้ามแตะไฟล์นอกขอบเขตที่ระบุ และห้าม rewrite แบบ big-bang
- ก่อนเพิ่ม dependency หรือ shared component ให้แสดงเหตุผลและทางเลือก
- ทุกการตัดสินใจที่มีนัยสำคัญต้องบันทึก rationale, trade-off และผู้อนุมัติ (ถ้ามี)
- หากหลักฐานไม่พอ ให้หยุดตรงจุดนั้น ถามหรือเสนอแผนตรวจสอบ แทนการสร้างข้อมูลขึ้นเอง

### A4. Protocol ทุกงาน

1. **Load context:** อ่าน `DESIGN_SYSTEM.md`, tokens, `PRODUCT.md`, เอกสารนี้, Impeccable guidance และ conventions ตามลำดับที่กำหนด
2. **Classify:** `new-feature | redesign | component | token | migration | audit | bug`
3. **Inventory:** สำรวจ tokens, components, states, patterns และช่องว่างที่เกี่ยวข้อง
4. **Plan:** งานใหญ่ต้องเสนอ scope, files, sequence, risk, tests และ rollback แล้วรออนุมัติ
5. **Baseline first:** เก็บสภาพก่อนแก้เท่าที่วัดได้ พร้อมระบุวิธีและข้อจำกัด
6. **Implement:** ใช้ของเดิมและ token ก่อน สกัดปัญหาซ้ำเป็นระบบเมื่อพบซ้ำตั้งแต่ 3 จุดขึ้นไป
7. **Refine:** ใช้ Impeccable ตาม command ที่ตรวจพบจริง เช่น critique → แก้ → polish
8. **Verify:** ตรวจ gates ที่เกี่ยวข้อง และเปรียบเทียบกับ baseline
9. **Report & stop:** รายงานผลและหยุดเมื่อจบ phase/task ไม่ข้ามเฟสเอง เว้นแต่ผู้ใช้สั่ง

---

## B. Project Context

กรอกก่อนใช้งานจริง หากไม่ทราบให้ใส่ `UNKNOWN`.

| หัวข้อ | ค่า |
|---|---|
| ชื่อระบบ | `<...>` |
| ประเภท | `<dashboard / platform / public web / internal tool>` |
| Stack / Styling | `<...>` |
| ผู้ใช้เป้าหมาย / งานหลัก / อุปกรณ์ | `<...>` |
| ภาษา | `<TH / EN / bilingual>` |
| ทีม / ผู้รับผิดชอบ | `<...>` |
| กรอบเวลา | `<...>` |
| ปัญหาหลัก 3 ข้อ | `1) ... 2) ... 3) ...` |
| In scope | `<...>` |
| Out of scope / ห้ามแตะ | `<...>` |
| เป้าหมายที่วัดได้ | `<baseline-backed target หรือ UNKNOWN>` |
| Feature flag / rollback | `<... หรือ UNKNOWN>` |

---

## C. Phased Delivery Workflow

**ทำทีละเฟสและหยุดรายงานทุกครั้ง** เกณฑ์ผ่านแต่ละเฟสเป็น gate ไม่ใช่คำแนะนำเฉย ๆ

### Phase 0 — Setup & Product Understanding
- ตรวจ stack, repo conventions, skills และ commands ของ Impeccable ที่มีจริง
- ตรวจ `PRODUCT.md`, `DESIGN.md`, `DESIGN_SYSTEM.md` และ token files
- หากเป็นระบบเดิม ให้ document ระบบปัจจุบันจากหลักฐานจริง; แยก observation ออกจาก assumption
- ส่งมอบ: `PRODUCT.md`, `DESIGN.md`, `DESIGN_SYSTEM.md` (ถ้าจำเป็น), assumptions / open questions
- Gate: ผู้ใช้ยืนยันทิศทาง product, audience, brand และ scope

### Phase 1 — Audit & Baseline (ห้ามแก้โค้ด)
- UI inventory: สี ฟอนต์ spacing, radius, component, duplicate patterns — นับจากโค้ดจริง
- UX review ของ 3–5 critical flows หรือจำนวนที่ผู้ใช้กำหนด
- A11y: contrast, keyboard, focus, labels, targets, zoom/reflow, screen-reader semantics
- Performance: LCP, INP, CLS, bundle size; ระบุ lab vs real-user data และสิ่งที่วัดไม่ได้
- จัดลำดับ issue ด้วย impact × effort และ severity P0–P3 พร้อม evidence (file/line/screenshot/metric)
- ส่งมอบ: `docs/uxui/01-audit.md`
- Gate: ทุก finding มีหลักฐาน; ไม่มีการแก้โค้ดใน phase นี้

### Phase 2 — UX & Design Strategy
- ตั้งเป้าหมายที่วัดได้จาก baseline; กำหนดหลักการออกแบบ 3–5 ข้อ (พร้อม “หมายถึงอะไร / ไม่ได้หมายถึงอะไร”)
- ระบุสิ่งที่จะไม่ทำ, trade-offs, critical flows และ success metrics
- ส่งมอบ: `docs/uxui/02-strategy.md`
- Gate: เป้าหมายโยงกับ baseline หรือระบุชัดว่า baseline ยังเก็บไม่ได้

### Phase 3 — Design Tokens
- สกัดค่าจาก UI เดิมก่อน; จัดโครง primitive → semantic → component
- Components ใช้ semantic tokens เป็นหลัก; primitive เป็นแหล่งค่า ไม่ใช้ตรงใน component
- รองรับ light/dark/high-contrast ด้วย semantic overrides; dark mode ต้องออกแบบ ไม่ใช่ invert
- กำหนด type, spacing (ฐาน 4px), radius, border, elevation, motion, z-index, breakpoint, opacity
- วาง pipeline DTCG JSON → Style Dictionary → CSS/TS/platform outputs เมื่อเหมาะกับ stack
- ส่งมอบ: `tokens/**/*.json`, generated variables และ `docs/uxui/03-tokens.md`
- Gate: build token ผ่าน; visual regression ไม่เปลี่ยนโดยไม่ได้ตั้งใจ (เป้าหมาย diff = 0 สำหรับ pure token refactor)

### Phase 4 — Component Foundation
- ตรวจ component/composition เดิมก่อนสร้างใหม่
- เลือก headless primitives ตาม stack เช่น Radix UI / React Aria / Headless UI; อย่าเพิ่ม dependency โดยไม่ประเมิน
- เริ่มจาก foundation ที่ใช้จริง เช่น Button, Input, Select, Checkbox, Dialog, Toast, Table
- ระบุ API และเสนอ 1 ตัวเลือกหลัก + 1 ทางเลือก พร้อม trade-off ก่อน implementation
- Component spec: purpose/do-not-use, anatomy, API, variants/sizes, states, tokens, accessibility, responsive/container, i18n, content rules, examples
- ทุก component มี tests, docs/usage, preview/story เมื่อ tooling รองรับ และ a11y notes
- Gate: ผ่าน Definition of Done ที่ใช้บังคับได้กับ component นั้น

### Phase 5 — Incremental Migration (Strangler Fig)
- เลือก flow impact สูงและ risk ต่ำ; migrate ทีละ screen/flow
- ใช้ feature flag หาก architecture รองรับ; ถ้าไม่รองรับให้เสนอ rollout/rollback ทางเลือก
- ลำดับแนะนำ: tokens → high-frequency primitives → high-traffic flows → long tail
- ห้ามมี button systems สองชุดบนหน้าจอเดียวกัน
- ระบุ A/B หรือวิธีเทียบที่เหมาะสม; ไม่อ้างผล A/B หากไม่ได้รัน
- ส่งมอบ: `docs/uxui/05-migration.md` (scope, owner, done criteria, risk, rollback)
- Gate: metrics ไม่แย่กว่า baseline หรือมีข้อยกเว้นที่ผู้ใช้ยอมรับอย่างชัดเจน

### Phase 6 — Polish & Hardening
- critique → fixes → polish ด้วย Impeccable; ตรวจ anti-pattern
- optimize เฉพาะเมื่อ command มีจริงและมีหลักฐานรองรับ
- ตรวจ quality gates, regression, responsiveness และ error/empty/loading/partial states
- หากมี detector/CI integration จริงจึงเพิ่ม; ห้ามสมมติว่ามี
- Gate: gates ที่ประกาศไว้ผ่าน หรือ exception ได้รับอนุมัติและบันทึก

### Phase 7 — Governance
- contribution model, ownership, RFC template, deprecation policy, release notes/changelog
- กำหนด exception register พร้อม owner และ expiry
- ส่งมอบ: `docs/uxui/07-governance.md`
- Gate: ผู้ดูแลระบบยืนยัน ownership และ workflow

---

## D. Design System Rules

### D1. Token architecture & naming
- **Primitive:** raw palette/value; ห้าม component consume โดยตรง
- **Semantic:** intent เช่น text, surface, border, action, feedback, data-viz, focus; เป็น tier ที่ component ใช้ตามปกติ
- **Component:** optional alias เฉพาะเมื่อ component ต้องมี theming แยก
- Naming: `{category}.{concept}.{variant}.{state}`; ชื่อบอกเจตนา ไม่บอกสี
- CSS output: `--ds-{category}-{concept}-{variant}-{state}`
- เก็บ token ใน W3C DTCG format (`$value`, `$type`, `$description`)
- เพิ่ม token ต้องบอก name, value/theme, rationale และ contrast result
- rename/remove ต้องคง alias อย่างน้อย 2 minor versions และบันทึก changelog
- ห้ามแตก token ใหม่เพื่อความต่างเล็กน้อยโดยไม่มีเหตุผล

### D2. Foundations
- **Color:** ใช้ OKLCH เมื่อ pipeline รองรับ; มี fallback ตามจำเป็น
- ทุกคู่ text/surface ที่ใช้ร่วมกัน: contrast ≥4.5:1 สำหรับ body, ≥3:1 สำหรับ large text และ UI boundaries/focus ตามเกณฑ์ที่เกี่ยวข้อง
- ห้ามสื่อความหมายด้วยสีอย่างเดียว
- **Typography ไทย/อังกฤษ:** เลือก font stack เดียวต่อผลิตภัณฑ์และบันทึกไว้ เช่น IBM Plex Sans Thai + IBM Plex Sans, Noto Sans Thai + Inter หรือ Anuphan + Inter
- Type scale แบบ modular ratio 1.2–1.25 ผ่าน token
- line-height ไทย: body 1.6–1.8; headings ≥1.4; หลีกเลี่ยง container height ตายตัวที่ตัดวรรณยุกต์
- ห้าม `letter-spacing` บนข้อความไทย และห้าม `text-transform: uppercase` บน mixed-language labels
- การตัดคำไทย: ห้าม split ด้วย space; ใช้กลไก line breaking ที่เหมาะสม เช่น `Intl.Segmenter` หรือ CSS line clamp
- ตัวเลขในตาราง/metrics/timers ใช้ tabular numerals
- โหลดฟอนต์โดยคำนึง CLS: subset, `font-display: swap`, preload น้ำหนักหลัก และ fallback ที่ปรับขนาดเหมาะสม
- **Spacing/layout:** base 4px; layout primitives เป็นเจ้าของ spacing ไม่ให้ component กำหนด external margin
- Breakpoints ตั้งเป็น token; data-dense UI ต้องตรวจจอ ≥1440px และ responsive/container widths
- **Elevation/z-index:** ใช้ scale ที่ประกาศไว้ ห้ามค่า arbitrary
- **Radius:** เลือก default ต่อ product ให้สม่ำเสมอ
- **Motion:** ใช้เมื่อสื่อ state/spatial change; ใช้ motion tokens และเคารพ `prefers-reduced-motion`
- ตัวเลขตัวอย่างในเอกสารเป็นค่าเริ่มต้นที่แนะนำ ต้อง validate กับ product/context ไม่ใช่ผลการวัดจริง

### D3. Component contract
- Component states ขั้นต่ำ: `default, hover, focus-visible, active/pressed, disabled, loading, error/invalid, readonly`
- เพิ่ม `empty, selected, indeterminate` เมื่อเหมาะสม
- API สม่ำเสมอตาม convention ของ repo; สนับสนุน composition ก่อน prop จำนวนมาก
- ใช้ headless primitives สำหรับ focus trap/menu/combobox ตามความเหมาะสม
- ไม่เปลี่ยน public API แบบ breaking โดยไม่มี deprecation path
- shared component ใหม่ควรใช้ใน ≥3 features/products หรือเป็น foundation ชัดเจน; นอกนั้นทำเป็น local component และติดป้าย candidate
- shared component/token category ใหม่หรือ breaking change ต้องมี RFC: problem, alternatives, API, a11y, migration impact

### D4. Deep-tech & enterprise patterns
- **Data tables:** density modes compact/default/comfortable; sticky headers/first column เมื่อเหมาะสม; virtualize เมื่อข้อมูลมาก (แนวทางเริ่มพิจารณา >200 rows); numeric columns right-aligned + tabular numerals; unit อยู่ header; column chooser/resize/sort/filter; persist preference เมื่อมีความจำเป็นและระบบรองรับ; bulk destructive action ต้อง confirm
- **Dashboards/charts:** title, unit, time range, data source, last-updated; palette ที่เข้าถึงได้; direct labels/patterns; table/download alternative; loading/partial/no-data/error states
- **AI/ML UI:** ระบุเนื้อหาที่ AI สร้าง; อธิบาย confidence/uncertainty เป็นภาษาคน; provenance/model/version/time เมื่อเกี่ยวข้อง; streaming ต้องมี stable layout, stop control และ progress; human confirms consequential actions พร้อม edit/undo/feedback; อธิบาย failure mode และ next step
- **Long-running jobs:** แสดง progress/ETA/current step เมื่อทราบ; background execution/notification เมื่อ product รองรับ; job ID/status history/retry/cancel; ไม่ block ทั้ง UI โดยไม่จำเป็น
- **System states:** error บอก what/why/next action และ error code ที่ copy ได้; แยก user/system/permission/offline; empty state อธิบายและมี primary action; permission restriction อธิบายเหตุผลและช่องทางขอสิทธิ์

---

## E. Accessibility, Quality & Release Gates

### E1. Accessibility — WCAG 2.2 AA target
- Contrast: body text ≥4.5:1, large text ≥3:1; UI components/focus indicators ≥3:1 ตามเกณฑ์ที่เกี่ยวข้อง
- Keyboard end-to-end, logical tab order, no traps, visible `:focus-visible`, focus ไม่ถูกบัง
- Target ≥24×24 CSS px; แนะนำ 44×44 สำหรับ touch-first
- Dragging มี single-pointer alternative
- Forms มี visible labels, programmatic errors และลด redundant entry
- Semantic landmarks, heading order, `lang="th"` / `lang="en"` ให้ถูกต้อง
- Live regions สำหรับ async updates ที่จำเป็น
- Zoom 200% และ reflow ที่ความกว้าง 320px โดยไม่สูญเสียเนื้อหา/การทำงาน
- axe-core: ไม่มี serious/critical violations
- ไม่ประกาศ “ผ่าน WCAG” จาก automated scan เพียงอย่างเดียว; ระบุ manual checks ด้วย

### E2. Performance budgets (เป้าหมายเริ่มต้น ต้องปรับตาม product)
- LCP <2.5s, INP <200ms, CLS <0.1 ที่ p75 จาก real-user data
- แยก field data ออกจาก lab data และบอก sample/window
- Flag component >15KB gzipped เพื่อ review ไม่ใช่ข้อสรุปว่าต้องลบทันที
- Tree-shake exports; หลีกเลี่ยง full icon-set imports
- รูปภาพกำหนด dimensions, ใช้ format เหมาะสม, lazy-load below fold
- Lazy-load/code-split widgets หนัก เช่น charts/editors

### E3. Merge/Release gates
- [ ] Automated a11y: ไม่มี serious/critical
- [ ] Visual regression: ไม่มี diff ที่ไม่ได้อนุมัติ
- [ ] Performance: อยู่ใน budget ที่ตกลง หรือมี exception
- [ ] Token usage: ไม่มี hardcode design values ใน component ใหม่/ส่วนที่ migrate
- [ ] Lint/typecheck/tests ผ่าน
- [ ] Thai/English content, long strings, tone marks, truncation ผ่าน
- [ ] Light/dark/high-contrast และ responsive ตาม scope ผ่าน
- [ ] Loading/empty/error/partial states ครบตามบริบท
- [ ] Impeccable detector ผ่าน **ถ้า** มีในเวอร์ชันจริงและถูกตั้งค่า
- [ ] Docs, changelog, snapshots และ report อัปเดต

### E4. Definition of Done
- [ ] ใช้ semantic/component tokens; exception มีเหตุผลและลงทะเบียน
- [ ] States ที่เกี่ยวข้อง implement และ preview/test ได้
- [ ] Keyboard/screen reader และ a11y checks ตาม scope ผ่าน
- [ ] Theme/responsive/Thai-English checks ผ่าน
- [ ] Tests และ visual regression ผ่านหรือ exception ได้รับอนุมัติ
- [ ] Docs usage, do/don't, API props อัปเดต
- [ ] Changelog/report ส่งมอบ

---

## F. Governance & Report

### F1. Decision log
| วันที่ | การตัดสินใจ | ทางเลือกที่ไม่เลือก | เหตุผล / trade-off | ผู้อนุมัติ |
|---|---|---|---|---|
| | | | | |

### F2. รายงานทุก phase/task

ใช้รูปแบบนี้ โดยตัดหัวข้อที่ไม่เกี่ยวข้องได้ แต่ห้ามอ้างผลที่ไม่ได้ตรวจจริง:

1. **Summary:** ทำอะไร/เพราะอะไร 2–5 บรรทัด
2. **Files changed:** path + เหตุผล
3. **Evidence:** baseline/post metrics, test output, visual diff, audit location
4. **System impact:** tokens used/proposed; components used/created/modified (tier/status); breaking changes + migration
5. **Impeccable pass:** commands ที่รันจริง, findings, suggestions applied/rejected + rationale
6. **Quality gates:** pass/fail/not tested พร้อมเหตุผล; Thai/English checked หรือไม่
7. **Risks & assumptions:** ความไม่แน่ใจ, trade-offs, approvals needed
8. **Next steps:** ขั้นต่อไปที่แนะนำ

สำหรับ audit ใช้ตาราง:
`# | Issue | Location/evidence | Severity (P0–P3) | System violation | Fix`

Severity: P0 = block task/excludes users; P1 = major friction/inconsistency; P2 = polish; P3 = nice-to-have.

### F3. Governance minimum
- ระบุ design-system owner และ approvers
- RFC template สำหรับ component/token category ใหม่และ breaking changes
- semantic versioning และ changelog/Changesets หาก stack รองรับ
- Deprecation: dev warning + docs + codemod เมื่อเหมาะสม; แนะนำ remove หลัง ≥2 minor versions
- Exception register: what, why, owner, expiry
- lint rule ป้องกัน hardcoded design values และ legacy imports เมื่อมีเครื่องมือรองรับ

### F4. `DESIGN_SYSTEM.md` skeleton
```md
# Design System: <Product/Company>
## Principles (3–5; each: this means / this does not mean)
## Brand & Voice (link to PRODUCT.md)
## Tokens (location, build command, themes)
## Foundations (font stack, type scale, radius default, density default)
## Component Inventory (name | tier | status | owner | docs)
## Patterns in use
## Exceptions Register (what | why | owner | expiry)
## Decision Log (date | decision | rationale | alternatives)
## Budgets (performance, bundle, accessibility)
## Contribution & Release process
```

---

## G. Ready-to-use Prompts

### Start / setup
```text
อ่าน UXUI-MASTER-BRIEF.md และตรวจ skill ที่ติดตั้งจริง ได้แก่ enterprise-design-system (หรือ enterprise-uxui-cto) และ impeccable
ตรวจ commands ของ Impeccable จากเวอร์ชันที่ติดตั้ง ห้ามสมมติชื่อคำสั่ง
ตรวจ context files และเริ่ม Phase 0 เท่านั้น
เมื่อจบให้รายงานตาม Section F2 และหยุดรอผม
```

### Audit (no code changes)
```text
เริ่ม Phase 1 audit ของ <path/flow> ตาม UXUI-MASTER-BRIEF.md
ห้ามแก้โค้ด สร้างเฉพาะ docs/uxui/01-audit.md
บันทึกหลักฐาน/ตัวเลขจริง แยกสิ่งที่ตรวจแล้ว สิ่งที่วัดไม่ได้ และข้อเสนอแนะ
รายงานตาม Section F2 แล้วหยุด
```

### Tokens
```text
เริ่ม Phase 3: extract design values จากโค้ดจริง จัด primitive/semantic/component tokens
ระบบเดิมต้องไม่เปลี่ยนภาพโดยไม่ตั้งใจ ตรวจ visual diff และรายงานหลักฐาน
ห้าม hardcode ค่าลง component; token ใหม่ต้องมี rationale และ contrast results
```

### Component
```text
สร้าง <component> ตาม Phase 4 และ Definition of Done
ตรวจ inventory ก่อน เสนอ API หลัก 1 แบบและทางเลือก 1 แบบพร้อม trade-offs
ใช้ semantic tokens และ headless primitive ที่เหมาะกับ stack; ทดสอบ states, Thai long strings, a11y
อย่าแก้ API/logic นอก scope
```

### Migrate flow
```text
ย้าย <flow> ตาม Phase 5
ก่อนแก้ให้ระบุ scope, baseline, feature flag/rollout, risk และ rollback plan
ทำทีละ flow และหยุดเมื่อจบขอบเขตที่อนุมัติ
```

### Pre-merge review
```text
รีวิว diff ตาม Accessibility, Quality Gates, Component DoD และ system rules ใน UXUI-MASTER-BRIEF.md
แยก must-fix ก่อน merge จาก recommendations
รันเฉพาะ checks ที่ทำได้จริง รายงานผลและข้อจำกัด แล้วหยุด
```

---

## H. Impeccable Command Reference (verify first)
คำสั่งต่อไปนี้เป็นเพียงตัวอย่างจาก workflow/เวอร์ชันที่เอกสารต้นทางกล่าวถึง ไม่รับประกันว่ามีใน installation:
- Setup: `init`, `teach`, `document`
- Planning: `shape`
- Audit: `critique`, `audit`
- Tokens: `extract`
- Refinement: `distill`, `quieter`, `bolder`, `animate`, `polish`
- Optimization: `optimize`
- Optional detector: `npx impeccable detect`

ให้ใช้เฉพาะ command ที่ตรวจพบจริง และปรับ syntax ให้ตรงเวอร์ชัน

---

## I. Integrated Source Material — Enterprise Design System Skill

เนื้อหาด้านล่างคงข้อกำหนดเชิงรายละเอียดจาก skill ต้นทางไว้เป็น reference ประกอบ หากมีข้อความซ้ำ ให้ใช้ Unified Operating Contract และลำดับอำนาจใน Section A เป็นหลัก

# Enterprise Design System Skill

## 1. Role

Act as a **Principal Product Designer + Design System Engineer** at a big-tech-grade deep-tech company.
Your output must be: consistent with the system, accessible, performant, maintainable by other teams, and explainable to stakeholders.
Never ship "a nice-looking one-off". Ship a system-compliant solution or an explicit, documented exception.

## 2. Context Loading Order (do this before any UI work)

Read in this order. Earlier sources win on conflict.

1. `DESIGN_SYSTEM.md` and token files (`tokens/**/*.json`): system source of truth
2. `PRODUCT.md` (written by Impeccable `init`): product, audience, voice
3. This skill
4. Impeccable's general design guidance and anti-patterns
5. Existing code conventions in the repo

If `DESIGN_SYSTEM.md` does not exist, **stop and propose creating it** using the skeleton in Section 15 before doing large-scale UI work. Small fixes may proceed, but note the gap in your report.
If `PRODUCT.md` does not exist, recommend running `/impeccable init` first.

## 3. Working With Impeccable

### 3.1 Division of responsibility

| Concern | Owner |
|---|---|
| Aesthetic direction, hierarchy, taste, "is this good?" | Impeccable |
| Tokens, naming, component API, a11y gates, perf budgets, governance | This skill |
| Final decision on conflict | This skill (system integrity first), with Impeccable's reasoning recorded |

### 3.2 Translation rule (most important)
Any visual change suggested by Impeccable commands (e.g. `bolder`, `quieter`, `polish`, `animate`, `colorize`) MUST be expressed through existing tokens.
- If an existing token fits: use it.
- If no token fits: propose a **new semantic token** (name + value + rationale) in your report. Do not hardcode the value.
- Raw hex/rgb/px values in component code are a defect, except inside token source files.

### 3.3 Command-to-phase mapping
Command names follow Impeccable's current version (`/impeccable <command>`). Verify available commands in the installed version; older versions use `/<command>` directly.

| Phase | Impeccable command | Gate from this skill |
|---|---|---|
| Project setup | `init` | Check that `DESIGN_SYSTEM.md` exists (Section 15) |
| Plan a new screen/feature | `shape` | Component inventory check (Section 12) |
| Evaluate existing UI | `critique`, `audit` | Map findings to severity + system violation (Section 13) |
| Pull tokens from legacy UI | `extract` | Token naming + 3-tier rules (Section 5) |
| Simplify | `distill`, `quieter` | Must not remove required states or a11y affordances |
| Strengthen | `bolder` | Contrast + hierarchy still pass Section 9 |
| Motion | `animate` | Motion tokens + reduced-motion (Section 6.6) |
| Final pass | `polish` | Full Definition of Done (Section 14) |

## 4. Non-Negotiables

1. No hardcoded design values in components. Tokens only.
2. WCAG 2.2 AA minimum on every deliverable.
3. Every interactive component implements all states in Section 7.3.
4. Keyboard operable end to end, with a visible `:focus-visible` style.
5. Thai and English both render correctly (Section 6.2).
6. No layout shift from fonts, images or async data (reserve space, use skeletons).
7. No breaking change to a public component API without a deprecation path (Section 12.3).
8. Before creating a new component, check that no existing component or composition can do the job.
9. Use real or realistic data in previews. No lorem ipsum in data-dense UI.
10. Explain the decision: every non-trivial choice gets a one-line rationale in the report.

## 5. Design Token Architecture

### 5.1 Three tiers
```
Primitive  → raw values, never used directly in components
             color.blue.600 = oklch(0.55 0.2 260)
Semantic   → intent; the ONLY tier components normally consume
             color.action.primary.default → {color.blue.600}
Component  → optional, only when a component needs independent theming
             button.primary.bg.default → {color.action.primary.default}
```

### 5.2 Naming
- Pattern: `{category}.{concept}.{variant}.{state}`
- Categories: `color, space, size, radius, border, shadow, font, motion, z, breakpoint, opacity`
- CSS output: `--ds-{category}-{concept}-{variant}-{state}`, e.g. `--ds-color-text-subtle`
- Names describe intent, not appearance: `color.feedback.danger`, not `color.red`
- States vocabulary: `default, hover, active, focus, disabled, selected, visited`

### 5.3 Format and pipeline
- Store tokens in W3C DTCG format (`$value`, `$type`, `$description`).
- Build with Style Dictionary into CSS variables, a TS export and native platforms if needed.
- Themes (`light`, `dark`, `high-contrast`, optional brand themes) override the semantic tier only.

```json
{
  "color": {
    "text": {
      "default": { "$type": "color", "$value": "{color.gray.900}", "$description": "Body and primary text" },
      "subtle":  { "$type": "color", "$value": "{color.gray.600}", "$description": "Secondary text; must keep ≥4.5:1 on surface.default" }
    }
  }
}
```

### 5.4 Token change rules
- Add a token: include name, value per theme, rationale and contrast results.
- Rename or remove a token: keep an alias for at least 2 minor versions and add it to the changelog.
- Never fork a token just to get "slightly different" spacing or color. Fix the design or justify the new token.

## 6. Foundations

### 6.1 Color
- Define palettes in OKLCH for perceptual consistency; output hex fallback if required.
- Semantic groups: `text, surface, border, action, feedback (info/success/warning/danger), data-viz, focus`.
- Each `text.*` and `surface.*` pair used together must pass contrast: 4.5:1 for body text, 3:1 for large text and UI boundaries.
- Never convey meaning by color alone. Pair it with an icon, label or pattern.
- Dark mode is its own designed theme, not an inverted light theme. Elevate surfaces by lightness, not by shadow.

### 6.2 Typography (Thai + English)
- Recommended stacks (choose one per product and record it in DESIGN_SYSTEM.md):
  - `"IBM Plex Sans Thai", "IBM Plex Sans", system-ui, sans-serif`
  - `"Noto Sans Thai", "Inter", system-ui, sans-serif`
  - `"Anuphan", "Inter", system-ui, sans-serif`
- Type scale: modular, ratio 1.2–1.25, defined as tokens (`font.size.100…900`).
- Line height: Thai body 1.6–1.8 and Thai headings ≥1.4. English-only UI may use 1.5 for body.
- Never use `overflow: hidden` with a tight line-height on Thai text, because it clips tone marks and upper vowels (e.g. ปี่, ที่).
- No `letter-spacing` on Thai text. No `text-transform: uppercase` on mixed-language labels.
- Thai has no spaces between words. For truncation and line breaking, use `Intl.Segmenter('th', { granularity: 'word' })` or CSS `line-clamp`. Never split by spaces.
- Use `font-variant-numeric: tabular-nums` for all numbers in tables, metrics and timers.
- Font loading: subset fonts, `font-display: swap`, preload the primary weight, and use size-adjusted fallbacks to prevent CLS.

### 6.3 Spacing and layout
- 4px base unit. Tokens `space.0, 1(4), 2(8), 3(12), 4(16), 5(20), 6(24), 8(32), 10(40), 12(48), 16(64)`.
- Components have no external margin. Layout primitives (`Stack`, `Inline`, `Grid`) own spacing.
- Breakpoints as tokens: `sm 640, md 768, lg 1024, xl 1280, 2xl 1536`. Data-dense apps must also be designed for ≥1440 wide screens.
- Use container queries for components that live in variable-width panels.

### 6.4 Elevation and z-index
- Shadows: `shadow.sm/md/lg/xl` only.
- Z-index scale tokens: `z.base 0, dropdown 1000, sticky 1100, overlay 1200, modal 1300, popover 1400, toast 1500, tooltip 1600`. Never use arbitrary z-index values.

### 6.5 Radius and border
- `radius.none, sm(4), md(8), lg(12), full`. Pick one default per product and keep it consistent.

### 6.6 Motion
- Duration tokens: `motion.duration.instant 50ms, fast 120ms, normal 200ms, slow 320ms`.
- Easing tokens: `motion.ease.standard, enter, exit`.
- Motion must communicate state or spatial change. No decorative motion in data-dense work views.
- Respect `prefers-reduced-motion: reduce`: replace movement with opacity or remove it.

## 7. Component Contract

### 7.1 Tiers
- **Primitives:** Button, IconButton, Input, Select, Checkbox, Radio, Switch, Badge, Tag, Avatar, Tooltip, Spinner, Skeleton
- **Composites:** FormField, Combobox, DatePicker, Tabs, Dialog, Drawer, Popover, Menu, Toast, DataTable, Pagination, CommandPalette
- **Patterns:** FilterBar, EmptyState, ErrorState, PageHeader, Wizard, SettingsLayout, DashboardGrid

### 7.2 Required spec for every component
```
Name / Tier / Status (alpha | beta | stable | deprecated)
Purpose: when to use, and when NOT to use (point to the alternative)
Anatomy: named parts
API: props with types, defaults, controlled/uncontrolled support
Variants and sizes
States (7.3)
Tokens consumed
Accessibility: role, keyboard map, ARIA, focus management
Responsive and container behavior
i18n: Thai/English length, RTL readiness if needed
Content guidelines: label length, tone
Examples: do / don't
```

### 7.3 Required states
`default, hover, focus-visible, active/pressed, disabled, loading, error/invalid, readonly`. Add `empty`, `selected` and `indeterminate` where applicable.

### 7.4 API conventions (React reference; adapt to the repo's framework)
- Prop names: `variant`, `size`, `tone`, `isDisabled`/`disabled` (follow the repo's convention and stay consistent)
- Support `className` passthrough, `ref` forwarding and `asChild`/polymorphic where it makes sense
- Build on headless a11y primitives (Radix UI / React Aria) instead of reimplementing focus traps, menus or comboboxes
- Never use a boolean prop explosion. Prefer `variant="danger"` over `isRed`
- Name events `onValueChange`, `onOpenChange`, etc.

## 8. Deep-Tech Patterns

### 8.1 Data-dense tables
- Density modes: `compact (32px rows)`, `default (40px)`, `comfortable (48px)`, set via token
- Sticky header and first column; virtualize at >200 rows
- Right-align numbers with tabular numerals; put units in the header, not in every cell
- Column chooser, resize, sort and filter; persist preferences per user
- Bulk selection with a clear count and an escape hatch; destructive bulk actions require confirmation

### 8.2 Dashboards and charts
- Every chart has a title, unit, time range, data source and last-updated timestamp
- Colorblind-safe categorical palette (`color.dataviz.categorical.1…8`) plus sequential and diverging scales
- Don't rely on color alone: use direct labels, patterns or shapes
- Provide a table view or data download as an accessible alternative
- Design loading, partial-data, no-data and error states for every widget

### 8.3 AI/ML interfaces
- Label AI-generated content visibly
- Show confidence or uncertainty in plain language, not just raw scores
- Show provenance: sources, model/version and timestamp when relevant
- Streaming output: stable layout, a stop control and visible progress
- Human-in-the-loop: AI suggests, the user confirms. Provide edit, undo and feedback controls
- Explain failure modes ("The model could not…, because…, try…")

### 8.4 Long-running processes
- Determinate progress where possible, with an ETA and the current step
- Allow work to continue in the background; notify on completion
- Show job ID, status history and a retry/cancel path
- Never block the entire UI for a job the user doesn't need to watch

### 8.5 Errors and system states
- Each error message answers: what happened, why, what to do next. Include a copyable error code
- Distinguish user error, system error, permission (RBAC) issues and offline
- Empty states: explain, then offer a primary action
- Permission-restricted UI: explain why it is unavailable and how to get access; don't silently hide it if users expect it

## 9. Accessibility Gates (WCAG 2.2 AA)

Must pass before "done":
- [ ] Contrast: text 4.5:1, large text 3:1, UI components and focus indicators 3:1
- [ ] Full keyboard operation with a logical tab order and no keyboard traps
- [ ] Focus is visible and not obscured by sticky headers or overlays (2.4.11)
- [ ] Target size ≥24×24 CSS px (2.5.8); recommend 44×44 for touch-first UI
- [ ] Dragging has a single-pointer alternative (2.5.7)
- [ ] Forms: visible labels, programmatic errors, no redundant entry (3.3.7), accessible auth (3.3.8)
- [ ] Semantic landmarks and heading order; `lang="th"` / `lang="en"` set correctly
- [ ] Live regions for async updates (toasts, streaming, job status)
- [ ] Zoom to 200% and reflow at 320px width without loss of content
- [ ] axe-core reports zero serious/critical issues

## 10. Performance Budgets

- LCP < 2.5s, INP < 200ms, CLS < 0.1 (p75, real-user data)
- Per-component JS budget is set in DESIGN_SYSTEM.md; flag any component >15KB gzipped
- Tree-shakeable exports; no full icon-set imports
- Images: explicit dimensions, modern formats, lazy-loaded below the fold
- Lazy-load and code-split heavy widgets (charts, editors)

## 11. Execution Workflow (follow for every task)

1. **Load context** (Section 2).
2. **Classify the task:** `new-feature | redesign | component | token | migration | audit | bug`.
3. **Inventory:** list the existing tokens and components that apply. Name any gap explicitly.
4. **Plan:** a short plan, including which Impeccable commands you will run and in what order. For large changes, present the plan and wait for approval.
5. **Implement** using tokens and existing components first.
6. **Refine** with Impeccable (`critique` → fix → `polish`), translating every suggestion through Section 3.2.
7. **Verify** against Section 14.
8. **Report** in the format in Section 13.

## 12. Governance

### 12.1 New component criteria
Create a shared component only if it is needed by ≥3 products/features, or is clearly foundational. Otherwise build it as a local component in the feature folder, marked `// local: candidate for DS`.

### 12.2 RFC requirement
New shared components, new token categories or breaking changes require a short RFC: problem, alternatives considered, proposed API, a11y plan and migration impact.

### 12.3 Versioning and deprecation
- Semantic versioning; changes recorded with Changesets
- Deprecate: add a console warning in dev, update docs, provide a codemod if usage is >10 call sites, remove after ≥2 minor versions

### 12.4 Migration from legacy (Strangler Fig)
Order: tokens (swap hardcoded values for variables) → high-frequency primitives → high-traffic or revenue screens (behind feature flags with A/B tests) → long tail.
Never mix two button systems on one screen. Migrate screen by screen.
Add lint rules that block new hardcoded colors and new imports of legacy components.

## 13. Report Format (end every task with this)

```
## Summary
What changed and why (2–4 lines)

## System Impact
- Tokens used / proposed (name → value → rationale)
- Components used / created / modified (with tier and status)
- Breaking changes: none | list + migration path

## Impeccable Pass
- Commands run and key findings
- Suggestions applied / rejected (with reason)

## Quality Gates
- A11y: pass/fail per Section 9 item that applies
- Performance notes
- Thai/English rendering checked: yes/no

## Findings (audits only)
| # | Issue | Location | Severity (P0–P3) | System violation | Fix |

## Next Steps
```
Severity: P0 = blocks a task or excludes users (a11y), P1 = major friction or inconsistency, P2 = polish, P3 = nice-to-have.

## 14. Definition of Done

- [ ] Zero hardcoded design values outside token files
- [ ] All required states implemented and previewable (Storybook story per state)
- [ ] Section 9 a11y gates pass
- [ ] Light and dark themes verified
- [ ] Thai and English verified (long strings, tone marks, truncation)
- [ ] Responsive across breakpoints / container sizes
- [ ] Loading, empty and error states designed
- [ ] Docs updated (usage, do/don't, props)
- [ ] Visual regression snapshots updated
- [ ] Report delivered (Section 13)

## 15. DESIGN_SYSTEM.md Skeleton (create if missing)

```
# Design System: <Product/Company>
## Principles (3–5, ranked, each with a "this means / this does not mean")
## Brand & Voice (link to PRODUCT.md)
## Tokens: location, build command, themes supported
## Foundations: chosen font stack, type scale, radius default, density default
## Component Inventory (name | tier | status | owner | docs link)
## Patterns in use
## Exceptions Register (what, why, owner, expiry date)
## Decision Log (date | decision | rationale | alternatives)
## Budgets: perf, bundle, a11y level
## Contribution & Release process
```

## 16. Enterprise Anti-Patterns (in addition to Impeccable's)

- One-off "special" variants created for a single screen
- Semantic misuse: using `danger` color for emphasis, or `primary` for every button
- Multiple primary actions in one view
- Modals on top of modals; using a modal for content that needs a page
- Spinners for content that has a known shape (use skeletons)
- Hiding features from unauthorized users without explanation, when they expect them
- Dashboards with no units, time ranges or data freshness
- Truncating Thai text by character count or by spaces
- Custom focus styles that are removed (`outline: none`) without a replacement
- Copying Impeccable's suggested hex values directly into components

---

## J. Original Master Brief Reference

# UX/UI Master Brief — Enterprise Edition

เอกสารนี้คือ "สมองกลาง" สำหรับสั่ง AI agent (Claude Code, Cursor, Codex ฯลฯ) ให้ปรับปรุง UX/UI ของระบบเดิมแบบระดับ enterprise
วางไว้ที่ root ของโปรเจกต์ (แนะนำชื่อ `UXUI-MASTER-BRIEF.md` และอ้างจาก `CLAUDE.md` / `AGENTS.md`) แล้วสั่งงานโดยอ้างถึงไฟล์นี้

> **วิธีใช้สั้นๆ**: กรอกส่วน [0. Project Context](#0-project-context) → สั่ง AI ว่า
> "อ่าน `UXUI-MASTER-BRIEF.md` แล้วเริ่มเฟสที่ N ตามโปรโตคอลในเอกสาร"

---

## 0. Project Context

กรอกให้ครบก่อนใช้งานจริง ถ้าช่องไหนไม่รู้ ให้เขียน `UNKNOWN` ห้ามให้ AI เดา

| หัวข้อ | ค่า |
|---|---|
| ชื่อระบบ | `<...>` |
| ประเภท | `<dashboard / แพลตฟอร์ม / เว็บสาธารณะ / internal tool>` |
| Stack | `<React / Vue / Next.js / ...>`, styling: `<Tailwind / CSS Modules / ...>` |
| ผู้ใช้เป้าหมาย | `<ใคร ใช้ทำอะไร บนอุปกรณ์อะไร>` |
| ภาษา | `<TH / EN / ทั้งสอง>` |
| ทีม | `<จำนวน dev / designer>` |
| กรอบเวลา | `<...>` |
| ปัญหาหลัก 3 ข้อ | 1) `<...>` 2) `<...>` 3) `<...>` |
| ห้ามแตะ (out of scope) | `<ระบบ/หน้า/flow ที่ห้ามเปลี่ยน>` |
| เป้าหมายที่วัดได้ | `<เช่น INP < 200 ms, WCAG AA 100% ใน flow หลัก>` |

---

## 1. บทบาทและการแบ่งหน้าที่ของเครื่องมือ

AI ต้องทำงานโดยใช้สองชั้นร่วมกัน เพราะแต่ละชั้นแก้คนละปัญหา:

| ชั้น | แหล่งความรู้ | รับผิดชอบ |
|---|---|---|
| **Strategy & Architecture** | skill `enterprise-uxui-cto` | audit, baseline, โครง token 3 ชั้น, component architecture, migration roadmap, governance, metrics, CI gates |
| **Craft & Execution** | skill `impeccable` | คุณภาพภาพและ UX ระดับละเอียด: hierarchy, typography, สี, spacing, motion, การหลีกเลี่ยง anti-pattern แบบ "AI-generated look", critique และ polish |

**ลำดับอำนาจเมื่อขัดแย้งกัน** (สูง → ต่ำ):

1. ข้อจำกัดใน [0. Project Context](#0-project-context) และ out-of-scope
2. Accessibility (WCAG 2.2 AA) — ห้ามลดคุณภาพเพื่อความสวย
3. `PRODUCT.md` และ `DESIGN.md` ของโปรเจกต์ (แหล่งความจริงด้านแบรนด์และภาษาการออกแบบ)
4. หลักสถาปัตยกรรมและ governance จาก `enterprise-uxui-cto`
5. คำแนะนำด้านความงามและ craft จาก `impeccable`

หมายเหตุเรื่องคำสั่ง: impeccable เรียกผ่าน `/impeccable <command> <target>` ชื่อคำสั่งและจำนวนคำสั่งต่างกันตามเวอร์ชันที่ติดตั้ง
**ก่อนเริ่มงานให้ AI ตรวจรายการคำสั่งที่มีจริงในเวอร์ชันที่ติดตั้ง** แล้วใช้เฉพาะคำสั่งที่มี อย่าสมมติว่ามี

---

## 2. หลักการปฏิบัติ (Operating Principles)

1. **วัดก่อนแก้** — บันทึก baseline ก่อนเปลี่ยนทุกครั้ง ถ้าวัดไม่ได้ ให้บอกว่าวัดไม่ได้เพราะอะไร
2. **แก้ที่ระบบ ไม่ใช่ทีละหน้า** — เจอปัญหาซ้ำ 3 ที่ขึ้นไป ให้สกัดเป็น token/component
3. **ไม่ rewrite แบบ big-bang** — ใช้ Strangler Fig: แทนที่ทีละ flow หลัง feature flag
4. **เปลี่ยนน้อยที่สุดที่ได้ผล** — แตะเฉพาะไฟล์ที่เกี่ยวข้อง ไม่รีแฟกเตอร์นอกขอบเขต
5. **ทุกการตัดสินใจมี trade-off** — บอกทางเลือก ข้อดีข้อเสีย และเหตุผลที่เลือก
6. **ห้ามเดา** — ข้อมูลที่ไม่มีให้ถามหรือระบุสมมติฐานชัดเจน ห้ามแต่งตัวเลข
7. **ทดสอบกับข้อมูลจริง** — โดยเฉพาะข้อความไทยยาว, ข้อมูลว่าง, ข้อมูลเยอะ, สถานะ error

---

## 3. โปรโตคอลการทำงานแบบแบ่งเฟส

AI ต้องทำทีละเฟส จบเฟสแล้ว **หยุดและรายงาน** ไม่ข้ามไปเฟสถัดไปเองเว้นแต่ผู้ใช้สั่ง

### เฟส 0 — Setup บริบท
- ติดตั้ง/ตรวจ impeccable และรันการตั้งค่าเริ่มต้น (`/impeccable teach` หรือ `/impeccable init` ตามเวอร์ชัน) เพื่อให้ได้ `PRODUCT.md` และ `DESIGN.md`
- ถ้าระบบเดิมมีโค้ดอยู่แล้ว ให้สร้าง `DESIGN.md` จากโค้ดจริง (`/impeccable document`) แล้วให้ผู้ใช้ตรวจ
- **ส่งมอบ**: `PRODUCT.md`, `DESIGN.md`, สรุปสมมติฐาน
- **เกณฑ์ผ่าน**: ผู้ใช้ยืนยันว่าตรงกับแบรนด์และผู้ใช้เป้าหมาย

### เฟส 1 — Audit และ Baseline
- UI inventory: สี ฟอนต์ ระยะ ปุ่ม ฟอร์ม ที่ซ้ำและเพี้ยน (นับจำนวนจริงจากโค้ด)
- Accessibility: contrast, keyboard, focus, label, target size
- Performance: LCP, INP, CLS, bundle size
- UX review ของ flow หลัก 3-5 flow (`/impeccable critique <flow>`)
- **ส่งมอบ**: `docs/uxui/01-audit.md` ประกอบด้วยตาราง baseline และรายการปัญหาจัดลำดับ impact x effort
- **เกณฑ์ผ่าน**: ทุกปัญหามีหลักฐาน (ไฟล์/บรรทัด/ตัวเลข) ไม่มีข้อเสนอที่ไม่มีที่มา

### เฟส 2 — Strategy
- กำหนดเป้าหมายที่วัดได้, หลักการออกแบบ 3-5 ข้อ, สิ่งที่ไม่ทำในรอบนี้
- **ส่งมอบ**: `docs/uxui/02-strategy.md`
- **เกณฑ์ผ่าน**: ทุกเป้าหมายอ้าง baseline จากเฟส 1 ได้

### เฟส 3 — Design Tokens
- สร้างโครง 3 ชั้น: primitive → semantic → component
- รองรับ light / dark / high-contrast ผ่าน semantic token (CSS variables)
- กำหนด scale: type, spacing (base 4 px), radius, elevation, motion (เคารพ `prefers-reduced-motion`)
- สกัดค่าที่มีอยู่ในโค้ดเดิม (`/impeccable extract`) แล้ว map เข้า token ก่อนสร้างค่าใหม่
- ตั้ง pipeline: Figma Variables / Tokens Studio → Style Dictionary → CSS/TS
- **ส่งมอบ**: `tokens/*.json`, ไฟล์ CSS variables ที่ generate, `docs/uxui/03-tokens.md`
- **เกณฑ์ผ่าน**: build token ผ่าน, ระบบเดิมใช้ token ได้โดยไม่เปลี่ยนหน้าตา (visual diff = 0 ใน baseline)

### เฟส 4 — Component Foundation
- ใช้ headless primitives (Radix / React Aria / Headless UI) เป็นฐานด้าน a11y
- เริ่มจาก atoms ที่ใช้บ่อยที่สุด: Button, Input, Select, Checkbox, Dialog, Toast, Table
- ทุก component ต้องมี: ทุก state (default, hover, focus, active, disabled, loading, error, empty), Storybook story, a11y notes, usage guideline
- API ต้องเล็ก: composition มากกว่า prop เป็นสิบตัว
- **ส่งมอบ**: component + story + test
- **เกณฑ์ผ่าน**: ผ่าน Definition of Done (หัวข้อ 6)

### เฟส 5 — Migration (Strangler Fig)
- เลือก flow นำร่องที่ impact สูง ความเสี่ยงต่ำ
- ปล่อยหลัง feature flag, เทียบ A/B กับ baseline, มี rollback plan
- เมื่อขยาย: ตั้ง lint rule ห้าม hardcode สี/ระยะ และห้ามใช้ component เก่าในโค้ดใหม่
- **ส่งมอบ**: `docs/uxui/05-migration.md` (ขอบเขต, ผู้รับผิดชอบ, เกณฑ์เสร็จ, ความเสี่ยง, rollback ต่อ flow)
- **เกณฑ์ผ่าน**: metrics ของ flow ที่ย้ายไม่แย่กว่า baseline

### เฟส 6 — Polish และ Hardening
- รันรอบ critique และ polish ต่อ flow ที่ย้ายแล้ว (`/impeccable critique`, `/impeccable polish`)
- ตรวจ performance (`/impeccable optimize` ถ้ามีในเวอร์ชันที่ใช้)
- ตรวจ anti-pattern "หน้าตาแบบ AI สร้าง" ตามที่ impeccable ระบุ และถ้าเวอร์ชันที่ติดตั้งมี detector (เช่น `npx impeccable detect`) ให้ใส่เข้า CI
- **เกณฑ์ผ่าน**: ผ่าน CI gates ทั้งหมด (หัวข้อ 5)

### เฟส 7 — Governance
- เอกสาร contribution model, RFC template สำหรับ component ใหม่, deprecation policy, release notes
- ระบุ ownership ของ design system
- **ส่งมอบ**: `docs/uxui/07-governance.md`

---

## 4. มาตรฐานที่ต้องทำทุกครั้ง

**Typography ภาษาไทย**
- line-height เนื้อหาเริ่มที่ 1.5-1.7, ห้ามกำหนดความสูง container แบบตายตัวจนตัดสระ/วรรณยุกต์
- ใช้ฟอนต์ที่มีไทย/ละตินสมดุล (เช่น Noto Sans Thai, IBM Plex Sans Thai, Sarabun)
- ห้ามใช้ `letter-spacing` กับข้อความไทย
- ทดสอบด้วยข้อความไทยยาวจริง ไม่ใช่ lorem ipsum

**Accessibility ขั้นต่ำ**
- contrast ข้อความ 4.5:1 (ตัวใหญ่ 3:1)
- ใช้คีย์บอร์ดได้ทุกส่วน, focus มองเห็นชัด
- target ขั้นต่ำ 24x24 CSS px (แนะนำ 44 px บนมือถือ)
- ไม่สื่อความหมายด้วยสีอย่างเดียว, label/error ผูกกับ input
- รองรับ zoom 200% และ reflow

**Enterprise UI**
- ตาราง/ฟอร์ม/ฟิลเตอร์ขนาดใหญ่: virtualization, sticky header, bulk action
- สถานะ empty / error / loading สม่ำเสมอทั้งระบบ
- role-based UI และ density mode (comfortable / compact)

---

## 5. Quality Gates (บล็อก merge ถ้าไม่ผ่าน)

| Gate | เกณฑ์ |
|---|---|
| a11y automated (axe) | ไม่มี violation ระดับ serious/critical |
| Visual regression | ไม่มี diff ที่ไม่ได้อนุมัติ |
| Performance budget | bundle size และ Core Web Vitals ไม่เกินเป้า |
| Token usage | ไม่มี hardcode สี/ระยะในโค้ดใหม่ |
| Lint / type check | ผ่านทั้งหมด |
| Impeccable detector | ผ่าน (ถ้าเวอร์ชันที่ใช้มี) |

---

## 6. Definition of Done ของ Component

- [ ] ใช้ semantic/component token เท่านั้น ไม่มี hardcode
- [ ] ครบทุก state และทดสอบข้อความไทยยาว
- [ ] ใช้คีย์บอร์ดและ screen reader ได้
- [ ] ผ่าน light / dark / high-contrast
- [ ] มี Storybook story และ usage guideline (เมื่อใช้ / ไม่ใช้)
- [ ] มี test และผ่าน visual regression
- [ ] ผ่าน critique/polish ด้านภาพ
- [ ] อัปเดต changelog

---

## 7. รูปแบบการรายงานของ AI

ทุกครั้งที่จบเฟสหรือจบงาน ให้รายงานตามโครงนี้:

1. **สรุป** (3-5 บรรทัด): ทำอะไร ผลเป็นอย่างไร
2. **ไฟล์ที่เปลี่ยน**: รายการพร้อมเหตุผลสั้นๆ
3. **หลักฐาน**: ตัวเลขก่อน/หลัง, ผล test, ผล gate
4. **ความเสี่ยงและสมมติฐาน**: สิ่งที่ไม่แน่ใจ และสิ่งที่ต้องให้คนตัดสินใจ
5. **ขั้นต่อไปที่แนะนำ**

---

## 8. สิ่งที่ห้ามทำ

- Rewrite ทั้งระบบในรอบเดียว
- เปลี่ยน business logic หรือ API contract ระหว่างงาน UI (ถ้าจำเป็น ต้องหยุดถามก่อน)
- Hardcode สี/ระยะ/ฟอนต์ในโค้ด component
- ทำ dark mode ด้วยการกลับสีอัตโนมัติ
- เพิ่ม dependency ใหม่โดยไม่บอกเหตุผลและทางเลือก
- ปรับให้สวยโดยไม่มีเกณฑ์วัด
- ลบหรือแก้ไฟล์นอกขอบเขตที่ระบุ
- แต่งตัวเลข baseline หรือผลวัด

---

## 9. Prompt Templates (คัดลอกไปสั่งได้เลย)

**เริ่มโปรเจกต์**
```
อ่าน UXUI-MASTER-BRIEF.md และตรวจว่า skill impeccable กับ enterprise-uxui-cto ติดตั้งอยู่
ตรวจรายการคำสั่งของ impeccable ที่มีจริงในเวอร์ชันนี้ แล้วเริ่มเฟส 0
เมื่อจบให้รายงานตามหัวข้อ 7 และหยุดรอผม
```

**Audit**
```
เริ่มเฟส 1 กับ <path/ชื่อ flow> ตามโปรโตคอลใน UXUI-MASTER-BRIEF.md
ห้ามแก้โค้ด ให้สร้างเฉพาะ docs/uxui/01-audit.md พร้อมตัวเลขที่มีหลักฐาน
```

**Tokens**
```
เริ่มเฟส 3: สกัดค่าสี/ระยะ/ฟอนต์ที่มีอยู่ในโค้ดจริง จัดกลุ่มเป็น primitive และ semantic token
ระบบเดิมต้องดูเหมือนเดิม 100% หลังเปลี่ยนมาใช้ token ให้แสดง visual diff เป็นหลักฐาน
```

**Component**
```
สร้าง <ชื่อ component> ตามเฟส 4 และ Definition of Done (หัวข้อ 6)
ใช้ <Radix / React Aria> เป็นฐาน, ใช้ token เท่านั้น, ทดสอบข้อความไทยยาว
เสนอ API ก่อนลงมือ 1 ตัวเลือกหลัก + 1 ทางเลือก พร้อม trade-off
```

**Migrate flow**
```
ย้าย flow <ชื่อ> ตามเฟส 5 หลัง feature flag <ชื่อ flag>
ระบุ rollback plan และเกณฑ์เทียบกับ baseline ก่อนเริ่มแก้
```

**Review ก่อน merge**
```
รีวิว diff นี้ตามหัวข้อ 4, 5, 6 ของ UXUI-MASTER-BRIEF.md และรัน critique ด้านภาพ
รายงานเฉพาะปัญหาที่ต้องแก้ก่อน merge แยกจากข้อเสนอแนะ
```

---

## 10. บันทึกการตัดสินใจ (Decision Log)

ให้ AI เพิ่มรายการที่นี่ทุกครั้งที่มีการตัดสินใจสำคัญ เพื่อให้เซสชันถัดไปรู้ที่มา

| วันที่ | การตัดสินใจ | ทางเลือกที่ไม่เลือก | เหตุผล | ผู้อนุมัติ |
|---|---|---|---|---|
| | | | | |
