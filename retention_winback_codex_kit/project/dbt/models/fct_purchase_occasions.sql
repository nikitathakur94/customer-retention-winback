-- Grain: user + identical purchase timestamp. Proxy occasions, not true orders.
select md5(user_id || '|' || cast(event_time as varchar)) as occasion_key,
user_id,event_time,count(*) as purchase_event_count,
sum(case when valid_price then price else 0 end) as purchase_event_value_proxy,
count(*) filter(where not valid_price) as invalid_price_events
from {{ source('retail','int_behavior_events') }}
where event_type='purchase' group by user_id,event_time
