-- Grain: observed user + UTC calendar day. Sparse activity; no customer/day cross join.
select md5(user_id || '|' || cast(cast(event_time as date) as varchar)) as customer_day_key,
user_id,cast(event_time as date) as activity_date,count(*) as event_count,
count(*) filter(where event_type='view') as views,
count(*) filter(where event_type='cart') as cart_additions,
count(*) filter(where event_type='remove_from_cart') as cart_removals,
count(*) filter(where event_type='purchase') as purchase_events,
sum(case when event_type='purchase' and valid_price then price else 0 end) as purchase_event_value_proxy
from {{ source('retail','int_behavior_events') }} group by user_id,cast(event_time as date)
