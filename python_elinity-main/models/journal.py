# flowchart TD
#     A[User Opens Chat] --> B[Load Chat History]
#     B --> C[Load Both User Profiles]
#     C --> D[Initialize AI Assistant]
#     D --> E[AI Generates Ice Breakers]
#     E --> F[Display Chat Interface]
    
#     F --> G{User Input Type}
#     G -->|Text| H[Process Text Message]
#     G -->|Voice| I[Record Voice Message]
    
#     I --> J[Convert to Text]
#     J --> H
#     H --> K[Store Message in Chat DB]
    
#     K --> L[AI Analysis]
#     L --> M{AI Action}
#     M -->|Observe| N[Continue Monitoring]
#     M -->|Suggest| O[Generate Contextual Suggestion]
#     M -->|Interject| P[Insert AI Message in Chat]
    
#     O --> Q[Show Subtle Suggestion to User]
#     Q --> R{User Accepts?}
#     R -->|Yes| S[Convert to Message]
#     R -->|No| T[Discard Suggestion]
    
#     S --> K
#     P --> K
#     N --> F
#     T --> F

from database.session import Base
from sqlalchemy import Column, String, ForeignKey
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime

def gen_uuid():
    return str(uuid.uuid4())


class Journal(Base):
    __tablename__ = "journals"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    media = Column(String, nullable=True) # url of media file
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Journal {self.id}>"
    
    class Config:
        from_attributes = True
    
    
    