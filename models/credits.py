from database.session import Base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from enum import Enum as PyEnum


# Enums
class PlanType(PyEnum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class TransactionStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class APIEndpointCategory(PyEnum):
    BASIC = "basic"
    ADVANCED = "advanced"
    PREMIUM = "premium"
    AI_INTENSIVE = "ai_intensive"
 

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    plan_type = Column(Enum(PlanType), nullable=False)
    price_monthly = Column(Float, default=0.0)
    price_yearly = Column(Float, default=0.0)
    credits_included = Column(Integer, default=0) 
    max_requests_per_minute = Column(Integer, default=10)
    max_requests_per_hour = Column(Integer, default=100)
    max_requests_per_day = Column(Integer, default=1000)
    features = Column(Text)  
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    tenant = Column(Integer, nullable=False)  # Reference to your user model
    plan = Column(Integer, ForeignKey("plans.id"), nullable=False)
    credits_remaining = Column(Integer, default=0)
    credits_used_this_period = Column(Integer, default=0)
    subscription_start = Column(DateTime, default=datetime.now(timezone.utc))
    subscription_end = Column(DateTime)
    is_active = Column(Boolean, default=True)
    auto_renewal = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class CreditPurchase(Base):
    __tablename__ = "credit_purchases"
    
    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    credits_purchased = Column(Integer, nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String(50))
    transaction_id = Column(String(255), unique=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
class APIUsageLog(Base):
    __tablename__ = "api_usage_logs"
    
    id = Column(Integer, primary_key=True)
    subscription = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    endpoint = Column(String(255), nullable=False)
    credits_consumed = Column(Integer, nullable=False)
    request_timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    response_status = Column(Integer)  
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
class RateLimitLog(Base):
    __tablename__ = "rate_limit_logs"
    
    id = Column(Integer, primary_key=True)
    tenant = Column(Integer, nullable=False)
    endpoint_path = Column(String(255), nullable=False)
    requests_count = Column(Integer, default=1)
    window_start = Column(DateTime, default=datetime.now(timezone.utc))
    window_type = Column(String(20)) 
    
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    subscription = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    credits_purchased = Column(Integer, nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String(50))
    description = Column(String(255))
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


