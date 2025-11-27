from typing import List, Dict, Optional
import json
import uuid
from datetime import datetime
import os
from openai import OpenAI
from .database import get_db_connection
from .models import DigitalClone, CloneConversation, CloneMessage, SubjectSocialPost

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def extract_personality_traits(posts: List[SubjectSocialPost]) -> Dict:
    """
    Analyze social media posts to identify personality characteristics
    """
    if not posts:
        return {
            'traits': [],
            'values': [],
            'communication_style': ''
        }
    
    posts_text = "\n\n".join([
        f"[{post.platform} - {post.posted_at}]: {post.content}"
        for post in posts[:40]
    ])
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """Analyze these social media posts to create a personality profile.
Return a JSON object with:
1. traits: Array of personality traits (e.g., "curious", "skeptical", "rebellious", "anxious")
2. values: Array of core values and beliefs (e.g., "individualism", "justice", "loyalty")
3. communication_style: Description of how they express themselves (tone, formality, emotion)
4. worldview: Their general perspective on life, society, authority
5. emotional_state: Current emotional baseline (e.g., "frustrated", "hopeful", "angry")

Be specific and nuanced. Look for patterns in how they think and express themselves."""
                },
                {
                    "role": "user",
                    "content": f"Analyze this person's personality based on their posts:\n\n{posts_text}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error extracting personality traits: {e}")
        return {
            'traits': [],
            'values': [],
            'communication_style': 'Unable to analyze',
            'error': str(e)
        }


