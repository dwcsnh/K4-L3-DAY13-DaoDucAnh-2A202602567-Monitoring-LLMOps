import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

st.set_page_config(page_title="Day 13 Dashboard", layout="wide")

@st.cache_data(ttl=30)
def load_data():
    try:
        with open("data/logs.jsonl", "r") as f:
            data = [json.loads(line) for line in f]
        df = pd.DataFrame(data)
        if not df.empty and 'ts' in df.columns:
            df['ts'] = pd.to_datetime(df['ts'])
            cutoff = datetime.utcnow() - timedelta(minutes=60)
            df = df[df['ts'] >= cutoff.replace(tzinfo=df['ts'].dt.tz)]
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("No data found")
    st.stop()

st.title("K4-L3A Day 13 Monitoring & LLMOps")
st.write("Time range: Last 60 minutes")

c1, c2 = st.columns(2)
c3, c4 = st.columns(2)
c5, c6 = st.columns(2)

with c1:
    st.subheader("1. Latency percentiles and TTFT (ms)")
    sent = df[df['event'] == 'response_sent']
    if not sent.empty:
        p50 = sent['latency_ms'].quantile(0.5)
        p95 = sent['latency_ms'].quantile(0.95)
        p99 = sent['latency_ms'].quantile(0.99)
        ttft_95 = sent['ttft_ms'].quantile(0.95)
        st.metric("P50 Latency", f"{p50:.2f} ms")
        st.metric("P95 Latency", f"{p95:.2f} ms", delta="- Threshold: 3000 ms", delta_color="inverse")
        st.metric("P99 Latency", f"{p99:.2f} ms")
        st.metric("P95 TTFT", f"{ttft_95:.2f} ms")
    else:
        st.write("No data")

with c2:
    st.subheader("2. Request traffic (requests_per_minute)")
    reqs = df[df['event'] == 'request_received']
    count = len(reqs)
    rpm = count / 60
    st.metric("Total Requests", count)
    st.metric("Rate per minute", f"{rpm:.2f}", delta="+ Threshold: 1", delta_color="off")

with c3:
    st.subheader("3. Error rate and retrieval success (%)")
    errs = len(df[df['event'] == 'request_failed'])
    err_rate = (errs / count * 100) if count > 0 else 0
    st.metric("Error Rate", f"{err_rate:.2f} %", delta="- Threshold: 2 %", delta_color="inverse")
    if 'error_type' in df.columns:
        st.write("Breakdown:")
        st.write(df['error_type'].value_counts())
    
    if 'tool_success' in sent.columns:
        valid_tools = sent.dropna(subset=['tool_success'])
        if len(valid_tools) > 0:
            success = valid_tools['tool_success'].astype(bool).sum()
            st.metric("Retrieval Success Rate", f"{(success / len(valid_tools) * 100):.2f} %")

with c4:
    st.subheader("4. Cost over time (USD)")
    if not sent.empty and 'cost_usd' in sent.columns:
        total_cost = sent['cost_usd'].sum()
        st.metric("Total Cost", f"${total_cost:.4f}", delta="- Threshold: 2.5", delta_color="inverse")
        cost_by_min = sent.set_index('ts').resample('1min')['cost_usd'].sum()
        st.line_chart(cost_by_min)
    else:
        st.write("No data")

with c5:
    st.subheader("5. Input and output tokens")
    if not sent.empty and 'tokens_in' in sent.columns:
        tokens_in = sent['tokens_in'].sum()
        tokens_out = sent['tokens_out'].sum()
        st.metric("Tokens In", tokens_in)
        st.metric("Tokens Out", tokens_out)
        st.metric("Total Tokens", tokens_in + tokens_out, delta="- Threshold: 50000", delta_color="inverse")
    else:
        st.write("No data")

with c6:
    st.subheader("6. Quality proxy (score_0_to_1)")
    if not sent.empty and 'quality_score' in sent.columns:
        mean_quality = sent['quality_score'].mean()
        st.metric("Mean Quality Score", f"{mean_quality:.2f}", delta="+ Threshold: 0.75", delta_color="off")
        st.line_chart(sent.set_index('ts')['quality_score'])
    else:
        st.write("No data")
