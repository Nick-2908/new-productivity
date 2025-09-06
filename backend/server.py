from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize LLM Chat
def get_llm_chat():
    return LlmChat(
        api_key=os.environ.get('EMERGENT_LLM_KEY'),
        session_id=str(uuid.uuid4()),
        system_message="""You are an evidence-based productivity coach synthesizing ideas from Ikigai, 5AM Club, Atomic Habits, Deep Work, and Designing Your Life. 

Produce concise, actionable Year/Monthly/Weekly/Daily plans based on a 6-axis user profile. Output must be in structured JSON format.

Focus on creating progressive, achievable plans that build momentum. Keep language encouraging and pragmatic."""
    ).with_model("anthropic", "claude-3-7-sonnet-20250219")

# Define Models
class QuestionnaireAnswer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Q1: What activities make you feel energized and absorbed for hours?
    energizing_activities: str
    
    # Q2: What problems are you passionate about solving?
    passionate_problems: str
    
    # Q3: What skills do you already have that you'd like to use or build? (pick up to 3)
    existing_skills: List[str]
    
    # Q4: How many hours per weekday and weekend can you realistically devote to focused work?
    weekday_hours: int
    weekend_hours: int
    
    # Q5: When are you naturally most alert?
    chronotype: str  # Early morning, Late morning, Afternoon, Evening, Night
    
    # Q6: Do you currently do a morning routine? If yes, list key elements and duration.
    morning_routine: str
    morning_routine_duration: Optional[int] = None  # in minutes
    
    # Q7: How many existing daily habits do you reliably keep?
    reliable_habits: str  # 0, 1-2, 3-4, 5+
    
    # Q8: How do you react to setbacks?
    setback_reaction: str  # give up, try again same way, adjust approach and try again, learn and iterate immediately
    
    # Q9: What are 3 outcomes you want to achieve in 12 months?
    yearly_goals: List[str]
    
    # Q10: What single habit change would make the largest difference?
    key_habit_change: str
    
    # Q11: What distractions are your biggest time sinks?
    main_distractions: List[str]
    
    # Q12: On a scale 1–10, how committed are you to following a new plan?
    commitment_level: int
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    questionnaire_id: str
    
    # 6-axis scoring (0-100)
    purpose_clarity: int  # From Q2 + Q9
    energy_chronotype: int  # From Q5 + Q6 + Q4
    focus_capacity: int  # From Q1 + Q4 + Q11
    habit_foundation: int  # From Q7 + Q10
    mindset_resilience: int  # From Q8 + Q12
    skill_trajectory: int  # From Q3 + Q9
    
    archetype: str  # Purpose-driven, Exploratory, Foundation-building
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PersonalizedPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    
    yearly_goal: str
    pillars: List[str]  # 3 main pillars
    monthly_focus: str
    weekly_template: Dict[str, Any]
    daily_template: Dict[str, Any]
    habit_stack: List[Dict[str, Any]]
    time_blocks: List[Dict[str, Any]]
    accountability_steps: List[str]
    justification: str
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Scoring Functions
def calculate_scores(answers: QuestionnaireAnswer) -> Dict[str, int]:
    """Calculate 6-axis scores from questionnaire answers"""
    
    # Purpose clarity (Q2 + Q9)
    purpose_score = 0
    # Check for purpose keywords in problems and goals
    purpose_keywords = ['help', 'solve', 'create', 'build', 'improve', 'teach', 'mentor', 'impact']
    combined_text = (answers.passionate_problems + " " + " ".join(answers.yearly_goals)).lower()
    purpose_matches = sum(1 for keyword in purpose_keywords if keyword in combined_text)
    purpose_score = min(100, purpose_matches * 20 + len(answers.yearly_goals) * 15)
    
    # Energy & Chronotype (Q5 + Q6 + Q4)
    energy_score = 0
    chronotype_scores = {
        'Early morning': 90,
        'Late morning': 75,
        'Afternoon': 60,
        'Evening': 45,
        'Night': 30
    }
    energy_score += chronotype_scores.get(answers.chronotype, 50)
    
    # Add points for existing morning routine
    if answers.morning_routine.strip() and answers.morning_routine.lower() != 'no':
        energy_score += 20
    
    # Adjust for available time
    total_weekly_time = (answers.weekday_hours * 5) + (answers.weekend_hours * 2)
    if total_weekly_time >= 25:
        energy_score += 10
    elif total_weekly_time >= 15:
        energy_score += 5
    
    energy_score = min(100, energy_score)
    
    # Focus capacity (Q1 + Q4 + Q11)
    focus_score = 0
    focus_keywords = ['coding', 'writing', 'design', 'research', 'study', 'create', 'build', 'analyze']
    activities_text = answers.energizing_activities.lower()
    focus_matches = sum(1 for keyword in focus_keywords if keyword in activities_text)
    focus_score += focus_matches * 15
    
    # Time availability bonus
    if answers.weekday_hours >= 4:
        focus_score += 30
    elif answers.weekday_hours >= 2:
        focus_score += 20
    elif answers.weekday_hours >= 1:
        focus_score += 10
    
    # Distraction penalty
    high_distraction_penalty = len(answers.main_distractions) * 5
    focus_score = max(20, min(100, focus_score - high_distraction_penalty))
    
    # Habit foundation (Q7 + Q10)
    habit_score = 0
    habit_mapping = {
        '0': 10,
        '1-2': 35,
        '3-4': 65,
        '5+': 90
    }
    habit_score += habit_mapping.get(answers.reliable_habits, 35)
    
    # Bonus for specific habit change idea
    if answers.key_habit_change.strip() and len(answers.key_habit_change.strip()) > 10:
        habit_score += 15
    
    habit_score = min(100, habit_score)
    
    # Mindset resilience (Q8 + Q12)
    mindset_score = 0
    setback_scores = {
        'give up': 20,
        'try again same way': 40,
        'adjust approach and try again': 75,
        'learn and iterate immediately': 95
    }
    mindset_score += setback_scores.get(answers.setback_reaction, 50)
    
    # Commitment level bonus
    commitment_bonus = (answers.commitment_level - 5) * 5
    mindset_score += commitment_bonus
    
    mindset_score = max(10, min(100, mindset_score))
    
    # Skill trajectory (Q3 + Q9)
    skill_score = 0
    skill_score += len(answers.existing_skills) * 20  # Up to 60 points for 3 skills
    
    # Check if goals align with skills
    skills_text = " ".join(answers.existing_skills).lower()
    goals_text = " ".join(answers.yearly_goals).lower()
    alignment_keywords = ['design', 'code', 'write', 'teach', 'manage', 'create', 'build']
    
    skill_alignment = 0
    for keyword in alignment_keywords:
        if keyword in skills_text and keyword in goals_text:
            skill_alignment += 10
    
    skill_score += min(40, skill_alignment)
    skill_score = min(100, skill_score)
    
    return {
        'purpose_clarity': purpose_score,
        'energy_chronotype': energy_score,
        'focus_capacity': focus_score,
        'habit_foundation': habit_score,
        'mindset_resilience': mindset_score,
        'skill_trajectory': skill_score
    }

