import requests
import sys
import json
from datetime import datetime

class LifePlanAPITester:
    def __init__(self, base_url="https://lifeplan-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.questionnaire_id = None
        self.profile_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_submit_questionnaire(self):
        """Test questionnaire submission with sample data"""
        sample_data = {
            "energizing_activities": "coding and designing apps, solving complex problems",
            "passionate_problems": "help students learn better through technology",
            "existing_skills": ["Programming", "Design", "Teaching"],
            "weekday_hours": 4,
            "weekend_hours": 6,
            "chronotype": "Early morning",
            "morning_routine": "Coffee, meditation, planning for 30 minutes",
            "morning_routine_duration": 30,
            "reliable_habits": "3-4",
            "setback_reaction": "learn and iterate immediately",
            "yearly_goals": ["Launch online course", "Build learning app", "Grow audience"],
            "key_habit_change": "Start deep work sessions every morning",
            "main_distractions": ["Social media", "Email", "Phone notifications"],
            "commitment_level": 8
        }
        
        success, response = self.run_test(
            "Submit Questionnaire",
            "POST",
            "questionnaire",
            200,
            data=sample_data
        )
        
        if success and 'id' in response:
            self.questionnaire_id = response['id']
            print(f"   Questionnaire ID: {self.questionnaire_id}")
            return True
        return False

    def test_create_profile(self):
        """Test profile creation from questionnaire"""
        if not self.questionnaire_id:
            print("❌ Cannot test profile creation - no questionnaire ID")
            return False
            
        success, response = self.run_test(
            "Create Profile",
            "POST",
            "profile",
            200,
            params={"questionnaire_id": self.questionnaire_id}
        )
        
        if success and 'id' in response:
            self.profile_id = response['id']
            print(f"   Profile ID: {self.profile_id}")
            print(f"   Archetype: {response.get('archetype', 'N/A')}")
            print(f"   Scores: Purpose={response.get('purpose_clarity', 'N/A')}, Energy={response.get('energy_chronotype', 'N/A')}, Focus={response.get('focus_capacity', 'N/A')}")
            return True
        return False

    def test_generate_plan(self):
        """Test plan generation using Claude"""
        if not self.profile_id:
            print("❌ Cannot test plan generation - no profile ID")
            return False
            
        print("   Note: This may take 10-30 seconds for Claude to generate the plan...")
        success, response = self.run_test(
            "Generate Plan",
            "POST",
            "plan",
            200,
            params={"profile_id": self.profile_id}
        )
        
        if success:
            print(f"   Plan ID: {response.get('id', 'N/A')}")
            print(f"   Yearly Goal: {response.get('yearly_goal', 'N/A')}")
            print(f"   Pillars: {response.get('pillars', 'N/A')}")
            return True
        return False

    def test_get_plan(self):
        """Test retrieving existing plan"""
        if not self.profile_id:
            print("❌ Cannot test plan retrieval - no profile ID")
            return False
            
        success, response = self.run_test(
            "Get Plan",
            "GET",
            f"plan/{self.profile_id}",
            200
        )
        
        if success:
            print(f"   Retrieved plan with {len(response.get('habit_stack', []))} habits")
            print(f"   Time blocks: {len(response.get('time_blocks', []))}")
            return True
        return False

def main():
    print("🚀 Starting LifePlan AI Backend API Tests")
    print("=" * 50)
    
    tester = LifePlanAPITester()
    
    # Test sequence
    tests = [
        ("Root API Endpoint", tester.test_root_endpoint),
        ("Questionnaire Submission", tester.test_submit_questionnaire),
        ("Profile Creation", tester.test_create_profile),
        ("Plan Generation (Claude)", tester.test_generate_plan),
        ("Plan Retrieval", tester.test_get_plan)
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())