from fastapi import APIRouter, Depends,status
from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload
from database.session import get_db
from models.user import Tenant, PersonalInfo, BigFiveTraits,MBTITraits, Psychology, InterestsAndHobbies, ValuesBeliefsAndGoals, Favorites, RelationshipPreferences, FriendshipPreferences, CollaborationPreferences, PersonalFreeForm, Intentions, IdealCharacteristics, AspirationAndReflections
from schemas.user import (
    User as UserSchema,
    PersonalInfo as PersonalInfoSchema,
    BigFiveTraits as BigFiveTraitsSchema,
    MBTITraits as MBTITraitsSchema,
    Psychology as PsychologySchema,
    InterestsAndHobbies as InterestsAndHobbiesSchema,
    ValuesBeliefsAndGoals as ValuesBeliefsAndGoalsSchema,
    Favorites as FavoritesSchema,
    RelationshipPreferences as RelationshipPreferencesSchema,
    FriendshipPreferences as FriendshipPreferencesSchema,
    CollaborationPreferences as CollaborationPreferencesSchema,
    PersonalFreeForm as PersonalFreeFormSchema,
    Intentions as IntentionsSchema,
    IdealCharacteristics as IdealCharacteristicsSchema,
    AspirationAndReflections as AspirationAndReflectionsSchema,
)
from schemas.user import ProfilePicture as ProfilePictureSchema, ProfilePictureCreate
from models.user import ProfilePicture as ProfilePictureModel
from typing import List
from utils.token import get_current_user


class RouteTagEnum:
    ME = "Me"
    PUBLIC_USER = "Public User"
    
class RouteEnum:
    ME = "/me"
    PUBLIC_USER = "/public/users"

class UserRouteEnum:
    PROFILE_PICTURE = "/profile-picture"
    PERSONAL_INFO = "/personal-info/"
    BIG_FIVE_TRAITS = "/big-five-traits/"
    MBTI_TRAITS = "/mbti-traits/"
    PSYCHOLOGY = "/psychology/"
    INTERESTS_AND_HOBBIES = "/interests-and-hobbies/"
    VALUES_BELIEFS_AND_GOALS = "/values-beliefs-and-goals/"
    FAVORITES = "/favorites/"
    RELATIONSHIP_PREFERENCES = "/relationship-preferences/"
    FRIENDSHIP_PREFERENCES = "/friendship-preferences/"
    COLLABORATION_PREFERENCES = "/collaboration-preferences/"
    PERSONAL_FREE_FORM = "/personal-free-form/"  
    INTENTIONS = "/intentions/"
    IDEAL_CHARACTERISTICS = "/ideal-characteristics/"
    ASPIRATION_AND_REFLECTIONS = "/aspiration-and-reflections/"

router = APIRouter(dependencies=[Depends(get_current_user)], tags=[RouteTagEnum.ME])