def determine_archetype(scores: Dict[str, int]) -> str:
    """Determine user archetype based on scores"""
    purpose = scores['purpose_clarity']
    energy = scores['energy_chronotype']
    focus = scores['focus_capacity']
    habits = scores['habit_foundation']
    mindset = scores['mindset_resilience']
    
    if purpose >= 70 and energy >= 70 and focus >= 60:
        return "Purpose-driven Achiever"
    elif habits < 40 and mindset >= 60:
        return "Foundation Builder"
    else:
        return "Strategic Explorer"

async def generate_personalized_plan(profile: UserProfile, answers: QuestionnaireAnswer) -> Dict[str, Any]:
    """Generate personalized plan using Claude"""
    
    # Prepare context for Claude
    user_context = f"""
User Profile Analysis:
- Purpose Clarity: {profile.purpose_clarity}/100
- Energy & Chronotype: {profile.energy_chronotype}/100
- Focus Capacity: {profile.focus_capacity}/100
- Habit Foundation: {profile.habit_foundation}/100
- Mindset Resilience: {profile.mindset_resilience}/100
- Skill Trajectory: {profile.skill_trajectory}/100
- Archetype: {profile.archetype}

User Responses:
- Energizing Activities: {answers.energizing_activities}
- Passionate Problems: {answers.passionate_problems}
- Existing Skills: {', '.join(answers.existing_skills)}
- Available Time: {answers.weekday_hours}h weekdays, {answers.weekend_hours}h weekends
- Natural Alert Time: {answers.chronotype}
- Morning Routine: {answers.morning_routine}
- Current Habits: {answers.reliable_habits}
- Setback Response: {answers.setback_reaction}
- 12-Month Goals: {', '.join(answers.yearly_goals)}
- Key Habit Change: {answers.key_habit_change}
- Main Distractions: {', '.join(answers.main_distractions)}
- Commitment Level: {answers.commitment_level}/10

Create a comprehensive productivity roadmap with:
1. One clear yearly goal
2. Three supporting pillars
3. Monthly focus theme
4. Weekly schedule template
5. Daily routine structure
6. Habit stack (3-5 micro-habits)
7. Specific time blocks based on their chronotype
8. Accountability measures

Format as JSON with these exact keys: yearly_goal, pillars, monthly_focus, weekly_template, daily_template, habit_stack, time_blocks, accountability_steps, justification
"""

    try:
        chat = get_llm_chat()
        user_message = UserMessage(text=user_context)
        
        response = await chat.send_message(user_message)
        
        # Try to parse JSON response
        import json
        try:
            plan_data = json.loads(response)
            return plan_data
        except json.JSONDecodeError:
            # Fallback plan if JSON parsing fails
            return {
                "yearly_goal": f"Achieve meaningful progress in {answers.yearly_goals[0] if answers.yearly_goals else 'personal development'}",
                "pillars": ["Skill Development", "Habit Formation", "Focus Optimization"],
                "monthly_focus": "Building Foundation",
                "weekly_template": {
                    "Monday": "Deep work session",
                    "Tuesday": "Skill practice",
                    "Wednesday": "Deep work session", 
                    "Thursday": "Review and adjust",
                    "Friday": "Creative work",
                    "Saturday": "Learning and exploration",
                    "Sunday": "Planning and reflection"
                },
                "daily_template": {
                    "morning": "Routine + Planning",
                    "deep_work": "Focused sessions",
                    "afternoon": "Tasks and meetings",
                    "evening": "Reflection + Preparation"
                },
                "habit_stack": [
                    {"habit": "Morning planning", "cue": "After coffee", "time": "5 minutes"},
                    {"habit": "Focus session", "cue": "After morning planning", "time": "25 minutes"},
                    {"habit": "Evening reflection", "cue": "Before dinner", "time": "5 minutes"}
                ],
                "time_blocks": [
                    {"name": "Deep Work", "time": f"{answers.chronotype} - 90 minutes", "frequency": "Daily"},
                    {"name": "Skill Practice", "time": "30 minutes", "frequency": "3x/week"}
                ],
                "accountability_steps": [
                    "Weekly review of goals",
                    "Daily habit tracking",
                    "Monthly progress assessment"
                ],
                "justification": f"Plan tailored for {profile.archetype} with focus on building habits and leveraging {answers.chronotype} energy."
            }
            
    except Exception as e:
        logging.error(f"Error generating plan: {e}")
        raise HTTPException(status_code=500, detail="Error generating personalized plan")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "LifePlan AI - Productivity Coaching API"}