async def build_writing_style_model(posts: List[SubjectSocialPost]) -> Dict:
    """
    Analyze writing style including vocabulary, syntax, and tone
    """
    if not posts:
        return {}
    
    posts_text = "\n".join([post.content for post in posts[:30]])
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """Analyze the writing style in these posts.
Return a JSON object with:
1. vocabulary: Common words/phrases they use, slang, technical terms
2. sentence_structure: How they construct sentences (short/long, simple/complex)
3. tone: Overall tone (casual, serious, sarcastic, angry, etc.)
4. punctuation_style: How they use punctuation, capitalization, etc.
5. typical_expressions: Phrases or expressions they frequently use
6. emojis_used: Emoji patterns if any

This will be used to simulate their writing style accurately."""
                },
                {
                    "role": "user",
                    "content": posts_text
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error building writing style model: {e}")
        return {'error': str(e)}


async def extract_interests_and_beliefs(posts: List[SubjectSocialPost]) -> tuple[List[str], Dict]:
    """
    Extract interests and specific beliefs/opinions from posts
    """
    if not posts:
        return [], {}
    
    posts_text = "\n".join([post.content for post in posts[:35]])
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """Extract interests and beliefs from these posts.
Return a JSON object with:
1. interests: Array of topics/activities they're interested in
2. beliefs: Object mapping topics to their stated opinions/beliefs
   Example: {"climate_change": "skeptical of mainstream narrative", "government": "mistrustful"}

Be specific and capture nuance in their beliefs."""
                },
                {
                    "role": "user",
                    "content": posts_text
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('interests', []), result.get('beliefs', {})
        
    except Exception as e:
        print(f"Error extracting interests and beliefs: {e}")
        return [], {}


async def train_clone(subject_id: str) -> DigitalClone:
    """
    Train a digital clone by analyzing all available social media posts
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all posts for this subject
    cursor.execute(
        """SELECT * FROM subject_social_posts 
        WHERE subject_id = ? 
        ORDER BY posted_at DESC""",
        (subject_id,)
    )
    
    post_rows = cursor.fetchall()
    
    if not post_rows:
        # Create a pending clone instead of raising exception
        # Check if clone already exists
        cursor.execute(
            "SELECT id FROM digital_clones WHERE subject_id = ?",
            (subject_id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            return DigitalClone(
                id=existing['id'],
                subject_id=subject_id,
                personality_model=json.loads(existing['personality_model']) if existing['personality_model'] else {},
                writing_style=json.loads(existing['writing_style']) if existing['writing_style'] else {},
                interests=json.loads(existing['interests']) if existing['interests'] else [],
                beliefs=json.loads(existing['beliefs']) if existing['beliefs'] else {},
                last_trained=existing['last_trained'],
                training_post_count=existing['training_post_count'],
                status=existing['status']
            )
            
        clone_id = str(uuid.uuid4())
        cursor.execute(
            """INSERT INTO digital_clones
            (id, subject_id, personality_model, writing_style, interests, beliefs, last_trained, training_post_count, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
            (
                clone_id,
                subject_id,
                json.dumps({}),
                json.dumps({}),
                json.dumps([]),
                json.dumps({}),
                None,
                0
            )
        )
        conn.commit()
        conn.close()
        
        return DigitalClone(
            id=clone_id,
            subject_id=subject_id,
            personality_model={},
            writing_style={},
            interests=[],
            beliefs={},
            last_trained=None,
            training_post_count=0,
            status='pending'
        )
    
    # Convert to SubjectSocialPost objects
    posts = []
    for row in post_rows:
        posts.append(SubjectSocialPost(
            id=row['id'],
            subject_id=row['subject_id'],
            feed_id=row['feed_id'],
            content=row['content'],
            posted_at=row['posted_at'],
            platform=row['platform'],
            url=row['url'],
            engagement_metrics=json.loads(row['engagement_metrics']) if row['engagement_metrics'] else None,
            scraped_at=row['scraped_at']
        ))
    
    # Perform analysis
    personality = await extract_personality_traits(posts)
    writing_style = await build_writing_style_model(posts)
    interests, beliefs = await extract_interests_and_beliefs(posts)
    
    # Check if clone already exists
    cursor.execute(
        "SELECT id FROM digital_clones WHERE subject_id = ?",
        (subject_id,)
    )
    existing = cursor.fetchone()
    
    if existing:
        clone_id = existing['id']
        # Update existing clone
        cursor.execute(
            """UPDATE digital_clones 
            SET personality_model = ?, writing_style = ?, interests = ?, beliefs = ?,
                last_trained = ?, training_post_count = ?, status = 'ready'
            WHERE id = ?""",
            (
                json.dumps(personality),
                json.dumps(writing_style),
                json.dumps(interests),
                json.dumps(beliefs),
                datetime.now().isoformat(),
                len(posts),
                clone_id
            )
        )
    else:
        # Create new clone
        clone_id = str(uuid.uuid4())
        cursor.execute(
            """INSERT INTO digital_clones
            (id, subject_id, personality_model, writing_style, interests, beliefs, last_trained, training_post_count, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ready')""",
            (
                clone_id,
                subject_id,
                json.dumps(personality),
                json.dumps(writing_style),
                json.dumps(interests),
                json.dumps(beliefs),
                datetime.now().isoformat(),
                len(posts)
            )
        )
    
    conn.commit()
    conn.close()
    
    return DigitalClone(
        id=clone_id,
        subject_id=subject_id,
        personality_model=personality,
        writing_style=writing_style,
        interests=interests,
        beliefs=beliefs,
        last_trained=datetime.now().isoformat(),
        training_post_count=len(posts),
        status='ready'
    )


async def get_or_create_clone(subject_id: str) -> DigitalClone:
    """Get existing clone or create a new one if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM digital_clones WHERE subject_id = ?",
        (subject_id,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return DigitalClone(
            id=row['id'],
            subject_id=row['subject_id'],
            personality_model=json.loads(row['personality_model']) if row['personality_model'] else {},
            writing_style=json.loads(row['writing_style']) if row['writing_style'] else {},
            interests=json.loads(row['interests']) if row['interests'] else [],
            beliefs=json.loads(row['beliefs']) if row['beliefs'] else {},
            last_trained=row['last_trained'],
            training_post_count=row['training_post_count'],
            status=row['status']
        )
    else:
        # Create new clone
        return await train_clone(subject_id)


async def get_all_clones() -> List[DigitalClone]:
    """Get all digital clones"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM digital_clones")
    rows = cursor.fetchall()
    conn.close()
    
    clones = []
    for row in rows:
        clones.append(DigitalClone(
            id=row['id'],
            subject_id=row['subject_id'],
            personality_model=json.loads(row['personality_model']) if row['personality_model'] else {},
            writing_style=json.loads(row['writing_style']) if row['writing_style'] else {},
            interests=json.loads(row['interests']) if row['interests'] else [],
            beliefs=json.loads(row['beliefs']) if row['beliefs'] else {},
            last_trained=row['last_trained'],
            training_post_count=row['training_post_count'],
            status=row['status']
        ))
    return clones


