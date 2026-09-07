select user_id from {{ source('retail','mart_customer_outcome') }}
where (not label_mature and non_repurchase_28d is not null) or (label_mature and non_repurchase_28d is null)