@api_router.post("/questionnaire", response_model=QuestionnaireAnswer)
async def submit_questionnaire(answers: QuestionnaireAnswer):
    """Submit questionnaire answers"""
    try:
        # Prepare for MongoDB
        answer_dict = answers.dict()
        answer_dict['created_at'] = answer_dict['created_at'].isoformat()
        
        await db.questionnaire_answers.insert_one(answer_dict)
        return answers
    except Exception as e:
        logging.error(f"Error saving questionnaire: {e}")
        raise HTTPException(status_code=500, detail="Error saving questionnaire")

@api_router.post("/profile", response_model=UserProfile) 
async def create_profile(questionnaire_id: str):
    """Create user profile from questionnaire answers"""
    try:
        # Get questionnaire answers
        answer_doc = await db.questionnaire_answers.find_one({"id": questionnaire_id})
        if not answer_doc:
            raise HTTPException(status_code=404, detail="Questionnaire not found")
        
        # Convert back from MongoDB format
        if isinstance(answer_doc['created_at'], str):
            answer_doc['created_at'] = datetime.fromisoformat(answer_doc['created_at'])
            
        answers = QuestionnaireAnswer(**answer_doc)
        
        # Calculate scores
        scores = calculate_scores(answers)
        archetype = determine_archetype(scores)
        
        # Create profile
        profile = UserProfile(
            questionnaire_id=questionnaire_id,
            purpose_clarity=scores['purpose_clarity'],
            energy_chronotype=scores['energy_chronotype'], 
            focus_capacity=scores['focus_capacity'],
            habit_foundation=scores['habit_foundation'],
            mindset_resilience=scores['mindset_resilience'],
            skill_trajectory=scores['skill_trajectory'],
            archetype=archetype
        )
        
        # Save to database
        profile_dict = profile.dict()
        profile_dict['created_at'] = profile_dict['created_at'].isoformat()
        
        await db.user_profiles.insert_one(profile_dict)
        return profile
        
    except Exception as e:
        logging.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail="Error creating profile")