async def generate_clone_response(clone: DigitalClone, message: str, conversation_history: List[CloneMessage] = None) -> str:
    """
    Generate a response from the digital clone based on their personality and writing style
    """
    if conversation_history is None:
        conversation_history = []
    
    # Build context from clone's personality
    personality_context = f"""You are simulating a young person with the following characteristics:

PERSONALITY TRAITS: {', '.join(clone.personality_model.get('traits', []))}
CORE VALUES: {', '.join(clone.personality_model.get('values', []))}
COMMUNICATION STYLE: {clone.personality_model.get('communication_style', 'casual')}
WORLDVIEW: {clone.personality_model.get('worldview', 'not specified')}
EMOTIONAL STATE: {clone.personality_model.get('emotional_state', 'neutral')}

WRITING STYLE:
- Tone: {clone.writing_style.get('tone', 'casual')}
- Sentence structure: {clone.writing_style.get('sentence_structure', 'varied')}
- Typical expressions: {', '.join(clone.writing_style.get('typical_expressions', [])[:5])}

INTERESTS: {', '.join(clone.interests[:10])}

BELIEFS:
{json.dumps(clone.beliefs, indent=2)}

CRITICAL INSTRUCTIONS:
1. Respond EXACTLY as this person would, matching their tone, vocabulary, and communication style
2. Stay true to their beliefs and worldview, even if they're skeptical or resistant
3. Be authentic to their emotional state and personality
4. Use their typical expressions and writing patterns
5. If they tend to be defensive, suspicious, or resistant to authority - reflect that
6. You are NOT trying to be helpful or agreeable - you're simulating their actual response

Respond to the following message as this person would:"""

    # Build conversation messages
    messages = [
        {"role": "system", "content": personality_context}
    ]
    
    # Add conversation history
    for msg in conversation_history[-6:]:  # Last 6 messages for context
        role = "assistant" if msg.role == "clone" else "user"
        messages.append({"role": role, "content": msg.content})
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.8,  # Higher temperature for more authentic variation
            max_tokens=300
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating clone response: {e}")
        return "I don't really want to talk about this right now."


