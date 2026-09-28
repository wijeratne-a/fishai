# Rights-request email templates (local 50-mile planning)

**Date:** 2026-09-23  
**Status:** Drafts for a human sender  
**Not:** license grants, scraping instructions, credentials, VMS queries, or guidance to locate fish or fishing spots

Send only after a human has named the legal/operating entity, storage region, and intended research use. Public download pages are not a substitute for a written yes. Until a written yes exists, FishAI classes stay at `CONDITIONAL_REVIEW_REQUIRED` (see `species/goliath-grouper/RVC_RIGHTS_RECORD.md`).

Observer program data and VMS stay out of the public product unless a separate written confidentiality review states that a named aggregate output is allowed. These templates do not request raw observer set locations or VMS tracks.

---

## Template A — NOAA SEFSC / NCEI (accessions 0282183 and 0306184)

**To:** Point of contact on the NCEI accession / SEFSC laboratory pages (e.g. laboratory contact named on the Florida NCRMP fish community products); CC NCEI user services if your counsel prefers  
**Subject:** Written permission request — NCEI 0282183 and 0306184 for research model training and coarsened display

Hello,

I am contacting you about National Coral Reef Monitoring Program fish community data for the Florida Reef Tract, specifically:

- NCEI Accession **0282183** (2022 field season; landing page describes two-stage design; Keys included on the page)
- NCEI Accession **0306184** (2024 field season; landing page describes single-stage design)

Parent collection context: DOI https://doi.org/10.7289/v52n50ks

We are building an internal research prototype (working name FishAI). We are **not** asking for help locating fish, wrecks, spawning sites, or fishing spots. We need a clear written yes or no on the following uses:

1. **Acquisition** of the public archive packages for the two accessions above, for internal research only.
2. **Storage** of the extract **outside** our public source repository, with access controls, and with **native sample coordinates withheld** from git, browsers, fixtures, and public materials.
3. **Model training** on detection / non-detection (or counts) of Atlantic goliath grouper (*Epinephelus itajara*, species code `EPIITAJ` if present) and other reef fishes as needed to define the sample frame, using effort and habitat fields in the files.
4. **Coarsened aggregate display** of model outputs (e.g. sample-unit or coarser probabilities), never native coordinates, never site pins that could serve as wreck, aggregation, or nursery guides.
5. **Citation** exactly as you require (we will store the accession citations and parent DOI with any subset phrase you specify).

Please also confirm:

- Whether training on these accessions and publishing derived aggregate graphics is allowed under your terms.
- Whether any partner-contributed rows require additional permission.
- Any rules for sensitive locations or threatened/endangered species rows.
- Whether accession 0306184’s protocol change (single-stage vs two-stage) affects reuse relative to 0282183.

We treat public HTTPS availability and citation text as **not** automatically granting training or display rights. We will not download for training until we have your written answer.

**Requested reply:** a short written **YES** or **NO** (or YES with conditions) covering items 1–5, from a person authorized to speak for the data providers, plus any required citation string.

Thank you,  
[Name]  
[Organization]  
[Email]  
[Storage region / purpose one-liner]

---

## Template B — California Current data steward (CalCOFI CUFES and WCOFS)

**To:** CalCOFI / SWFSC or SIO data steward for CUFES / ichthyoplankton products; and NOAA NOS CO-OPS / OFS contact for WCOFS terms (send as two emails if contacts differ; keep the same ask)  
**Subject:** Written permission request — CalCOFI CUFES and WCOFS for a research nowcast prototype

Hello,

I am requesting written clarification for a **research nowcast prototype** in the California Current (working name FishAI). The proposed biological target is Pacific sardine and northern anchovy egg or encounter products associated with **CalCOFI CUFES** (or the CalCOFI product you designate as correct). The proposed environmental fields are from **WCOFS** (West Coast Operational Forecast System) surface analyses/forecasts.

This is a planning request. We have **not** ingested these datasets into our public repository. We are **not** asking for vessel monitoring queries, scraping procedures, credentials beyond normal public access, or advice on where to fish.

Please provide a written **YES** or **NO** (or YES with conditions) on:

1. **Internal acquisition and storage** of the named CalCOFI CUFES (or designated) tables for research, stored outside our public git repo if you require.
2. **Training** a statistical nowcast / index model (candidate family: spatiotemporal delta models) that predicts egg density or encounter metrics conditional on survey effort and ocean fields.
3. **Use of WCOFS** fields as covariates, including any attribution, redistribution, or “do not imply NOAA endorsement” rules we must follow for derived research graphics.
4. **Coarsened public display** of research outputs (probabilities or indices on a coarse grid), with no claim of live tracking and no harvest guidance.
5. **Citation** strings and versioning you require for both the biological and ocean-model inputs.

Please state any prohibition on commercial use, redistribution of raw files, or parallel bulk downloads we must respect. If CUFES and WCOFS need separate approvals, a YES/NO on each dataset is ideal.

We will not begin training ingest until we have written answers.

Thank you,  
[Name]  
[Organization]  
[Email]  
[Intended region: California Current ~50-mile research window]  
[Non-goals: no fishing guidance; no public raw coordinates]

---

## After a reply arrives

1. File the email (or letter) under the relevant species or planning rights record.  
2. Assign `APPROVED_*` **only** if the writing clearly grants the use; otherwise leave `CONDITIONAL_REVIEW_REQUIRED`.  
3. Record hash and schema notes only **after** approval and acquisition.  
4. Keep observer/VMS and any confidential fleet data on a separate review track; default remains **out of the public product**.
