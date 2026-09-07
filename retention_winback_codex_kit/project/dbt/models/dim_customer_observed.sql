-- Grain: observed user. Descriptive source coverage only; never a predictor lookup.
select user_id,min(event_time) as first_observed_event,max(event_time) as last_observed_event,
count(*) as source_event_count
from {{ source('retail','int_behavior_events') }} group by user_id
