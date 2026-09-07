select user_id from {{ source('retail','mart_customer_snapshot') }}
where feature_max_timestamp>=as_of_timestamp or purchasing_days_60<1