async def evaluate_argument_effectiveness(clone: DigitalClone, argument: str, clone_response: str) -> tuple[float, List[str]]:
    """
    Evaluate how effective an argument would be on this person
    Returns: (effectiveness_score 0-100, list of suggestions for improvement)
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert at evaluating persuasive communication with at-risk youth.
Analyze the argument and the simulated response to determine effectiveness.

Return a JSON object with:
1. effectiveness_score: 0-100, where:
   - 0-20: Counterproductive, likely to increase resistance
   - 21-40: Ineffective, ignored or dismissed
   - 41-60: Neutral, acknowledged but not persuasive
   - 61-80: Somewhat effective, creates openness
   - 81-100: Highly effective, genuine engagement and reflection

2. reasoning: Brief explanation of the score

3. suggestions: Array of 3-5 specific suggestions to improve the argument, considering:
   - The person's personality, values, and communication style
   - What resonates with them vs. what triggers defensiveness
   - Alternative framing or approaches
   - Timing and emotional state considerations"""
                },
                {
                    "role": "user",
                    "content": f"""PERSONALITY PROFILE:
Traits: {', '.join(clone.personality_model.get('traits', []))}
Values: {', '.join(clone.personality_model.get('values', []))}
Worldview: {clone.personality_model.get('worldview', '')}

ARGUMENT PRESENTED:
{argument}

SIMULATED RESPONSE:
{clone_response}

Evaluate the effectiveness of this argument."""
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('effectiveness_score', 50.0), result.get('suggestions', [])
        
    except Exception as e:
        print(f"Error evaluating argument effectiveness: {e}")
        return 50.0, ["Unable to generate suggestions due to an error."]


async def chat_with_clone(clone_id: str, message: str, conversation_id: Optional[str] = None) -> Dict:
    """
    Send a message to a clone and get response with effectiveness evaluation
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get clone
    cursor.execute("SELECT * FROM digital_clones WHERE id = ?", (clone_id,))
    clone_row = cursor.fetchone()
    
    if not clone_row:
        raise Exception("Clone not found")
    
    clone = DigitalClone(
        id=clone_row['id'],
        subject_id=clone_row['subject_id'],
        personality_model=json.loads(clone_row['personality_model']) if clone_row['personality_model'] else {},
        writing_style=json.loads(clone_row['writing_style']) if clone_row['writing_style'] else {},
        interests=json.loads(clone_row['interests']) if clone_row['interests'] else [],
        beliefs=json.loads(clone_row['beliefs']) if clone_row['beliefs'] else {},
        last_trained=clone_row['last_trained'],
        training_post_count=clone_row['training_post_count'],
        status=clone_row['status']
    )
    
    # Get or create conversation
    conversation_history = []
    if conversation_id:
        cursor.execute(
            "SELECT * FROM clone_conversations WHERE id = ?",
            (conversation_id,)
        )
        conv_row = cursor.fetchone()
        if conv_row:
            conversation_history = json.loads(conv_row['conversation'])
            conversation_history = [CloneMessage(**msg) for msg in conversation_history]
    else:
        conversation_id = str(uuid.uuid4())
    
    # Generate clone response
    clone_response = await generate_clone_response(clone, message, conversation_history)
    
    # Evaluate effectiveness
    effectiveness_score, suggestions = await evaluate_argument_effectiveness(clone, message, clone_response)
    
    # Add messages to conversation
    now = datetime.now().isoformat()
    conversation_history.append(CloneMessage(role="user", content=message, timestamp=now))
    conversation_history.append(CloneMessage(role="clone", content=clone_response, timestamp=now))
    
    # Save conversation
    conversation_json = json.dumps([msg.dict() for msg in conversation_history])
    
    cursor.execute(
        """INSERT OR REPLACE INTO clone_conversations
        (id, clone_id, conversation, effectiveness_score, timestamp, notes)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (
            conversation_id,
            clone_id,
            conversation_json,
            effectiveness_score,
            now,
            None
        )
    )
    
    conn.commit()
    conn.close()
    
    return {
        'conversation_id': conversation_id,
        'clone_response': clone_response,
        'effectiveness_score': effectiveness_score,
        'suggestions': suggestions
    }


async def get_clone_conversations(clone_id: str) -> List[CloneConversation]:
    """Get all conversations for a clone"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT * FROM clone_conversations 
        WHERE clone_id = ? 
        ORDER BY timestamp DESC""",
        (clone_id,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    conversations = []
    for row in rows:
        conv_messages = json.loads(row['conversation']) if row['conversation'] else []
        conversations.append(CloneConversation(
            id=row['id'],
            clone_id=row['clone_id'],
            conversation=[CloneMessage(**msg) for msg in conv_messages],
            effectiveness_score=row['effectiveness_score'],
            timestamp=row['timestamp'],
            notes=row['notes']
        ))
    
    return conversations
