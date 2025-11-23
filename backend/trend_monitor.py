import uuid
from typing import List
from .models import DisinformationTrend, RedFlag

import uuid
import json
from typing import List
from .models import DisinformationTrend
from .database import get_db_connection

async def get_active_trends() -> List[DisinformationTrend]:
    """
    Retrieves currently active disinformation trends from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trends")
    rows = cursor.fetchall()
    conn.close()
    
    trends = []
    for row in rows:
        trends.append(DisinformationTrend(
            id=row['id'],
            topic=row['topic'],
            description=row['description'],
            severity=row['severity'],
            common_phrases=json.loads(row['common_phrases']),
            counter_arguments=json.loads(row['counter_arguments']),
            sources=json.loads(row['sources']) if row['sources'] else []
        ))
    return trends

async def add_trend(trend: DisinformationTrend):
    """
    Adds a new trend to the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()
    return trend

