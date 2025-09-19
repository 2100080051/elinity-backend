import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
from faker import Faker
from passlib.hash import bcrypt as _bcrypt
from database.session import Session
from models.user import (
    Tenant, ProfilePicture, PersonalInfo, BigFiveTraits,MBTITraits, Psychology,
    InterestsAndHobbies, ValuesBeliefsAndGoals, Favorites,
    RelationshipPreferences, FriendshipPreferences,
    CollaborationPreferences, PersonalFreeForm, Intentions,
    IdealCharacteristics, AspirationAndReflections
)

faker = Faker()
session = Session()

EMAIL_DOMAINS = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com']
COUNTRY_CODES = ['+1', '+44', '+61', '+91']
GENDERS = ['Male', 'Female']
ORIENTATIONS = ['Heterosexual', 'Homosexual', 'Bisexual', 'Other']
STATUSES = ['Single', 'Married', 'Dating', 'Complicated']
EDUCATIONS = ['High School', 'Bachelors', 'Masters', 'PhD']
OCCUPATIONS = ['Engineer', 'Artist', 'Teacher', 'Doctor', 'Lawyer', 'Student']

for _ in range(300):
    # Tenant
    username = faker.unique.user_name()
    email = f"{username}@{random.choice(EMAIL_DOMAINS)}"
    phone = random.choice(COUNTRY_CODES) + str(faker.random_number(digits=10, fix_len=True))
    password = _bcrypt.hash('Password123!')
    tenant = Tenant(email=email, phone=phone, password=password)
    session.add(tenant)
    session.flush()  # assign tenant.id

    # Profile Pictures
    for _ in range(random.randint(1, 3)):
        pic = ProfilePicture(
            tenant=tenant.id,
            url=f'https://picsum.photos/seed/{tenant.id}-{_}/200'
        )
        session.add(pic)

    # Personal Info
    personal = PersonalInfo(
        tenant=tenant.id,
        first_name=faker.first_name(),
        middle_name=faker.first_name() if random.random() < 0.3 else None,
        last_name=faker.last_name(),
        age=faker.random_int(min=18, max=70),
        gender=random.choice(GENDERS),
        sexual_orientation=random.choice(ORIENTATIONS),
        location=faker.city(),
        relationship_status=random.choice(STATUSES),
        education=random.choice(EDUCATIONS),
        occupation=random.choice(OCCUPATIONS)
    )
    session.add(personal)

    # Big Five Traits
    traits = BigFiveTraits(
        tenant=tenant.id,
        openness=round(random.random(), 2),
        conscientiousness=round(random.random(), 2),
        extraversion=round(random.random(), 2),
        agreeableness=round(random.random(), 2),
        neuroticism=round(random.random(), 2)
    )
    session.add(traits)
    
    mbti = MBTITraits(
        tenant=tenant.id,
        introversion=round(random.random()*10, 2),
        extraversion=round(random.random()*10, 2),
        agreeableness=round(random.random()*10, 2),
        neuroticism=round(random.random()*10, 2)
    )
    session.add(mbti)

    # Psychology
    psychology = Psychology(
        tenant=tenant.id,
        attachment_style=random.choice(['Secure','Avoidant','Anxious']),
        emotional_intelligence=round(random.random(), 2),
        cognitive_style=random.choice(['Analytical','Creative','Pragmatic']),
        stress_tolerance=random.choice(['High','Medium','Low']),
        conflict_resolution_style=random.choice(['Collaborative','Compromising','Avoiding'])
    )
    session.add(psychology)

    # Interests and Hobbies
    ih = InterestsAndHobbies(
        tenant=tenant.id,
        interests=faker.words(nb=3),
        hobbies=faker.words(nb=3)
    )
    session.add(ih)

    # Values, Beliefs and Goals
    vbg = ValuesBeliefsAndGoals(
        tenant=tenant.id,
        values=faker.words(nb=3),
        beliefs=faker.sentence(),
        personal_goals=faker.words(nb=2),
        professional_goals=faker.words(nb=2)
    )
    session.add(vbg)

    # Favorites
    fav = Favorites(
        tenant=tenant.id,
        anecdotes=[faker.sentence() for _ in range(2)],
        quotes=[faker.sentence() for _ in range(2)],
        movies=[faker.word() for _ in range(2)],
        music=[faker.word() for _ in range(2)],
        art=[faker.word() for _ in range(2)],
        books=[faker.word() for _ in range(2)],
        poems=[faker.word() for _ in range(2)],
        places=[faker.city() for _ in range(2)]
    )
    session.add(fav)

    # Relationship Preferences
    rp = RelationshipPreferences(
        tenant=tenant.id,
        seeking=random.choice(STATUSES),
        looking_for=faker.words(nb=2),
        relationship_goals=faker.sentence(),
        deal_breakers=faker.words(nb=2),
        red_flags=faker.words(nb=2),
        green_flags=faker.words(nb=2),
        what_i_offer=faker.words(nb=2),
        what_i_want=faker.words(nb=2)
    )
    session.add(rp)

    # Friendship Preferences
    fp = FriendshipPreferences(
        tenant=tenant.id,
        seeking=random.choice(STATUSES),
        goals=faker.sentence(),
        ideal_traits=faker.words(nb=2),
        activities=faker.words(nb=2)
    )
    session.add(fp)

    # Collaboration Preferences
    cp = CollaborationPreferences(
        tenant=tenant.id,
        seeking=random.choice(['Professional','Volunteer','Academic']),
        areas_of_expertise=faker.words(nb=2),
        achievements=[faker.sentence() for _ in range(2)],
        ideal_collaborator_traits=faker.words(nb=2),
        goals=faker.words(nb=2)
    )
    session.add(cp)

    # Personal Free Form
    pff = PersonalFreeForm(
        tenant=tenant.id,
        things_to_share=faker.sentence()
    )
    session.add(pff)

    # Intentions
    intent = Intentions(
        tenant=tenant.id,
        romantic=random.choice(['Yes','No']),
        social=random.choice(['Yes','No']),
        professional=random.choice(['Yes','No'])
    )
    session.add(intent) 
    
    # Ideal Characteristics
    ideal = IdealCharacteristics(
        tenant=tenant.id,
        passionate=round(random.random() * 10, 2),
        adventurous=round(random.random() * 10, 2),
        supportive=round(random.random() * 10, 2),
        funny=round(random.random() * 10, 2),
        reliable=round(random.random() * 10, 2),
        open_minded=round(random.random() * 10, 2),
        innovative=round(random.random() * 10, 2),
        dedicated=round(random.random() * 10, 2),
        ethical=round(random.random() * 10, 2),
    )
    session.add(ideal)

    # Aspiration and Reflections
    aspiration = AspirationAndReflections(
        tenant=tenant.id,
        bucket_list=[faker.sentence() for _ in range(2)],
        life_goals=[faker.sentence() for _ in range(2)],
        greatest_regrets=[faker.sentence() for _ in range(2)],
        greatest_fears=[faker.sentence() for _ in range(2)],
    )
    session.add(aspiration)

    session.commit()

print('Seeded 300 tenants with associated profiles.')