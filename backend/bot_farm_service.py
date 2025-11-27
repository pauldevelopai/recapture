import random
import uuid
from datetime import datetime, timedelta
from .models import BotFarm, DisinformationCampaign

class BotFarmService:
    # In-memory storage for simulation
    _farms = []
    _campaigns = []

    @classmethod
    def initialize_data(cls):
        if cls._farms:
            return

        # Seed initial bot farms
        cls._farms = [
            BotFarm(
                id=str(uuid.uuid4()),
                name="Glacial Trolls",
                origin_country="Russia",
                network_size=15000,
                status="Active",
                primary_tactics=["Hashtag Flooding", "Fake News", "Divisive Memes"]
            ),
            BotFarm(
                id=str(uuid.uuid4()),
                name="Silk Road Cyber",
                origin_country="China",
                network_size=8500,
                status="Active",
                primary_tactics=["Reply Guy", "Narrative Shaping", "Whataboutism"]
            ),
            BotFarm(
                id=str(uuid.uuid4()),
                name="Desert Storm Net",
                origin_country="Iran",
                network_size=4200,
                status="Dormant",
                primary_tactics=["Anti-Western Rhetoric", "Religious Extremism"]
            )
        ]

        # Seed initial campaigns
        cls._campaigns = [
            DisinformationCampaign(
                id=str(uuid.uuid4()),
                name="Operation Blue Divide",
                target_demographic="Young Men (18-25)",
                narrative_goal="Increase political polarization and distrust in institutions.",
                active_platforms=["Twitter", "4chan"],
                bot_farm_id=cls._farms[0].id,
                reach_estimate=1200000,
                status="Active",
                detected_at=(datetime.now() - timedelta(days=5)).isoformat()
            ),
            DisinformationCampaign(
                id=str(uuid.uuid4()),
                name="Project Harmony",
                target_demographic="Tech Workers",
                narrative_goal="Promote specific state-sponsored tech alternatives.",
                active_platforms=["LinkedIn", "Twitter"],
                bot_farm_id=cls._farms[1].id,
                reach_estimate=450000,
                status="Active",
                detected_at=(datetime.now() - timedelta(days=12)).isoformat()
            )
        ]
        
        # Link campaigns to farms
        cls._farms[0].active_campaigns.append(cls._campaigns[0].id)
        cls._farms[1].active_campaigns.append(cls._campaigns[1].id)

    @classmethod
    def get_all_farms(cls):
        cls.initialize_data()
        return cls._farms

    @classmethod
    def get_all_campaigns(cls):
        cls.initialize_data()
        return cls._campaigns

    @classmethod
    def create_campaign(cls, name: str, target: str, goal: str, platforms: list, farm_id: str):
        cls.initialize_data()
        campaign = DisinformationCampaign(
            id=str(uuid.uuid4()),
            name=name,
            target_demographic=target,
            narrative_goal=goal,
            active_platforms=platforms,
            bot_farm_id=farm_id,
            reach_estimate=random.randint(10000, 500000),
            status="Active",
            detected_at=datetime.now().isoformat()
        )
        cls._campaigns.append(campaign)
        
        # Update farm
        for farm in cls._farms:
            if farm.id == farm_id:
                farm.active_campaigns.append(campaign.id)
                break
                
        return campaign

    @classmethod
    def simulate_activity(cls):
        """
        Randomly updates reach estimates and statuses to simulate live activity.
        """
        cls.initialize_data()
        updates = []
        for campaign in cls._campaigns:
            if campaign.status == "Active":
                growth = random.randint(100, 5000)
                campaign.reach_estimate += growth
                updates.append(f"Campaign '{campaign.name}' reach grew by {growth}")
        return updates
