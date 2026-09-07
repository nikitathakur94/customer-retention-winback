"""Half-open feature windows; outcomes stored separately and immature labels null."""
from .common import CUTS,connect,read,run_dir,save
from .features import FEATURES

def snapshot_sql(cutoff):
    # Cutoff is a validated ISO date from configuration, never dashboard free text.
    import datetime
    datetime.date.fromisoformat(cutoff)
    purchase="event_type='purchase'"
    expressions=[]
    for days in [7,14,28,60]:
        expressions.append(f"count(DISTINCT cast(event_time AS DATE)) FILTER(WHERE {purchase} AND event_time>=t-INTERVAL '{days} days') AS purchasing_days_{days}")
    for days in [7,14,28]: expressions.append(f"count(DISTINCT cast(event_time AS DATE)) FILTER(WHERE event_time>=t-INTERVAL '{days} days') AS active_days_{days}")
    for event,name in [('view','views'),('cart','carts'),('remove_from_cart','removals')]:
        expressions.append(f"count(*) FILTER(WHERE event_type='{event}' AND event_time>=t-INTERVAL '28 days') AS {name}_28")
    for days in [28,60]: expressions.append(f"coalesce(sum(price) FILTER(WHERE {purchase} AND valid_price AND event_time>=t-INTERVAL '{days} days'),0) AS value_{days}")
    extra=',\n'.join(expressions)
    return f"""WITH windowed AS (SELECT *,TIMESTAMPTZ '{cutoff} 00:00:00+00' t FROM int_behavior_events
    WHERE event_time>=TIMESTAMPTZ '{cutoff} 00:00:00+00'-INTERVAL '60 days' AND event_time<TIMESTAMPTZ '{cutoff} 00:00:00+00'),
    category_counts AS (SELECT user_id, category_id,count(*) n FROM windowed WHERE event_type='view' AND category_id IS NOT NULL GROUP BY 1,2),
    concentration AS (SELECT user_id,max(n)::DOUBLE/sum(n) category_view_concentration FROM category_counts GROUP BY 1),
    aggregates AS (SELECT user_id, t AS as_of_timestamp,
    epoch(t-max(event_time) FILTER(WHERE {purchase}))/86400 purchase_recency,
    epoch(t-max(event_time))/86400 event_recency,
    epoch(t-max(event_time) FILTER(WHERE event_type='view'))/86400 view_recency,
    epoch(t-max(event_time) FILTER(WHERE event_type='cart'))/86400 cart_recency,
    count(DISTINCT event_time) FILTER(WHERE {purchase}) occasions_60,
    avg(valid_price::INTEGER) FILTER(WHERE {purchase}) valid_price_share,
    median(price) FILTER(WHERE {purchase} AND valid_price) median_purchase_event_value,
    epoch(t-min(event_time) FILTER(WHERE {purchase}))/86400 first_purchase_age,
    count(DISTINCT cast(event_time AS DATE)) FILTER(WHERE {purchase})>1 repeat_buyer,
    epoch(max(event_time) FILTER(WHERE {purchase})-min(event_time) FILTER(WHERE {purchase}))/86400/nullif(count(DISTINCT event_time) FILTER(WHERE {purchase})-1,0) mean_purchase_gap,
    count(DISTINCT user_session) FILTER(WHERE event_time>=t-INTERVAL '28 days') sessions_28,
    count(DISTINCT product_id) FILTER(WHERE event_type='view' AND event_time>=t-INTERVAL '28 days') products_28,
    count(DISTINCT category_id) FILTER(WHERE event_type='view' AND event_time>=t-INTERVAL '28 days') categories_28,
    count(*) FILTER(WHERE event_type='cart' AND event_time>=t-INTERVAL '14 days')>0 AND count(*) FILTER(WHERE {purchase} AND event_time>=t-INTERVAL '14 days')=0 cart_without_purchase_14,
    count(*) FILTER(WHERE event_time>=t-INTERVAL '14 days') activity_recent_14,
    count(*) FILTER(WHERE event_time>=t-INTERVAL '28 days' AND event_time<t-INTERVAL '14 days') activity_previous_14,
    count(DISTINCT category_id) FILTER(WHERE {purchase}) purchase_categories,
    avg((user_session IS NULL)::INTEGER) missing_session_share,
    max(event_time) feature_max_timestamp, {extra}
    FROM windowed GROUP BY user_id,t HAVING count(*) FILTER(WHERE {purchase})>0)
    SELECT a.*,activity_recent_14-activity_previous_14 activity_change,
    (activity_recent_14-activity_previous_14)::DOUBLE/nullif(activity_previous_14,0) activity_relative_change,
    activity_previous_14=0 no_activity_baseline,c.category_view_concentration
    FROM aggregates a LEFT JOIN concentration c USING(user_id)"""

def build(mode='dev'):
    import pandas as pd
    con=connect(mode); quality=read(run_dir(mode)/'quality.json'); summary=[]
    for i,(split,t) in enumerate(CUTS.items()):
        con.execute('CREATE OR REPLACE TEMP TABLE snap AS '+snapshot_sql(t))
        con.execute(('CREATE OR REPLACE TABLE mart_customer_snapshot AS ' if i==0 else 'INSERT INTO mart_customer_snapshot ')+f"SELECT *, '{split}' split FROM snap")
        end=pd.Timestamp(t,tz='UTC')+pd.Timedelta(days=28)
        mature=quality['coverage_usable'] and end<=pd.Timestamp(quality['coverage_end_exclusive'],tz='UTC')
        label="CASE WHEN count(e.user_id)>0 THEN 0 ELSE 1 END" if mature else 'NULL::INTEGER'
        query=f"""SELECT s.user_id,s.as_of_timestamp,'{split}' split,{str(mature).lower()} label_mature,
        {label} non_repurchase_28d FROM snap s LEFT JOIN int_behavior_events e ON e.user_id=s.user_id AND e.event_type='purchase' AND e.event_time>=s.as_of_timestamp AND e.event_time<s.as_of_timestamp+INTERVAL '28 days' GROUP BY 1,2"""
        con.execute(('CREATE OR REPLACE TABLE mart_customer_outcome AS ' if i==0 else 'INSERT INTO mart_customer_outcome ')+query)
        df=con.execute(f"SELECT * FROM mart_customer_snapshot WHERE split='{split}'").df()
        df.to_parquet(run_dir(mode)/f'features_{split}.parquet',index=False)
        outcomes=con.execute(f"SELECT * FROM mart_customer_outcome WHERE split='{split}'").df(); outcomes.to_parquet(run_dir(mode)/f'outcomes_{split}.parquet',index=False)
        assert (df.feature_max_timestamp<df.as_of_timestamp).all()
        assert not df.user_id.duplicated().any()
        summary.append({'split':split,'cutoff':t,'n':len(df),'label_mature':mature,'non_repurchase_prevalence':float(outcomes.non_repurchase_28d.mean()) if mature else None})
    save(run_dir(mode)/'snapshots.json',summary); con.close(); return summary
