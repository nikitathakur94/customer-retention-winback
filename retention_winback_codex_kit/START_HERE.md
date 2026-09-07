# Customer Retention & Win-Back Analytics — local Codex kit

This kit specifies a public-data reconstruction of Nikita Thakur’s Factspan/Macy’s customer-retention project. It is a build specification, not a completed implementation or a package of measured results.

## Use it

Extract the kit into a new local folder and open that folder in your local Codex workspace. Paste this:

```text
Read CODEX_MASTER_PROMPT.md completely. Also read RESOURCES.md,
ACCEPTANCE_CHECKLIST.md, and the files under resources/.

Build the project described in that specification under ./project/.
Do not stop at a plan, scaffold, or sample notebook. Acquire the specified
real datasets through their documented sources, execute the pipeline,
build and test the dashboard, generate the audience outputs and independent
campaign experiment analysis, and create the learning materials and final
presentation from actual computed results.

Start with an environment/access check and a working real-data vertical
slice, then continue through the phases. Keep STATUS.md and HANDOFF.md
current. Make the important choices understandable through short decision
records, source traces, and worked examples. Keep reconstructed results
separate from claims about my original employment project.

Never invent data, measurements, campaign effects, original-project facts,
or completed tests. If access or local resources block a stage, tell me the
exact blocker and resume command, and continue the work that is not blocked.
```

The master prompt is self-contained enough to use on its own; the supporting files make source selection, configuration, and acceptance checks easier to keep consistent.

## What the build should produce

The main project follows real shopping histories into a forward-looking non-repurchase model, a customer-health dashboard, and proposed win-back audiences. A separate real randomized email dataset demonstrates treatment-versus-control measurement and an introductory uplift comparison. The two datasets must never be joined or their outcomes combined.

The final product should include runnable SQL/Python/dbt, a trained model with out-of-time evaluation, real anonymous customer traces, seven dashboard pages, local audience exports, a proposed experiment, a real independent experiment readout, a learning guide, and editable slides plus a PDF.

## Files in this kit

- `CODEX_MASTER_PROMPT.md`: complete implementation brief.
- `RESOURCES.md`: selected source and official documentation links, with their roles.
- `resources/source_manifest.yaml`: machine-readable source information and verification limits.
- `resources/project_spec.yaml`: initial date, modeling, sampling, and evidence-label settings.
- `resources/metric_contracts.yaml`: initial grains and metric definitions.
- `ACCEPTANCE_CHECKLIST.md`: correctness and completion checks, initially not run.
- `KIT_MANIFEST.json`: checksums of the guidance files.

## What is not included

No raw datasets, trained model, application, or campaign results are bundled. Source descriptions and documentation were researched for this kit; the underlying archives have not been downloaded or profiled here. Codex must acquire the data locally, verify permissions and actual content, record dataset versions/checksums, and execute the analysis.

Kaggle access can require local authentication or consent. Configure credentials only through supported local methods; do not paste tokens into the prompt or commit them to the repository. See the official KaggleHub documentation linked in RESOURCES.md.

The settings in `resources/` are starting design decisions, not measurements. Null values mean unknown/uncomputed, not zero. All downloaded data stays local unless its terms and the owner’s explicit publishing instructions permit otherwise.

## Resume boundary

This reconstruction teaches the same problem described on the resume. Its algorithms, dates, results, code, and datasets do not establish what was originally built at Macy’s. Preserve that distinction in interview notes and any portfolio publication.
