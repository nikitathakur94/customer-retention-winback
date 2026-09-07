from pathlib import Path
import streamlit as st
from retention.common import ROOT,read,DISCLOSURE
st.set_page_config(page_title='Retention & Win-Back',layout='wide')
st.title('Customer Retention & Win-Back')
st.caption(DISCLOSURE)
mode=st.sidebar.selectbox('Run mode',['dev','full'])
p=ROOT/'artifacts'/f'{mode}-v1'
st.caption(f'REES46 cosmetics • {mode} • OBSERVED • 60-day history / 28-day future purchase')
if (p/'snapshots.json').exists(): st.dataframe(read(p/'snapshots.json'),width='stretch')
else: st.info('No built snapshots yet. Run make demo to acquire and build the real-data development sample.')
