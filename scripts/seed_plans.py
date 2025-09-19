import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.credits import Plan, PlanType
from database.session import Session

# Configuration for default plans
DEFAULT_PLANS = [
    {
        "name": "Free",
        "plan_type": PlanType.FREE,
        "price_monthly": 0.0,
        "price_yearly": 0.0,
        "credits_included": 100,
        "max_requests_per_minute": 5,
        "max_requests_per_hour": 50,
        "max_requests_per_day": 200,
        "features": '["Basic API access", "Community support"]'
    },
    {
        "name": "Basic",
        "plan_type": PlanType.BASIC,
        "price_monthly": 9.99,
        "price_yearly": 99.99,
        "credits_included": 1000,
        "max_requests_per_minute": 20,
        "max_requests_per_hour": 500,
        "max_requests_per_day": 5000,
        "features": '["All Basic features", "Email support", "Higher rate limits"]'
    },
    {
        "name": "Premium",
        "plan_type": PlanType.PREMIUM,
        "price_monthly": 29.99,
        "price_yearly": 299.99,
        "credits_included": 5000,
        "max_requests_per_minute": 100,
        "max_requests_per_hour": 2000,
        "max_requests_per_day": 20000,
        "features": '["All Basic features", "Priority support", "Advanced endpoints", "Analytics dashboard"]'
    },
    {
        "name": "Enterprise",
        "plan_type": PlanType.ENTERPRISE,
        "price_monthly": 99.99,
        "price_yearly": 999.99,
        "credits_included": 20000,
        "max_requests_per_minute": 500,
        "max_requests_per_hour": 10000,
        "max_requests_per_day": 100000,
        "features": '["All Premium features", "24/7 support", "Custom integrations", "SLA guarantee"]'
    }
]

 
def seed_default_plans():
    # Create a new session
    db = Session()
    try:
        print("Checking for existing plans...")
        # Check if plans already exist
        existing_plans = db.query(Plan).count()
        if existing_plans > 0:
            print("Plans already exist. Skipping seeding.")
            return

        print("Seeding default plans...")
        for plan_data in DEFAULT_PLANS:
            plan = Plan(**plan_data)
            db.add(plan)
            print(f"Added plan: {plan_data['name']}")
        
        db.commit()
        print(f"Successfully seeded {len(DEFAULT_PLANS)} default plans")
    except Exception as e:
        db.rollback()
        print(f"Error seeding plans: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_default_plans()