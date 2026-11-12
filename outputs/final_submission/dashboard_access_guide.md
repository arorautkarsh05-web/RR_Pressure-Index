# RR AUCTION INTELLIGENCE 2027: DASHBOARD ACCESS GUIDE
## Production Power BI Project & Offline Interactive Prototype Instructions

This guide provides complete instructions for accessing, deploying, and presenting the **RR AUCTION INTELLIGENCE 2027** platform.

---

### Deployment Option 1: Microsoft Power BI Desktop Project (.pbip)

The solution is natively packaged as a developer project in `dashboard/`:

```
d:\RR_PRESSURE_INDEX_2027\dashboard\
├── RR_Auction_Intelligence.pbip               <-- Open this file in Power BI Desktop
├── RR_Auction_Intelligence.Report\
│   └── definition.pbir
├── RR_Auction_Intelligence.Dataset\
│   ├── definition.pbism
│   └── model.bim                              <-- Complete Tabular Object Model (52 measures)
├── theme.json                                 <-- Official Rajasthan Royals Dark Theme
├── dax_measures.dax                           <-- Full DAX Measure Repository
└── data\                                      <-- 10 Certified Star Schema CSV tables
```

#### How to Launch:
1. Double-click `dashboard\RR_Auction_Intelligence.pbip`.
2. Microsoft Power BI Desktop (October 2023+ / 64-bit) will load the semantic model, schema relationships, custom theme, and measures automatically.
3. If prompted to refresh data sources, click **Apply Changes**. VertiPaq memory footprint is 3.94 MB; load time is ~6–10 seconds.
4. To export a single compiled document: Click **File &rarr; Save As &rarr; Power BI Document (*.pbix)**.

---

### Deployment Option 2: Standalone Offline HTML Prototype (Zero-Server, Zero-CDN)

For instant presentation in any boardroom, on any laptop or tablet without Power BI installed:

```
d:\RR_PRESSURE_INDEX_2027\dashboard\html\
├── index.html                                 <-- Double-click to launch in any browser
├── assets\
│   ├── styles.css                             <-- Rajasthan Royals design system
│   └── dashboard.js                           <-- Pure SVG vector charting engine
└── data\
    ├── data.js                                <-- Embedded offline data bundle
    └── dashboard_data.json
```

#### How to Launch:
1. Double-click `dashboard\html\index.html` (or open via Chrome, Edge, Safari, Firefox).
2. The dashboard runs 100% offline via `file:///` protocol.
3. Zero web servers, zero internet connection, zero external CDNs required.
4. Features live tab routing, interactive player dossier updates on table row clicks, and head-to-head comparison dropdowns.

---

### Deployment Option 3: Executive Vector PDF Intelligence Briefs

Pre-rendered, high-resolution vector PDF briefs are available in `dashboard\exports\`:
- `dashboard\exports\executive_overview.pdf` (Page 1 Executive Brief)
- `dashboard\exports\batting_intelligence.pdf` (Page 2 Finisher Intelligence)
- `dashboard\exports\bowling_intelligence.pdf` (Page 3 Enforcer Intelligence)
- `dashboard\exports\auction_intelligence.pdf` (Page 5 Target Board & Strategy)
