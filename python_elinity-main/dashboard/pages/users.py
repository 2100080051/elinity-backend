import streamlit as st
import pandas as pd
from sqlalchemy.orm import selectinload
from models.user import Tenant
from fastapi.encoders import jsonable_encoder
from dashboard.pages.user_detail import user_detail_page
from st_aggrid import AgGrid, GridOptionsBuilder

def users_page():
    st.title("Users Dashboard")
    # Load users directly from DB
    try:
        db = get_db()
        users = (
            session.query(Tenant)
            .options(
                selectinload(Tenant.profile_pictures),
                selectinload(Tenant.personal_info),
                selectinload(Tenant.big_five_traits),
                selectinload(Tenant.psychology),
                selectinload(Tenant.interests_and_hobbies),
                selectinload(Tenant.values_beliefs_and_goals),
                selectinload(Tenant.favorites),
                selectinload(Tenant.relationship_preferences),
                selectinload(Tenant.friendship_preferences),
                selectinload(Tenant.collaboration_preferences),
                selectinload(Tenant.personal_free_form),
                selectinload(Tenant.intentions),
            )
            .all()
        )
        data = jsonable_encoder(users)
    except Exception as e:
        st.error(f"Failed to load users: {e}")
        return
    df = pd.json_normalize(data)
    # Show only tenant basic columns
    if not df.empty:
        basic_cols = ['id', 'email', 'phone']
        df_basic = df[basic_cols]
        st.subheader("Users List")
        # Build grid options for single row selection
        gb = GridOptionsBuilder.from_dataframe(df_basic)
        gb.configure_selection('single')
        grid_options = gb.build()
        grid_response = AgGrid(
            df_basic,
            gridOptions=grid_options,
            enable_enterprise_modules=False,
            update_mode='SELECTION_CHANGED'
        )
        selected = grid_response['selected_rows']
        if selected:
            selected_id = selected[0].get('id')
            user_detail_page(selected_id)
        return
