from pydantic import BaseModel
from typing import Optional 
from datetime import datetime 


class PlanSchema(BaseModel):
    id: int
    name: str
    plan_type: str
    price_monthly: float
    price_yearly: float 
    credits_included: int 
    max_requests_per_minute: int
    max_requests_per_hour: int
    max_requests_per_day: int
    features: Optional[str] 
    is_active: bool
    created_at: datetime



class SubscriptionSchema(BaseModel):
    
    id: int
    tenant: int  
    plan: int
    credits_remaining: int
    credits_used_this_period: int
    subscription_start: datetime
    subscription_end: Optional[datetime]
    is_active: bool
    auto_renewal: bool
    created_at: datetime
    updated_at: datetime


class CreditPurchaseSchema(BaseModel):
    subscription_id: int
    credits_purchased: int
    amount_paid: float
    payment_method: str
    transaction_id: str
    status: str
    created_at: datetime
    

class APIUsageLogSchema(BaseModel):
    subscription: int
    endpoint: str
    credits_consumed: int
    request_timestamp: datetime
    response_status: int  
    ip_address: str
    user_agent: str
    

class RateLimitLogSchema(BaseModel):
    tenant: int
    endpoint_path: str
    requests_count: int
    window_start: datetime
    window_type: str  

    
class TransactionSchema(BaseModel):
    subscription: int
    credits_purchased: int
    amount_paid: float
    payment_method: str
    description: str
    status: str
    created_at: datetime

