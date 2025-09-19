import streamlit as st
from sqlalchemy.orm import selectinload
from database.session import Session
from models.user import Tenant
from fastapi.encoders import jsonable_encoder

def user_detail_page(user_id: str):
    """Display detailed profile of a specific user"""
    st.title("User Detail")
    session = Session()
    user = (
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
        .filter(Tenant.id == user_id)
        .first()
    )
    if not user:
        st.error("User not found")
        return
    data = jsonable_encoder(user)   
    # Display sections
    sections = [
        ("Basic Info", ["email", "phone", "id"]),
        ("Personal Info", "personal_info"),
        ("Big Five Traits", "big_five_traits"),
        ("Psychology", "psychology"),
        ("Interests and Hobbies", "interests_and_hobbies"),
        ("Values, Beliefs and Goals", "values_beliefs_and_goals"),
        ("Favorites", "favorites"),
        ("Relationship Preferences", "relationship_preferences"),
        ("Friendship Preferences", "friendship_preferences"),
        ("Collaboration Preferences", "collaboration_preferences"),
        ("Personal Free Form", "personal_free_form"),
        ("Intentions", "intentions"),
        ("Profile Pictures", "profile_pictures"),
    ]
    for title, key in sections:
        if isinstance(key, list):
            st.subheader(title)
            st.json({k: data.get(k) for k in key})
        else:
            value = data.get(key)
            if value:
                st.subheader(title)
                st.json(value)
