SYSTEM_PROMPT = """You are a helpful AI assistant for university students.
You help with:
- Course information and schedules
- Assignment deadlines
- Campus facilities and locations
- General academic queries

Be concise, friendly, and accurate in your responses."""

INTENT_CLASSIFICATION_PROMPT = """Classify the user's intent into one of these categories:
- course_info: Questions about courses, schedules, professors
- deadline: Questions about assignment or exam deadlines
- location: Questions about campus locations and facilities
- general: General questions or chitchat
- unknown: Cannot determine intent

User query: {query}

Return only the category name."""

RESPONSE_GENERATION_PROMPT = """Based on the conversation context and user query, generate a helpful response.

Context: {context}
User Query: {query}

Generate a concise and helpful response."""
