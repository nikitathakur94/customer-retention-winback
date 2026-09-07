"""Stream monthly CSVs to DuckDB; retain row identity and duplicate ambiguity."""
from pathlib import Path
from .common import ROOT,connect,read,save,run_dir

def profile(mode='dev'):
    source=read(ROOT/'data/manifests/acquisition.json')['cosmetics']
    if source['status']!='acquired': raise RuntimeError(source.get('resume','Cosmetics unavailable'))
    con=connect(mode); reports=[]
    con.execute('DROP TABLE IF EXISTS source_events')
    for i,file in enumerate(source['files']):
        path=file['path'].replace("'","''")
        con.execute(f"CREATE OR REPLACE TEMP TABLE raw_month AS SELECT row_number() OVER () AS source_row, * FROM read_csv('{path}',all_varchar=true,parallel=false)")
        names=[r[0] for r in con.execute('DESCRIBE raw_month').fetchall()]
        expected={'event_time','event_type','product_id','category_id','category_code','brand','price','user_id','user_session'}
        if not expected.issubset(names): raise ValueError(f'Schema mismatch: {names}')
        q=con.execute("""SELECT count(*) n, count(*) FILTER(WHERE user_id IS NULL) missing_user,
        count(*) FILTER(WHERE try_cast(event_time AS TIMESTAMPTZ) IS NULL) invalid_time,
        count(*) FILTER(WHERE user_session IS NULL) missing_session,
        count(*) FILTER(WHERE brand IS NULL) missing_brand,
        count(*) FILTER(WHERE category_code IS NULL) missing_category,
        count(*) FILTER(WHERE try_cast(price AS DOUBLE) IS NULL OR try_cast(price AS DOUBLE)<=0) invalid_price,
        min(try_cast(event_time AS TIMESTAMPTZ)) first_event, max(try_cast(event_time AS TIMESTAMPTZ)) last_event
        FROM raw_month""").df().iloc[0].to_dict()
        q['file']=file['name']; q['event_counts']=dict(con.execute('SELECT event_type,count(*) FROM raw_month GROUP BY 1').fetchall()); reports.append(q)
        sample="AND ('0x'||substr(md5(user_id),1,8))::UBIGINT % 10=0" if mode=='dev' else ''
        select=f"""SELECT '{file['name']}' AS source_file,source_row,try_cast(event_time AS TIMESTAMPTZ) AS event_time,
        event_type,product_id,category_id,category_code,brand,try_cast(price AS DOUBLE) AS price,user_id,user_session,
        md5(concat_ws('|',coalesce(event_time,''),coalesce(event_type,''),coalesce(product_id,''),coalesce(category_id,''),coalesce(category_code,''),coalesce(brand,''),coalesce(price,''),coalesce(user_id,''),coalesce(user_session,''))) content_hash
        FROM raw_month WHERE true {sample}"""
        con.execute(('CREATE TABLE source_events AS ' if i==0 else 'INSERT INTO source_events ')+select)
        print(f"Ingested {file['name']} ({mode})",flush=True)
    con.execute("""CREATE OR REPLACE TABLE stg_cosmetics_events AS SELECT *,
    user_id IS NOT NULL AND event_time IS NOT NULL AND event_type IN ('view','cart','remove_from_cart','purchase') AS valid_behavior,
    price IS NOT NULL AND isfinite(price) AND price>0 AS valid_price,
    count(*) OVER(PARTITION BY content_hash) AS identical_row_count
    FROM source_events""")
    con.execute('CREATE OR REPLACE TABLE int_behavior_events AS SELECT * FROM stg_cosmetics_events WHERE valid_behavior')
    counts=con.execute('SELECT count(*) source_rows,count(*) FILTER(WHERE valid_behavior) included,count(*) FILTER(WHERE NOT valid_behavior) excluded,count(*)-count(DISTINCT content_hash) identical_excess FROM stg_cosmetics_events').df().iloc[0].to_dict()
    sensitivity=con.execute("""SELECT sum(price) FILTER(WHERE valid_price) preserved_value,
    count(*) purchase_events,count(DISTINCT (user_id,event_time)) inferred_occasions,
    count(DISTINCT(user_id,cast(event_time AS DATE))) purchasing_days,
    count(DISTINCT(user_id,user_session)) provided_session_proxy FROM int_behavior_events WHERE event_type='purchase'""").df().iloc[0].to_dict()
    sensitivity['deduplicated_value']=con.execute("SELECT sum(price) FILTER(WHERE valid_price) FROM (SELECT DISTINCT ON(content_hash) * FROM int_behavior_events WHERE event_type='purchase')").fetchone()[0]
    daily=con.execute("SELECT cast(event_time AS DATE) AS day,count(*) n FROM int_behavior_events GROUP BY 1 ORDER BY 1").df()
    daily.to_csv(run_dir(mode)/'coverage_daily.csv',index=False)
    expected_days=152
    coverage_ok=len(daily)==expected_days and str(daily.day.min().date())=='2019-10-01' and str(daily.day.max().date())=='2020-02-29'
    report={'dataset_id':'rees46_cosmetics','run_mode':mode,'monthly_full_source':reports,'analytical_waterfall':counts,'duplicate_sensitivity':sensitivity,'coverage_usable':coverage_ok,'coverage_start':'2019-10-01','coverage_end_exclusive':'2020-03-01','coverage_basis':'All five monthly archives, publisher monthly coverage, daily event presence. Does not establish absence of intra-day tracking outages.','duplicate_policy':'Preserve multiplicity; binary targets and purchasing-day frequency robust to exact duplicates.','missing_capabilities':['verified currency','true order ID','quantity','refunds','consent','contactability','campaign exposure','margin']}
    save(run_dir(mode)/'quality.json',report); con.close(); return report