# Me
@router.get(RouteEnum.ME, response_model=UserSchema, tags=[RouteTagEnum.ME])
async def read_users_me(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Return the authenticated user's profile with related data"""
    user = (
        db.query(Tenant)
        .options(
            selectinload(Tenant.profile_pictures),
            selectinload(Tenant.personal_info),
            selectinload(Tenant.big_five_traits),
            selectinload(Tenant.mbti_traits),
            selectinload(Tenant.psychology),
            selectinload(Tenant.interests_and_hobbies),
            selectinload(Tenant.values_beliefs_and_goals),
            selectinload(Tenant.favorites),
            selectinload(Tenant.relationship_preferences),
            selectinload(Tenant.friendship_preferences),
            selectinload(Tenant.collaboration_preferences),
            selectinload(Tenant.personal_free_form),
            selectinload(Tenant.intentions),
            selectinload(Tenant.aspiration_and_reflections),
            selectinload(Tenant.ideal_characteristics),
        )
        .filter(Tenant.id == current_user.id)
        .first()
    )
    return user


@router.put(RouteEnum.ME + UserRouteEnum.PERSONAL_INFO, response_model=PersonalInfoSchema, tags=[RouteTagEnum.ME])
async def update_personal_info(req: PersonalInfoSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Create or update personal info"""
    obj = db.query(PersonalInfo).filter(PersonalInfo.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = PersonalInfo(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.BIG_FIVE_TRAITS, response_model=BigFiveTraitsSchema, tags=[RouteTagEnum.ME])
async def update_big_five(req: BigFiveTraitsSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(BigFiveTraits).filter(BigFiveTraits.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = BigFiveTraits(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.MBTI_TRAITS, response_model=MBTITraitsSchema, tags=[RouteTagEnum.ME])
async def update_mbti(req: MBTITraitsSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(MBTITraits).filter(MBTITraits.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = MBTITraits(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.PSYCHOLOGY, response_model=PsychologySchema, tags=[RouteTagEnum.ME])
async def update_psychology(req: PsychologySchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(Psychology).filter(Psychology.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = Psychology(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.INTERESTS_AND_HOBBIES, response_model=InterestsAndHobbiesSchema, tags=[RouteTagEnum.ME])
async def update_interests(req: InterestsAndHobbiesSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(InterestsAndHobbies).filter(InterestsAndHobbies.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = InterestsAndHobbies(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.VALUES_BELIEFS_AND_GOALS, response_model=ValuesBeliefsAndGoalsSchema, tags=[RouteTagEnum.ME])
async def update_values(req: ValuesBeliefsAndGoalsSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(ValuesBeliefsAndGoals).filter(ValuesBeliefsAndGoals.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = ValuesBeliefsAndGoals(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.FAVORITES, response_model=FavoritesSchema, tags=[RouteTagEnum.ME])
async def update_favorites(req: FavoritesSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(Favorites).filter(Favorites.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = Favorites(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.RELATIONSHIP_PREFERENCES, response_model=RelationshipPreferencesSchema, tags=[RouteTagEnum.ME])
async def update_relationships(req: RelationshipPreferencesSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(RelationshipPreferences).filter(RelationshipPreferences.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = RelationshipPreferences(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.FRIENDSHIP_PREFERENCES, response_model=FriendshipPreferencesSchema, tags=[RouteTagEnum.ME])
async def update_friendships(req: FriendshipPreferencesSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(FriendshipPreferences).filter(FriendshipPreferences.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = FriendshipPreferences(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.COLLABORATION_PREFERENCES, response_model=CollaborationPreferencesSchema, tags=[RouteTagEnum.ME])
async def update_collaborations(req: CollaborationPreferencesSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(CollaborationPreferences).filter(CollaborationPreferences.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = CollaborationPreferences(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.PERSONAL_FREE_FORM, response_model=PersonalFreeFormSchema, tags=[RouteTagEnum.ME])
async def update_freeform(req: PersonalFreeFormSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(PersonalFreeForm).filter(PersonalFreeForm.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = PersonalFreeForm(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.INTENTIONS, response_model=IntentionsSchema, tags=[RouteTagEnum.ME])
async def update_intentions(req: IntentionsSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(Intentions).filter(Intentions.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = Intentions(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.IDEAL_CHARACTERISTICS, response_model=IdealCharacteristicsSchema, tags=[RouteTagEnum.ME])
async def update_ideal_characteristics(req: IdealCharacteristicsSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(IdealCharacteristics).filter(IdealCharacteristics.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = IdealCharacteristics(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put(RouteEnum.ME + UserRouteEnum.ASPIRATION_AND_REFLECTIONS, response_model=AspirationAndReflectionsSchema, tags=[RouteTagEnum.ME])
async def update_aspiration_and_reflections(req: AspirationAndReflectionsSchema, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    obj = db.query(AspirationAndReflections).filter(AspirationAndReflections.tenant == current_user.id).first()
    if obj:
        for k, v in req.model_dump().items(): setattr(obj, k, v)
    else:
        obj = AspirationAndReflections(tenant=current_user.id, **req.model_dump())
        db.add(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.post(RouteEnum.ME + UserRouteEnum.PROFILE_PICTURE, response_model=ProfilePictureSchema, status_code=status.HTTP_201_CREATED, tags=[RouteTagEnum.ME])
async def add_profile_picture(pic: ProfilePictureCreate, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    # Create and persist picture
    db_pic = ProfilePictureModel(
        tenant=current_user.id,
        url=str(pic.url),
        uploaded_at=datetime.now(timezone.utc)
    )
    db.add(db_pic)
    db.commit(); db.refresh(db_pic)
    return db_pic

@router.get(RouteEnum.ME + UserRouteEnum.PROFILE_PICTURE, response_model=List[ProfilePictureSchema], tags=[RouteTagEnum.ME])
async def list_profile_pictures(tenant_id: str, db: Session = Depends(get_db)):
    pics = db.query(ProfilePictureModel).filter(ProfilePictureModel.tenant == tenant_id).all()
    return pics 

## Public User
@router.get("/{user_id}", response_model=UserSchema, tags=[RouteTagEnum.PUBLIC_USER])
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Retrieve a single user by ID with related data"""
    user = (
        db.query(Tenant)
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
            selectinload(Tenant.aspiration_and_reflections),
            selectinload(Tenant.ideal_characteristics),
        )
        .filter(Tenant.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user



