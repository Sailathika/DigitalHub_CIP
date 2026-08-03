from typing import Optional

import streamlit as st

from core.api_client import ApiError, delete, get, post_form, put_form
from core.theme import badge_html

st.title("My Products")
st.caption("Manage your product catalog, pricing, and stock levels.")


def _submit_product_form(mode: str, product: Optional[dict] = None):
    """Shared create/edit form. `mode` is 'create' or 'edit'."""
    prefix = "add" if mode == "create" else f"edit_{product['id']}"
    with st.form(f"{prefix}_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Product Name", value=product["name"] if product else "")
        category = c2.text_input("Category", value=(product or {}).get("category") or "", placeholder="e.g. Smartphones")
        description = st.text_area("Description", value=(product or {}).get("description") or "")

        c3, c4, c5 = st.columns(3)
        price = c3.number_input("Price", min_value=0.0, value=float(product["price"]) if product else 0.0, step=1.0)
        stock = c4.number_input("Stock", min_value=0, value=int(product["stock"]) if product else 0, step=1)
        status = c5.selectbox(
            "Status", ["active", "inactive", "draft"],
            index=["active", "inactive", "draft"].index(product["status"]) if product else 0,
            format_func=str.title,
        )

        c6, c7 = st.columns(2)
        sku = c6.text_input("SKU", value=(product or {}).get("sku") or "")
        brand = c7.text_input("Brand", value=(product or {}).get("brand") or "")

        if product and product.get("imageUrl"):
            st.image(product["imageUrl"], width=120, caption="Current image")
        image_file = st.file_uploader("Product Image (optional)", type=["png", "jpg", "jpeg", "webp", "gif"], key=f"{prefix}_image")

        submit_label = "Add Product" if mode == "create" else "Save Changes"
        submitted = st.form_submit_button(submit_label, type="primary")

        if submitted:
            if not name.strip() or not sku.strip():
                st.error("Product name and SKU are required.")
                return

            form_data = {
                "name": name, "category": category, "description": description,
                "price": price, "stock": stock, "sku": sku, "brand": brand, "status": status,
            }
            files = None
            if image_file is not None:
                files = {"image": (image_file.name, image_file.getvalue(), image_file.type)}

            try:
                if mode == "create":
                    post_form("/vendor/products/", data=form_data, files=files)
                    st.success("Product added.")
                else:
                    put_form(f"/vendor/products/{product['id']}", data=form_data, files=files)
                    st.success("Product updated.")
                    st.session_state.editing_product_id = None
                st.rerun()
            except ApiError as exc:
                st.error(exc.message)


with st.expander("Add Product", icon=":material/add:"):
    _submit_product_form("create")

st.markdown("---")

f1, f2 = st.columns([2, 1])
search = f1.text_input("Search by name, SKU, or brand", key="product_search")

try:
    initial = get("/vendor/products/")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

category_filter = f2.selectbox("Category", ["all"] + initial["categories"])

params = {}
if search:
    params["search"] = search
if category_filter != "all":
    params["category"] = category_filter

try:
    data = get("/vendor/products/", params=params)
except ApiError as exc:
    st.error(exc.message)
    st.stop()

products = data["products"]
st.caption(f"{len(products)} product(s)")

status_variant = {"active": "success", "inactive": "secondary", "draft": "warning"}

if not products:
    st.info("No products yet. Add your first product above.")
else:
    h1, h2, h3, h4, h5, h6 = st.columns([2.5, 1, 1, 1, 1, 1.5])
    h1.markdown("<span class='dh-muted' style='font-weight:600;'>PRODUCT</span>", unsafe_allow_html=True)
    h2.markdown("<span class='dh-muted' style='font-weight:600;'>CATEGORY</span>", unsafe_allow_html=True)
    h3.markdown("<span class='dh-muted' style='font-weight:600;'>PRICE</span>", unsafe_allow_html=True)
    h4.markdown("<span class='dh-muted' style='font-weight:600;'>STOCK</span>", unsafe_allow_html=True)
    h5.markdown("<span class='dh-muted' style='font-weight:600;'>STATUS</span>", unsafe_allow_html=True)
    h6.markdown("<span class='dh-muted' style='font-weight:600;'>ACTIONS</span>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:0.4rem 0 0.8rem 0;border-color:#E2E8F0;'>", unsafe_allow_html=True)

for product in products:
    editing = st.session_state.get("editing_product_id") == product["id"]
    confirming_delete = st.session_state.get("confirm_delete_id") == product["id"]

    with st.container(border=True):
        if editing:
            _submit_product_form("edit", product)
            if st.button("Cancel", key=f"cancel_{product['id']}"):
                st.session_state.editing_product_id = None
                st.rerun()
        else:
            c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1, 1, 1, 1, 1.5])
            with c1:
                if product.get("imageUrl"):
                    st.image(product["imageUrl"], width=48)
                st.markdown(f"**{product['name']}**  \n<span class='dh-muted'>{product.get('sku')}</span>", unsafe_allow_html=True)
            c2.markdown(product.get("category") or "—")
            c3.markdown(f"₹{product['price']:,.0f}")
            stock_color = "color:#EF4444;" if product["stock"] <= 0 else ("color:#F59E0B;" if product["stock"] <= 15 else "")
            c4.markdown(f"<span style='{stock_color}'>{product['stock']}</span>", unsafe_allow_html=True)
            c5.markdown(badge_html(product["status"].title(), status_variant.get(product["status"], "default")), unsafe_allow_html=True)

            with c6:
                bcols = st.columns(2)
                if bcols[0].button("Edit", key=f"edit_{product['id']}"):
                    st.session_state.editing_product_id = product["id"]
                    st.rerun()
                if bcols[1].button("Delete", key=f"del_{product['id']}"):
                    st.session_state.confirm_delete_id = product["id"]
                    st.rerun()

        if confirming_delete:
            st.warning(f"Permanently delete **{product['name']}**? This cannot be undone.")
            dc1, dc2 = st.columns(2)
            if dc1.button("Confirm Delete", key=f"confirm_del_{product['id']}", type="primary"):
                try:
                    delete(f"/vendor/products/{product['id']}")
                    st.session_state.confirm_delete_id = None
                    st.success("Product deleted.")
                    st.rerun()
                except ApiError as exc:
                    st.error(exc.message)
            if dc2.button("Cancel", key=f"cancel_del_{product['id']}"):
                st.session_state.confirm_delete_id = None
                st.rerun()
