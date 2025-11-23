import asyncio
import uuid
from backend.database import init_db, get_db_connection
from backend.models import DisinformationTrend
import json

# Real-world Harmful / Radicalization Trends
HARMFUL_TRENDS = [
    DisinformationTrend(
        id=str(uuid.uuid4()),
        topic="Incel Ideology / Misogyny",
        description="Ideology promoting hatred of women, male supremacy, and justifying violence against 'Chads' and 'Stacys'.",
        severity="Critical",
        common_phrases=[
            "Blackpill", 
            "Femoid", 
            "Foid", 
            "Stacy", 
            "Chad", 
            "It's over", 
            "Looksmaxxing", 
            "Hypergamy",
            "Beta uprising"
        ],
        counter_arguments=[
            "Women are individuals with their own agency, not objects.", 
            "Relationships are built on mutual respect, not biological determinism.", 
            "Seeking mental health support and community outside of echo chambers is vital."
        ],
        sources=["4chan /r9k/", "Incel Forums", "Manosphere Blogs"]
    ),
    DisinformationTrend(
        id=str(uuid.uuid4()),
        topic="White Supremacy / Great Replacement",
        description="Racist conspiracy theory alleging a plot to replace white populations with non-white immigrants.",
        severity="Critical",
        common_phrases=[
            "Great Replacement", 
            "White Genocide", 
            "You will not replace us", 
            "Diversity is a code word for anti-white", 
            "14 words", 
            "Globalist agenda"
        ],
        counter_arguments=[
            "Demographic changes are natural and not a coordinated plot.", 
            "Diversity strengthens societies economically and culturally.", 
            "Migration is driven by complex geopolitical factors, not a conspiracy."
        ],
        sources=["Stormfront", "Telegram Channels", "Gab"]
    ),
    DisinformationTrend(
        id=str(uuid.uuid4()),
        topic="Violent Extremism / Accelerationism",
        description="Ideology advocating for the collapse of society through violence to build a new ethnostate or order.",
        severity="Critical",
        common_phrases=[
            "Accelerationism", 
            "Boogaloo", 
            "Day of the Rope", 
            "Siege culture", 
            "Total collapse", 
            "Race war"
        ],
        counter_arguments=[
            "Violence destroys communities and solves nothing.", 
            "Democratic processes are the only legitimate way to effect change.", 
            "Extremist groups exploit vulnerable individuals for their own power."
        ],
        sources=["Terrorgram", "Dark Web Forums", "Encrypted Chats"]
    ),
    DisinformationTrend(
        id=str(uuid.uuid4()),
        topic="Anti-LGBTQ+ Hate",
        description="Narratives demonizing LGBTQ+ individuals, often framing them as 'groomers' or a danger to children.",
        severity="High",
        common_phrases=[
            "Groomer", 
            "Ok groomer", 
            "Gender ideology", 
            "Trans agenda", 
            "Protect the children (co-opted)", 
            "Biological reality"
        ],
        counter_arguments=[
            "LGBTQ+ people exist in every culture and history.", 
            "Gender identity is a deeply personal and valid experience.", 
            "Inclusivity reduces harm and suicide rates among youth."
        ],
        sources=["Twitter/X", "Libs of TikTok", "Far-right Media"]
    ),
    DisinformationTrend(
        id=str(uuid.uuid4()),
        topic="Self-Harm / Suicide Promotion",
        description="Online communities that encourage or romanticize self-harm and suicide.",
        severity="Critical",
        common_phrases=[
            "Shtwt", 
            "Meanspo", 
            "Thinspo", 
            "Final exit", 
            "Cuts", 
            "Beans"
        ],
        counter_arguments=[
            "Help is available and recovery is possible.", 
            "You are not alone; reach out to a crisis line.", 
            "Your life has value and meaning."
        ],
        sources=["Twitter/X (Shtwt)", "Tumblr", "Private Discords"]
    )
]

def seed():
    print("Initializing database...")
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing data (removing Flat Earth etc.)
    cursor.execute("DELETE FROM trends")
    
    print("Seeding HARMFUL / RADICALIZATION trends...")
    for trend in HARMFUL_TRENDS:
        cursor.execute(
            "INSERT INTO trends (id, topic, description, severity, common_phrases, counter_arguments, sources) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                trend.id,
                trend.topic,
                trend.description,
                trend.severity,
                json.dumps(trend.common_phrases),
                json.dumps(trend.counter_arguments),
                json.dumps(trend.sources)
            )
        )
        print(f"Added: {trend.topic}")
    
    conn.commit()
    conn.close()
    print("Database seeded with THREATS successfully.")

if __name__ == "__main__":
    seed()
