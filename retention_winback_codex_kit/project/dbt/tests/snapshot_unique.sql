select user_id,as_of_timestamp from {{ source('retail','mart_customer_snapshot') }} group by 1,2 having count(*)<>1
