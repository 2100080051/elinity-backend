from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Float,Integer
import uuid
from datetime import timezone
from database.session import Base
from sqlalchemy.orm import relationship

def gen_uuid():
    return str(uuid.uuid4())

USER_ROLES = ['user','admin']

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    role = Column(String, default='user', nullable=False)  
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)
    embedding_id = Column(Integer, nullable=True)
    

    # Relationships to profile data
    profile_pictures = relationship("ProfilePicture", backref="tenant_obj", cascade="all, delete-orphan")
    personal_info = relationship("PersonalInfo", uselist=False, backref="tenant_obj")
    big_five_traits = relationship("BigFiveTraits", uselist=False, backref="tenant_obj")
    mbti_traits = relationship("MBTITraits", uselist=False, backref="tenant_obj")
    psychology = relationship("Psychology", uselist=False, backref="tenant_obj")
    interests_and_hobbies = relationship("InterestsAndHobbies", uselist=False, backref="tenant_obj")
    values_beliefs_and_goals = relationship("ValuesBeliefsAndGoals", uselist=False, backref="tenant_obj")
    favorites = relationship("Favorites", uselist=False, backref="tenant_obj")
    relationship_preferences = relationship("RelationshipPreferences", uselist=False, backref="tenant_obj")
    friendship_preferences = relationship("FriendshipPreferences", uselist=False, backref="tenant_obj")
    collaboration_preferences = relationship("CollaborationPreferences", uselist=False, backref="tenant_obj")
    personal_free_form = relationship("PersonalFreeForm", uselist=False, backref="tenant_obj")
    intentions = relationship("Intentions", uselist=False, backref="tenant_obj")
    aspiration_and_reflections = relationship("AspirationAndReflections", uselist=False, backref="tenant_obj")
    ideal_characteristics = relationship("IdealCharacteristics", uselist=False, backref="tenant_obj")

    class Config:
        from_attributes = True
        
class ProfilePicture(Base):
    __tablename__ = "profile_pictures"  
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    url = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc))

class ProfilePictureCreate(BaseModel):
    url: str

class PersonalInfo(Base):
    __tablename__ = "personal_info"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    first_name = Column(String, default="")
    middle_name = Column(String, nullable=True)
    last_name = Column(String, default="")
    age = Column(JSON, default=0)
    gender = Column(String, default="")
    sexual_orientation = Column(String, nullable=True)
    location = Column(String, default="")
    relationship_status = Column(String, nullable=True)
    education = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    profile_pictures = Column(JSON, default=[])

class BigFiveTraits(Base):
    __tablename__ = "big_five_traits"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    openness = Column(JSON, default=0.0)
    conscientiousness = Column(JSON, default=0.0)
    extraversion = Column(JSON, default=0.0)
    agreeableness = Column(JSON, default=0.0)
    neuroticism = Column(JSON, default=0.0)

class MBTITraits(Base):
    __tablename__ = "mbti_traits"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    introversion = Column(Float, default=0.0)
    extraversion = Column(Float, default=0.0)
    agreeableness = Column(Float, default=0.0)
    neuroticism = Column(Float, default=0.0)

class Psychology(Base):
    __tablename__ = "psychology"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    communication_style = Column(String, nullable=True)
    conflict_resolution_style = Column(String, nullable=True)
    attachment_style = Column(String, nullable=True)
    emotional_intelligence = Column(JSON, default=0.0)
    cognitive_style = Column(String, nullable=True)
    stress_tolerance = Column(String, nullable=True)
    trusting = Column(Float, default=0.0)
    supportive = Column(Float, default=0.0)
    secure = Column(Float, default=0.0)
    anxious = Column(Float, default=0.0)
    avoidant = Column(Float, default=0.0)
    interests_visualized = Column(Float, default=0.0)
    values_visualized = Column(Float, default=0.0)
    goals_visualized = Column(Float, default=0.0)
    aspirations_visualized = Column(Float, default=0.0)

class InterestsAndHobbies(Base):
    
    __tablename__ = "interests_hobbies"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    interests = Column(JSON, default=[])
    hobbies = Column(JSON, default=[])

class ValuesBeliefsAndGoals(Base):
    __tablename__ = "values_beliefs_goals"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    values = Column(JSON, default=[])
    beliefs = Column(String, nullable=True)
    personal_goals = Column(JSON, default=[])
    professional_goals = Column(JSON, default=[])
    aspirations = Column(JSON, default=[])

class Favorites(Base):
    __tablename__ = "favorites"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    anecdotes = Column(JSON, default=[])
    quotes = Column(JSON, default=[])
    movies = Column(JSON, default=[])
    music = Column(JSON, default=[])
    art = Column(JSON, default=[])
    books = Column(JSON, default=[])
    poems = Column(JSON, default=[])
    places = Column(JSON, default=[])

class RelationshipPreferences(Base):
    __tablename__ = "relationship_preferences"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    seeking = Column(String, nullable=True)
    looking_for = Column(JSON, default=[])
    relationship_goals = Column(String, nullable=True)
    deal_breakers = Column(JSON, default=[])
    red_flags = Column(JSON, default=[])
    green_flags = Column(JSON, default=[])
    what_i_offer = Column(JSON, default=[])
    what_i_want = Column(JSON, default=[])

class FriendshipPreferences(Base):
    __tablename__ = "friendship_preferences"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    seeking = Column(String, nullable=True)
    goals = Column(String, nullable=True)
    ideal_traits = Column(JSON, default=[])
    activities = Column(JSON, default=[])

class CollaborationPreferences(Base):
    __tablename__ = "collaboration_preferences"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    seeking = Column(String, nullable=True)
    areas_of_expertise = Column(JSON, default=[])
    achievements = Column(JSON, default=[])
    ideal_collaborator_traits = Column(JSON, default=[])
    goals = Column(JSON, default=[])

class PersonalFreeForm(Base):
    __tablename__ = "personal_free_form"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    things_to_share = Column(String, nullable=True)

class Intentions(Base):
    __tablename__ = "intentions"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    romantic = Column(String, nullable=True)
    social = Column(String, nullable=True)
    professional = Column(String, nullable=True)

class AspirationAndReflections(Base):
    __tablename__ = "aspiration_and_reflections"
    id = Column(String,primary_key=True,default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    bucket_list = Column(JSON,default=[])
    life_goals = Column(JSON,default=[])
    greatest_regrets = Column(JSON,default=[])
    greatest_fears = Column(JSON,default=[])
    

class IdealCharacteristics(Base):
    __tablename__ = "ideal_characteristics"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    # Ideal Partner
    passionate = Column(Float, default=0.0)
    adventurous = Column(Float, default=0.0)
    supportive = Column(Float, default=0.0)
    # Ideal Friend
    funny = Column(Float, default=0.0)
    reliable = Column(Float, default=0.0)
    open_minded = Column(Float, default=0.0)
    # Ideal Business Partner
    innovative = Column(Float, default=0.0)
    dedicated = Column(Float, default=0.0)
    ethical = Column(Float, default=0.0)
