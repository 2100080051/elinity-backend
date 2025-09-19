from pydantic import BaseModel, HttpUrl,Field
from datetime import datetime
from typing import Optional, List
from pydantic import EmailStr

class ProfilePictureBase(BaseModel):
    url: HttpUrl

class ProfilePictureCreate(ProfilePictureBase):
    pass

class ProfilePicture(ProfilePictureBase):
    id: str
    tenant: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class TenantSchema(BaseModel):
    id: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None 
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class PersonalInfo(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    age: int
    gender: str
    sexual_orientation: Optional[str] = None
    location: str
    relationship_status: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    profile_pictures: List[str] = []

    class Config:
        from_attributes = True

class BigFiveTraits(BaseModel):
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

    class Config:
        from_attributes = True

class MBTITraits(BaseModel):
    introversion: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    
    class Config:
        from_attributes = True
class Psychology(BaseModel): 
    attachment_style: Optional[str] = None
    emotional_intelligence: float
    cognitive_style: Optional[str] = None
    stress_tolerance: Optional[str] = None
    conflict_resolution_style: Optional[str] = None

    class Config:
        from_attributes = True

class InterestsAndHobbies(BaseModel):
    interests: List[str] = []
    hobbies: List[str] = []

    class Config:
        from_attributes = True

class ValuesBeliefsAndGoals(BaseModel):
    values: List[str] = []
    beliefs: Optional[str] = None
    personal_goals: List[str] = []
    professional_goals: List[str] = []

    class Config:
        from_attributes = True

class Favorites(BaseModel):
    anecdotes: List[str] = []
    quotes: List[str] = []
    movies: List[str] = []
    music: List[str] = []
    art: List[str] = []
    books: List[str] = []
    poems: List[str] = []
    places: List[str] = []

    class Config:
        from_attributes = True

class RelationshipPreferences(BaseModel):
    seeking: Optional[str] = None
    looking_for: List[str] = []
    relationship_goals: Optional[str] = None
    dealbreakers: List[str] = []
    what_i_offer: List[str] = []

    class Config:
        from_attributes = True

class FriendshipPreferences(BaseModel):
    seeking: Optional[str] = None
    goals: Optional[str] = None
    ideal_traits: List[str] = []
    activities: List[str] = []

    class Config:
        from_attributes = True

class CollaborationPreferences(BaseModel):
    seeking: Optional[str] = None
    areas_of_expertise: List[str] = []
    achievements: List[str] = []
    ideal_collaborator_traits: List[str] = []
    goals: List[str] = []

    class Config:
        from_attributes = True

class PersonalFreeForm(BaseModel):
    things_to_share: Optional[str] = None

    class Config:
        from_attributes = True

class Intentions(BaseModel):
    romantic: Optional[str] = None
    social: Optional[str] = None
    professional: Optional[str] = None

    class Config:
        from_attributes = True

class AspirationAndReflections(BaseModel):
    bucket_list: List[str] = []
    life_goals: List[str] = []
    greatest_regrets: List[str] = []
    greatest_fears: List[str] = []

    class Config:
        from_attributes = True

class IdealCharacteristics(BaseModel):
    passionate: float = 0.0
    adventurous: float = 0.0
    supportive: float = 0.0
    
    # Ideal Partner
    funny: float = 0.0
    reliable: float = 0.0
    open_minded: float = 0.0
    
    # Ideal Business Partner
    innovative: float = 0.0
    dedicated: float = 0.0
    ethical: float = 0.0

    class Config:
        from_attributes = True
        

class User(BaseModel):
    id: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None   
    profile_pictures: List[ProfilePicture] = []
    personal_info: Optional[PersonalInfo] = None
    big_five_traits: Optional[BigFiveTraits] = None
    mbti_traits: Optional[MBTITraits] = None
    psychology: Optional[Psychology] = None
    interests_and_hobbies: Optional[InterestsAndHobbies] = None
    values_beliefs_and_goals: Optional[ValuesBeliefsAndGoals] = None
    favorites: Optional[Favorites] = None
    relationship_preferences: Optional[RelationshipPreferences] = None
    friendship_preferences: Optional[FriendshipPreferences] = None
    collaboration_preferences: Optional[CollaborationPreferences] = None
    personal_free_form: Optional[PersonalFreeForm] = None
    intentions: Optional[Intentions] = None
    aspiration_and_reflections: Optional[AspirationAndReflections] = None
    ideal_characteristics: Optional[IdealCharacteristics] = None

    class Config:
        from_attributes = True

class RecommendedUserSchema(BaseModel):
    tenant: TenantSchema
    score: float
    ai_insight: str
     
class UserPersonaSchema(BaseModel): 
    personal_info: Optional[PersonalInfo] = Field(None, description="User's personal information")
    big_five_traits: Optional[BigFiveTraits] = Field(None, description="User's Big Five traits")
    mbti_traits: Optional[MBTITraits] = Field(None, description="User's MBTI traits")
    psychology: Optional[Psychology] = Field(None, description="User's psychology")
    interests_and_hobbies: Optional[InterestsAndHobbies] = Field(None, description="User's interests and hobbies")
    values_beliefs_and_goals: Optional[ValuesBeliefsAndGoals] = Field(None, description="User's values, beliefs, and goals")
    favorites: Optional[Favorites] = Field(None, description="User's favorites")
    relationship_preferences: Optional[RelationshipPreferences] = Field(None, description="User's relationship preferences")
    friendship_preferences: Optional[FriendshipPreferences] = Field(None, description="User's friendship preferences")
    collaboration_preferences: Optional[CollaborationPreferences] = Field(None, description="User's collaboration preferences")
    personal_free_form: Optional[PersonalFreeForm] = Field(None, description="User's personal free form")
    intentions: Optional[Intentions] = Field(None, description="User's intentions")
    aspiration_and_reflections: Optional[AspirationAndReflections] = Field(None, description="User's aspirations and reflections")
    ideal_characteristics: Optional[IdealCharacteristics] = Field(None, description="User's ideal characteristics")
 