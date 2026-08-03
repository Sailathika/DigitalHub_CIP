import pandas as pd
import plotly.express as px
import streamlit as st

from core.api_client import ApiError, get, post
from core.auth import require_dataset
from core.theme import badge_html

st.title("Churn Prediction")
st.caption("Churn risk per customer, trained with a Random Forest on this dataset.")

dataset = require_dataset()

if st.button("Retrain Model", icon=":material/sync:"):
    st.session_state.pop(f"churn_result_{dataset['id']}", None)
    st.session_state.pop(f"churn_train_info_{dataset['id']}", None)

result_key = f"churn_result_{dataset['id']}"
train_key = f"churn_train_info_{dataset['id']}"

if result_key not in st.session_state:
    with st.spinner("Loading predictions…"):
        try:
            st.session_state[result_key] = get(f"/churn/{dataset['id']}/predict")
        except ApiError as exc:
            if exc.status_code == 400:
                with st.spinner("No model trained yet — training a churn model now…"):
                    try:
                        st.session_state[train_key] = post(f"/churn/{dataset['id']}/train")
                        st.session_state[result_key] = get(f"/churn/{dataset['id']}/predict")
                    except ApiError as train_exc:
                        st.error(train_exc.message)
                        st.stop()
            else:
                st.error(exc.message)
                st.stop()

result = st.session_state[result_key]
train_info = st.session_state.get(train_key)

predictions = result["predictions"]
high_risk_count = sum(1 for p in predictions if p["risk_level"] == "High")

if train_info:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", f"{train_info['accuracy']:.1%}")
    c2.metric("F1 Score", f"{train_info['f1_score']:.3f}")
    c3.metric("Precision / Recall", f"{train_info['precision']:.2f} / {train_info['recall']:.2f}")
    c4.metric("High Risk Customers", high_risk_count)
else:
    st.metric("High Risk Customers", high_risk_count)
    st.caption("Full training metrics show right after training — model is already trained for this dataset.")

feature_importance = result.get("feature_importance") or (train_info or {}).get("feature_importance")
if feature_importance:
    st.markdown("##### Feature Importance")
    df_fi = pd.DataFrame(
        [{"feature": k.replace("_", " ").title(), "importance": v} for k, v in feature_importance.items()]
    ).sort_values("importance")
    fig = px.bar(df_fi, x="importance", y="feature", orientation="h")
    fig.update_traces(marker_color="#EF4444")
    fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=None, xaxis_title=None,
                       plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("##### Churn Risk by Customer")
if predictions:
    df = pd.DataFrame(predictions).sort_values("churn_probability", ascending=False)
    df["Probability"] = df["churn_probability"].apply(lambda v: f"{v:.1%}")
    df["Risk"] = df["risk_level"]
    df = df.rename(columns={"name": "Customer", "customer_ref": "Customer ID"})
    st.dataframe(df[["Customer", "Customer ID", "Probability", "Risk"]], use_container_width=True, hide_index=True)
else:
    st.info("No customers available to predict for.")
