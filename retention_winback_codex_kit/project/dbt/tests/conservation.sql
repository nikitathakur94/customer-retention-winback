select 1 as broken where
(select sum(event_count) from {{ ref('fct_customer_day') }}) <>
(select count(*) from {{ source('retail','int_behavior_events') }})