@api_router.post("/plan", response_model=PersonalizedPlan)
async def generate_plan(profile_id: str):
    """Generate personalized plan for user profile"""
    try:
        # Get profile
        profile_doc = await db.user_profiles.find_one({"id": profile_id})
        if not profile_doc:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        # Convert from MongoDB format
        if isinstance(profile_doc['created_at'], str):
            profile_doc['created_at'] = datetime.fromisoformat(profile_doc['created_at'])
        profile = UserProfile(**profile_doc)
        
        # Get questionnaire answers
        answer_doc = await db.questionnaire_answers.find_one({"id": profile.questionnaire_id})
        if isinstance(answer_doc['created_at'], str):
            answer_doc['created_at'] = datetime.fromisoformat(answer_doc['created_at'])
        answers = QuestionnaireAnswer(**answer_doc)
        
        # Generate plan
        plan_data = await generate_personalized_plan(profile, answers)
        
        # Create plan object
        plan = PersonalizedPlan(
            profile_id=profile_id,
            yearly_goal=plan_data['yearly_goal'],
            pillars=plan_data['pillars'],
            monthly_focus=plan_data['monthly_focus'],
            weekly_template=plan_data['weekly_template'],
            daily_template=plan_data['daily_template'],
            habit_stack=plan_data['habit_stack'],
            time_blocks=plan_data['time_blocks'],
            accountability_steps=plan_data['accountability_steps'],
            justification=plan_data['justification']
        )
        
        # Save to database
        plan_dict = plan.dict()
        plan_dict['created_at'] = plan_dict['created_at'].isoformat()
        
        await db.personalized_plans.insert_one(plan_dict)
        return plan
        
    except Exception as e:
        logging.error(f"Error generating plan: {e}")
        raise HTTPException(status_code=500, detail="Error generating plan")

@api_router.get("/plan/{profile_id}", response_model=PersonalizedPlan)
async def get_plan(profile_id: str):
    """Get existing plan for profile"""
    try:
        plan_doc = await db.personalized_plans.find_one({"profile_id": profile_id})
        if not plan_doc:
            raise HTTPException(status_code=404, detail="Plan not found")
            
        # Convert from MongoDB format
        if isinstance(plan_doc['created_at'], str):
            plan_doc['created_at'] = datetime.fromisoformat(plan_doc['created_at'])
            
        return PersonalizedPlan(**plan_doc)
        
    except Exception as e:
        logging.error(f"Error retrieving plan: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving plan")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()