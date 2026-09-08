# Exercise answers

## 1. business

1. Risk is observational; a person may not respond to contact.
2. Verified identity, permission and reachable contact details.

## 2. sources

1. A checksum detects input changes and supports reproducibility.
2. Identical aggregate attributes can belong to different randomly assigned customers.

## 3. cleaning

1. One observed user and identical purchase timestamp.
2. No source order ID or quantity proves an actual order.

## 4. labels

1. Only in the outcome, not the features.
2. The half-open outcome excludes the exact end timestamp.

## 5. sql_features

1. A prior buyer can still meet the 60-day eligibility window.
2. The previous 14 days had zero activity, so no relative baseline exists.

## 6. models

1. Only the training snapshot.
2. The policy-selection half of validation after separate calibration.

## 7. evaluation

1. Repurchase is rarer and its AP has a different prevalence reference.
2. String user ID deterministically breaks ties.

## 8. audiences

1. They also receive the incentive when they convert in treatment.
2. No. It is a transparent prioritization heuristic without causal or margin identification.

## 9. experiments

1. No. They describe merchandise creatives.
2. No. The populations, intervention and follow-up differ.

## 10. dashboard

1. Only in a clearly labeled retrospective explorer view.
2. The recommendation can favor a simple policy or a prospective experiment when evidence is weak.