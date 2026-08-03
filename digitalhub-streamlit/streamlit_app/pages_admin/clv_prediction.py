import pandas as pd
import streamlit as st

from core.api_client import ApiError, get, post
from core.auth import require_dataset
from core.utils import format_currency

st.title("CLV Prediction")
st.caption("Predicted customer lifetime value, trained on this dataset's customers.")

dataset = require_dataset()

if st.button("Retrain Model", icon=":material/sync:"):
    st.session_state.pop(f"clv_result_{dataset['id']}", None)
    st.session_state.pop(f"clv_train_info_{dataset['id']}", None)

result_key = f"clv_result_{dataset['id']}"
train_key = f"clv_train_info_{dataset['id']}"

if result_key not in st.session_state:
    with st.spinner("Loading predictions…"):
        try:
            st.session_state[result_key] = get(f"/clv/{dataset['id']}/predict")
        except ApiError as exc:
            if exc.status_code == 400:
                with st.spinner("No model trained yet — training a CLV model now…"):
                    try:
                        st.session_state[train_key] = post(f"/clv/{dataset['id']}/train")
                        st.session_state[result_key] = get(f"/clv/{dataset['id']}/predict")
                    except ApiError as train_exc:
                        st.error(train_exc.message)
                        st.stop()
            else:
                st.error(exc.message)
                st.stop()

result = st.session_state[result_key]
train_info = st.session_state.get(train_key)

if train_info:
    c1, c2, c3 = st.columns(3)
    c1.metric("R² Score", f"{train_info['r2_score']:.3f}")
    c2.metric("Mean Abs. Error", format_currency(train_info["mae"]))
    c3.metric("Trained On", f"{train_info['trained_on_customers']} customers")
else:
    st.caption("Metric details (R²/MAE) show right after training — model is already trained for this dataset.")

st.markdown("##### Predicted Lifetime Value by Customer")
predictions = result["predictions"]
if predictions:
    df = pd.DataFrame(predictions).rename(
        columns={"name": "Customer", "customer_ref": "Customer ID", "predicted_clv": "Predicted CLV"}
    )
    df["Predicted CLV"] = df["Predicted CLV"].apply(format_currency)
    st.dataframe(df[["Customer", "Customer ID", "Predicted CLV"]], use_container_width=True, hide_index=True)
else:
    st.info("No customers available to predict for.")
