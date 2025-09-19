"""
Service for converting SQLAlchemy models to dict/JSON for embeddings
"""
from models.user import Tenant
from schemas.user import User
from typing import Dict, Any


def sqlalchemy_to_dict(obj: Any) -> Dict:
    """
    Convert an SQLAlchemy model instance to a dictionary.
    This is a generic function that works with any SQLAlchemy model.
    """
    if obj is None:
        return {}
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # Handle datetime objects by converting to ISO format string
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        result[column.name] = value
    return result


def tenant_to_dict(tenant: Tenant) -> Dict:
    """
    Convert a Tenant SQLAlchemy model to a dictionary with all related objects.
    This function creates a comprehensive representation of a tenant with all their profile data.
    """
    if tenant is None:
        return {}
    
    # Start with base tenant properties
    result = sqlalchemy_to_dict(tenant)
    
    # Add related objects
    if tenant.personal_info:
        result['personal_info'] = sqlalchemy_to_dict(tenant.personal_info)
    
    if tenant.big_five_traits:
        result['big_five_traits'] = sqlalchemy_to_dict(tenant.big_five_traits)
    
    if tenant.mbti_traits:
        result['mbti_traits'] = sqlalchemy_to_dict(tenant.mbti_traits)
    
    if tenant.psychology:
        result['psychology'] = sqlalchemy_to_dict(tenant.psychology)
    
    if tenant.interests_and_hobbies:
        result['interests_and_hobbies'] = sqlalchemy_to_dict(tenant.interests_and_hobbies)
    
    if tenant.values_beliefs_and_goals:
        result['values_beliefs_and_goals'] = sqlalchemy_to_dict(tenant.values_beliefs_and_goals)
    
    if tenant.favorites:
        result['favorites'] = sqlalchemy_to_dict(tenant.favorites)
    
    if tenant.relationship_preferences:
        result['relationship_preferences'] = sqlalchemy_to_dict(tenant.relationship_preferences)
    
    if tenant.friendship_preferences:
        result['friendship_preferences'] = sqlalchemy_to_dict(tenant.friendship_preferences)
    
    if tenant.collaboration_preferences:
        result['collaboration_preferences'] = sqlalchemy_to_dict(tenant.collaboration_preferences)
    
    if tenant.personal_free_form:
        result['personal_free_form'] = sqlalchemy_to_dict(tenant.personal_free_form)
    
    if tenant.intentions:
        result['intentions'] = sqlalchemy_to_dict(tenant.intentions)
    
    if tenant.aspiration_and_reflections:
        result['aspiration_and_reflections'] = sqlalchemy_to_dict(tenant.aspiration_and_reflections)
    
    if tenant.ideal_characteristics:
        result['ideal_characteristics'] = sqlalchemy_to_dict(tenant.ideal_characteristics)
    
    # Handle profile pictures which is a list
    if tenant.profile_pictures:
        result['profile_pictures'] = [sqlalchemy_to_dict(pic) for pic in tenant.profile_pictures]
    
    return result


def tenant_to_pydantic(tenant: Tenant) -> Dict:
    """
    Convert a Tenant SQLAlchemy model to a Pydantic model and then to a dictionary.
    This uses Pydantic for validation and conversion.
    """
    if tenant is None:
        return {}
    
    # Use from_orm to convert SQLAlchemy model to Pydantic model
    # The from_attributes=True setting in the Config class allows this
    pydantic_user = User.model_validate(tenant)
    
    # Convert to dict and return
    return pydantic_user.model_dump()
