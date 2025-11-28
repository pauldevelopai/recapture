import os
import json
import uuid
from dotenv import load_dotenv
from openai import AsyncOpenAI
from .models import AnalysisResponse, ArgumentResponse
from .empathy_service import detect_empathy, detect_emotions

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print(f"DEBUG: OpenAI API Key loaded: {bool(os.getenv('OPENAI_API_KEY'))}")

async def analyze_text(text: str) -> AnalysisResponse:
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are an expert in detecting harmful content, radicalization, and extremist ideologies. 
                Analyze the input text for markers of: Incel Ideology, White Supremacy, Violent Extremism, Anti-LGBTQ+ Hate, Self-Harm.
                Return a JSON object with:
                - radicalization_score (0.0 to 1.0)
                - detected_themes (list of strings)
                - summary (brief explanation)
                """},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return AnalysisResponse(
            id=str(uuid.uuid4()),
            radicalization_score=result.get("radicalization_score", 0.0),
            detected_themes=result.get("detected_themes", []),
            summary=result.get("summary", "Analysis complete.")
        )
    except Exception as e:
        print(f"OpenAI Error: {e}")
        # Fallback to mock if API fails or key is missing
        return AnalysisResponse(
            id=str(uuid.uuid4()),
            radicalization_score=0.1,
            detected_themes=["Error: AI Analysis Failed"],
            summary=f"Could not perform AI analysis: {str(e)}"
        )

async def generate_argument(
    topic: str,
    profile: dict = None,
    history: list = None,
    authorities: list = None,
    rag_context: str = ""
) -> ArgumentResponse:
    try:
        # Analyze topic for emotional triggers
        topic_empathy = detect_empathy(topic)
        topic_emotion = detect_emotions(topic)
        
        # Construct a rich system prompt
        system_prompt = """You are an expert in de-radicalization, street epistemology, and empathetic communication. 
        Your goal is to help a young person think more clearly and critically about harmful ideologies, without feeling attacked.
        
        GUIDELINES:
        1.  **Empathy First**: Validate their feelings (e.g., "It makes sense you feel angry about...").
        2.  **Socratic Method**: Ask open-ended questions to plant seeds of doubt.
        3.  **Authority Bridging**: If trusted authorities are provided, reference them gently (e.g., "I wonder what Father John would say about...").
        4.  **Facts via Curiosity**: Introduce counter-evidence as "something interesting to consider" rather than "the truth".
        5.  **Tone**: Kind, patient, non-judgmental, clear-minded.
        """
        
        # Add empathy guidance based on topic analysis
        if topic_emotion.get("model_available"):
            dominant_emotion = topic_emotion.get("dominant_emotion", "")
            if dominant_emotion in ["anger", "fear"]:
                system_prompt += f"\n\nNOTE: The topic involves {dominant_emotion}. Acknowledge this emotion before challenging beliefs."
        
        if topic_empathy.get("distress_score", 0) > 0.5:
            system_prompt += "\n\nNOTE: This topic may be distressing. Prioritize emotional safety and support."

        # Construct the user prompt with all available context
        user_prompt = f"TOPIC/CLAIM: {topic}\n\n"

        if profile:
            user_prompt += f"SUBJECT PROFILE:\n"
            user_prompt += f"- Name: {profile.get('name', 'Unknown')}\n"
            user_prompt += f"- Age: {profile.get('age', 'Unknown')}\n"
            user_prompt += f"- Risk Level: {profile.get('risk_level', 'Unknown')}\n"
            user_prompt += f"- Notes: {profile.get('notes', '')}\n\n"

        if history:
            user_prompt += f"RECENT CONTENT HISTORY (The 'Rabbit Hole'):\n"
            for item in history[:3]: # Last 3 items
                user_prompt += f"- {item.get('timestamp')}: {item.get('content')[:100]}...\n"
            user_prompt += "\n"

        if authorities:
            user_prompt += f"TRUSTED AUTHORITIES:\n"
            for auth in authorities:
                user_prompt += f"- {auth.get('name')} ({auth.get('relation')})\n"
            user_prompt += "\n"

        if rag_context:
            user_prompt += f"FACTUAL CONTEXT & COUNTER-NARRATIVES:\n{rag_context}\n\n"

        user_prompt += """TASK:
        Generate a response strategy.
        1.  **Strategy**: Briefly explain *why* you are choosing this approach based on the profile and history.
        2.  **Script**: The actual words to say to the subject.
        3.  **Talking Points**: 3-4 key bullets for a follow-up conversation.
        
        Return JSON format: { "strategy": "...", "script": "...", "talking_points": [...] }
        """

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return ArgumentResponse(
            argument_text=f"**Strategy:** {result.get('strategy')}\n\n**Script:**\n{result.get('script')}",
            talking_points=result.get('talking_points', [])
        )
    except Exception as e:
        print(f"Error generating argument: {e}")
        return ArgumentResponse(
            argument_text=f"Error generating argument: {str(e)}",
            talking_points=["Error"]
        )

async def simulate_subject_response(
    subject_profile: dict,
    subject_history: list,
    argument_text: str
) -> str:
    """
    Simulates how the Subject (Digital Clone) would respond to the generated argument.
    """
    try:
        system_prompt = f"""You are roleplaying as a young person named {subject_profile.get('name', 'Alex')}.
        
        YOUR PROFILE:
        - Age: {subject_profile.get('age', 'Unknown')}
        - Risk Level: {subject_profile.get('risk_level', 'Unknown')}
        - Personality/Notes: {subject_profile.get('notes', '')}
        
        YOUR RECENT CONSUMPTION HISTORY (What you've been reading/watching):
        {json.dumps(subject_history[:5], indent=2)}
        
        INSTRUCTIONS:
        - Respond to the input argument as if you are this person.
        - Use the tone, slang, and attitude consistent with your profile and risk level.
        - If you are "High" risk or "Critical", be defensive, dismissive, or repeat radicalized talking points.
        - If you are "Low" risk, be more open but perhaps skeptical.
        - Keep the response relatively short (1-3 sentences).
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": argument_text}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error simulating response: {str(e)}"
