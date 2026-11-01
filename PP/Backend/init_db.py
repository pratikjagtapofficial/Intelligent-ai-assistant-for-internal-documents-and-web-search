
from database import Base, engine
import models  # Registers the Conversation and Message models

Base.metadata.create_all(bind=engine)

print("Conversation and message tables created successfully!")
