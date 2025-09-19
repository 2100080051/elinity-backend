import streamlit as st
from sqlalchemy.orm import selectinload
import pandas as pd
from database.session import Session
from models.user import Tenant
from fastapi.encoders import jsonable_encoder

def report_page():
    st.title("Users Report")
    # Load users directly from DB
    session = Session()
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
    ).all()
    data = jsonable_encoder(users)
    df = pd.json_normalize(data)
    # Example report: count by city
    if 'personal_info.city' in df.columns:
        report = df.groupby('personal_info.city').size().reset_index(name='count')
        st.bar_chart(report.set_index('personal_info.city'))
    else:
        st.write("No city data available")
