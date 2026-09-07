-- Grain: scoring cutoff + maturity; immature means NULL, never zero return rate.
select as_of_timestamp,split,label_mature,count(*) as eligible_customers,
sum(1-non_repurchase_28d) as returning_customers,
avg(1-non_repurchase_28d) as observed_repurchase_28d
from {{ source('retail','mart_customer_outcome') }} group by 1,2,3
