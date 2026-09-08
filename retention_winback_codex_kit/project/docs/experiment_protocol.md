# Prospective cosmetics experiment protocol

Status: PROTOCOL AND ASSIGNMENT DRY RUN ONLY. No communication or intervention has occurred. Historical outcomes cannot evaluate the dry-run assignment.

At assignment, use the frozen 60-day purchase eligibility and recent-purchase suppression. Require separately verified identity, permission and contactability before operational activation. Exclude conflicting campaigns through a central campaign registry. Persist the stable customer-level arm in an assignment registry; do not reassign on later scoring runs.

Proposed arms: no contact, reminder/content, incentive, equal allocation. Primary outcome: any observed purchase in [assignment, assignment+28 days). Compare each treatment with control using intention-to-treat denominators, including undelivered contacts and nonconverters. Report absolute rate difference, 95% intervals and Bonferroni-adjusted inference for two primary comparisons. Check assignment sample ratios with a chi-square test before outcome interpretation. Secondary outcomes: purchase-event value proxy and engagement; label exploratory multiplicity separately.

Power inputs remain unspecified until the owner chooses a control-rate assumption and minimum meaningful absolute difference. `retention.experiments.power` calculates independent two-proportion sample sizes with Bonferroni alpha. If available verified contactable population cannot support three arms, use one prespecified treatment versus control, recalculate power with comparisons=1, and register the change before assignment. The current three-arm file is only a software dry run and does not imply feasibility.

Freeze before launch: eligibility SQL version, assignment registry checksum, primary/secondary outcomes, alpha, allocation, power inputs, observation end, analysis code commit and exclusions. No outcome peeking or reassignment. Record a separate analysis-freeze document with owner signoff in a real deployment.

Analysis template: tabulate assigned N, missing outcome follow-up, repurchase count, repurchase rate, difference from control, standard error, CI and raw/adjusted p-values. Treat missing follow-up as unknown and investigate attrition rather than assigning zeros.

Unavailable production guardrails: unsubscribes, complaints, returns, margin, discount redemption, delivery and cross-channel purchases. Monitoring these requires additional authorized sources. Actual Hillstrom effects cannot supply a measured cosmetics treatment effect.
