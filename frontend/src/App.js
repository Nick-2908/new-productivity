import React, { useState } from 'react';
import './App.css';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Checkbox } from './components/ui/checkbox';
import { Slider } from './components/ui/slider';
import { Progress } from './components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { ArrowRight, Target, Clock, Brain, Lightbulb, TrendingUp, CheckCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Hero Section Component
const HeroSection = ({ onStartQuestionnaire }) => (
  <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
    {/* Background Image with Overlay */}
    <div 
      className="absolute inset-0 bg-cover bg-center"
      style={{
        backgroundImage: `url('https://images.unsplash.com/photo-1483058712412-4245e9b90334?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwyfHxwcm9kdWN0aXZpdHl8ZW58MHx8fHwxNzU3MTIzODAxfDA&ixlib=rb-4.1.0&q=85')`
      }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900/90 via-slate-800/85 to-slate-900/90"></div>
    </div>
    
    {/* Hero Content */}
    <div className="relative z-10 max-w-6xl mx-auto px-6 text-center">
      <div className="space-y-8">
        <h1 className="text-5xl md:text-7xl font-bold text-white leading-tight">
          Transform Your Life with
          <span className="block bg-gradient-to-r from-orange-400 via-amber-400 to-yellow-400 bg-clip-text text-transparent">
            AI-Powered Coaching
          </span>
        </h1>
        
        <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
          Get personalized roadmaps based on proven principles from Ikigai, Atomic Habits, Deep Work, and more. 
          Build lasting habits and achieve your most ambitious goals.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center pt-8">
          <Button 
            onClick={onStartQuestionnaire}
            size="lg"
            className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white px-8 py-4 text-lg font-semibold rounded-full transform hover:scale-105 transition-all duration-300 shadow-xl"
          >
            Start Your Journey <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
          
          <div className="flex items-center space-x-4 text-slate-300">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span>12 Key Questions</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span>5 Minutes</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    {/* Floating Elements */}
    <div className="absolute top-20 left-10 w-16 h-16 bg-orange-400/20 rounded-full blur-xl animate-bounce"></div>
    <div className="absolute bottom-20 right-10 w-20 h-20 bg-amber-400/20 rounded-full blur-xl animate-pulse"></div>
  </div>
);

// Questionnaire Component
const Questionnaire = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    energizing_activities: '',
    passionate_problems: '',
    existing_skills: [],
    weekday_hours: 2,
    weekend_hours: 4,
    chronotype: '',
    morning_routine: '',
    morning_routine_duration: null,
    reliable_habits: '',
    setback_reaction: '',
    yearly_goals: ['', '', ''],
    key_habit_change: '',
    main_distractions: [],
    commitment_level: 7
  });

  const questions = [
    {
      id: 'energizing_activities',
      title: 'What activities make you feel energized and absorbed for hours?',
      type: 'textarea',
      placeholder: 'Describe activities where you lose track of time...'
    },
    {
      id: 'passionate_problems',
      title: 'What problems are you passionate about solving?',
      type: 'textarea',
      placeholder: 'What issues or challenges do you care deeply about?'
    },
    {
      id: 'existing_skills',
      title: 'What skills do you already have that you\'d like to use or build?',
      type: 'multi-select',
      options: ['Writing', 'Design', 'Programming', 'Teaching', 'Leadership', 'Analysis', 'Creative', 'Technical', 'Communication', 'Strategy']
    },
    {
      id: 'time_availability',
      title: 'How many hours can you realistically devote to focused work?',
      type: 'dual-slider'
    },
    {
      id: 'chronotype',
      title: 'When are you naturally most alert?',
      type: 'select',
      options: ['Early morning', 'Late morning', 'Afternoon', 'Evening', 'Night']
    },
    {
      id: 'morning_routine',
      title: 'Do you currently do a morning routine?',
      type: 'textarea',
      placeholder: 'Describe your morning routine or write "No" if you don\'t have one...'
    },
    {
      id: 'reliable_habits',
      title: 'How many existing daily habits do you reliably keep?',
      type: 'select',
      options: ['0', '1-2', '3-4', '5+']
    },
    {
      id: 'setback_reaction',
      title: 'How do you react to setbacks?',
      type: 'select',
      options: ['give up', 'try again same way', 'adjust approach and try again', 'learn and iterate immediately']
    },
    {
      id: 'yearly_goals',
      title: 'What are 3 outcomes you want to achieve in 12 months?',
      type: 'triple-input'
    },
    {
      id: 'key_habit_change',
      title: 'What single habit change would make the largest difference?',
      type: 'textarea',
      placeholder: 'Describe the one habit that would transform your productivity...'
    },
    {
      id: 'main_distractions',
      title: 'What distractions are your biggest time sinks?',
      type: 'multi-select',
      options: ['Social media', 'Meetings', 'Noise', 'Multitasking', 'Email', 'Phone notifications', 'Web browsing', 'TV/streaming']
    },
    {
      id: 'commitment_level',
      title: 'On a scale 1–10, how committed are you to following a new plan?',
      type: 'slider'
    }
  ];

  const updateFormData = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      submitQuestionnaire();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const submitQuestionnaire = async () => {
    try {
      const response = await axios.post(`${API}/questionnaire`, formData);
      onComplete(response.data.id);
    } catch (error) {
      console.error('Error submitting questionnaire:', error);
    }
  };

  const renderQuestion = (question) => {
    switch (question.type) {
      case 'textarea':
        return (
          <Textarea
            value={formData[question.id] || ''}
            onChange={(e) => updateFormData(question.id, e.target.value)}
            placeholder={question.placeholder}
            className="min-h-32"
          />
        );

      case 'select':
        return (
          <Select value={formData[question.id]} onValueChange={(value) => updateFormData(question.id, value)}>
            <SelectTrigger>
              <SelectValue placeholder="Select an option..." />
            </SelectTrigger>
            <SelectContent>
              {question.options.map((option) => (
                <SelectItem key={option} value={option}>{option}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case 'multi-select':
        return (
          <div className="grid grid-cols-2 gap-3">
            {question.options.map((option) => (
              <div key={option} className="flex items-center space-x-2">
                <Checkbox
                  id={option}
                  checked={formData[question.id]?.includes(option) || false}
                  onCheckedChange={(checked) => {
                    const current = formData[question.id] || [];
                    if (checked) {
                      updateFormData(question.id, [...current, option]);
                    } else {
                      updateFormData(question.id, current.filter(item => item !== option));
                    }
                  }}
                />
                <Label htmlFor={option}>{option}</Label>
              </div>
            ))}
          </div>
        );

      case 'dual-slider':
        return (
          <div className="space-y-6">
            <div>
              <Label>Weekday hours: {formData.weekday_hours}</Label>
              <Slider
                value={[formData.weekday_hours]}
                onValueChange={(value) => updateFormData('weekday_hours', value[0])}
                max={12}
                min={0}
                step={1}
                className="mt-2"
              />
            </div>
            <div>
              <Label>Weekend hours: {formData.weekend_hours}</Label>
              <Slider
                value={[formData.weekend_hours]}
                onValueChange={(value) => updateFormData('weekend_hours', value[0])}
                max={16}
                min={0}
                step={1}
                className="mt-2"
              />
            </div>
          </div>
        );

      case 'triple-input':
        return (
          <div className="space-y-4">
            {formData.yearly_goals.map((goal, index) => (
              <Input
                key={index}
                value={goal}
                onChange={(e) => {
                  const newGoals = [...formData.yearly_goals];
                  newGoals[index] = e.target.value;
                  updateFormData('yearly_goals', newGoals);
                }}
                placeholder={`Goal ${index + 1}...`}
              />
            ))}
          </div>
        );

      case 'slider':
        return (
          <div>
            <div className="flex justify-between text-sm text-muted-foreground mb-2">
              <span>Not committed</span>
              <span className="font-semibold text-lg">{formData.commitment_level}</span>
              <span>Absolutely committed</span>
            </div>
            <Slider
              value={[formData.commitment_level]}
              onValueChange={(value) => updateFormData('commitment_level', value[0])}
              max={10}
              min={1}
              step={1}
            />
          </div>
        );

      default:
        return null;
    }
  };

  const currentQuestion = questions[currentStep];
  const progress = ((currentStep + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-8">
      <div className="max-w-2xl mx-auto px-6">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-slate-800">Discover Your Path</h2>
            <Badge variant="outline">{currentStep + 1} of {questions.length}</Badge>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">{currentQuestion.title}</CardTitle>
            <CardDescription>Take your time to give thoughtful answers</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {renderQuestion(currentQuestion)}
          </CardContent>
        </Card>

        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 0}
          >
            Previous
          </Button>
          <Button onClick={handleNext}>
            {currentStep === questions.length - 1 ? 'Complete Assessment' : 'Next'}
            <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

// Results Component
const Results = ({ questionnaireId }) => {
  const [profile, setProfile] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    const generateResults = async () => {
      try {
        // Create profile
        const profileResponse = await axios.post(`${API}/profile?questionnaire_id=${questionnaireId}`);
        setProfile(profileResponse.data);

        // Generate plan
        const planResponse = await axios.post(`${API}/plan?profile_id=${profileResponse.data.id}`);
        setPlan(planResponse.data);
      } catch (error) {
        console.error('Error generating results:', error);
      } finally {
        setLoading(false);
      }
    };

    generateResults();
  }, [questionnaireId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <h3 className="text-xl font-semibold text-slate-800">Crafting Your Personalized Plan...</h3>
          <p className="text-slate-600">Analyzing your responses and designing your roadmap</p>
        </div>
      </div>
    );
  }

  if (!profile || !plan) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center text-red-600">
              <h3 className="font-semibold">Something went wrong</h3>
              <p>Please try again</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-8">
      <div className="max-w-6xl mx-auto px-6">
        {/* Profile Overview */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-orange-400 to-amber-400 rounded-full">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-2xl">Your Productivity Profile</CardTitle>
                <CardDescription>Archetype: <strong>{profile.archetype}</strong></CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{profile.purpose_clarity}</div>
                <div className="text-sm text-slate-600">Purpose Clarity</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-amber-600">{profile.energy_chronotype}</div>
                <div className="text-sm text-slate-600">Energy & Timing</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-emerald-600">{profile.focus_capacity}</div>
                <div className="text-sm text-slate-600">Focus Capacity</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{profile.habit_foundation}</div>
                <div className="text-sm text-slate-600">Habit Foundation</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{profile.mindset_resilience}</div>
                <div className="text-sm text-slate-600">Mindset Resilience</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-pink-600">{profile.skill_trajectory}</div>
                <div className="text-sm text-slate-600">Skill Trajectory</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Personalized Plan */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="weekly">Weekly Plan</TabsTrigger>
            <TabsTrigger value="habits">Habits</TabsTrigger>
            <TabsTrigger value="schedule">Schedule</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5" />
                    <span>Yearly Goal</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg font-medium text-slate-800">{plan.yearly_goal}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Lightbulb className="w-5 h-5" />
                    <span>Three Pillars</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {plan.pillars.map((pillar, index) => (
                      <li key={index} className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span>{pillar}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle>Monthly Focus</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-700">{plan.monthly_focus}</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="weekly">
            <Card>
              <CardHeader>
                <CardTitle>Weekly Template</CardTitle>
                <CardDescription>Your optimized weekly structure</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(plan.weekly_template).map(([day, activity]) => (
                    <div key={day} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                      <div className="font-medium text-slate-800">{day}</div>
                      <div className="text-slate-600">{activity}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="habits">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="w-5 h-5" />
                  <span>Habit Stack</span>
                </CardTitle>
                <CardDescription>Micro-habits designed for lasting change</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {plan.habit_stack.map((habit, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="font-semibold text-slate-800">{habit.habit}</div>
                      <div className="text-sm text-slate-600 mt-1">
                        <strong>Cue:</strong> {habit.cue} • <strong>Time:</strong> {habit.time}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="schedule">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Clock className="w-5 h-5" />
                    <span>Time Blocks</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {plan.time_blocks.map((block, index) => (
                      <div key={index} className="p-3 bg-orange-50 rounded-lg">
                        <div className="font-medium text-orange-800">{block.name}</div>
                        <div className="text-sm text-orange-600">{block.time} • {block.frequency}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Daily Template</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(plan.daily_template).map(([period, activity]) => (
                      <div key={period} className="p-3 bg-slate-50 rounded-lg">
                        <div className="font-medium capitalize text-slate-800">{period}</div>
                        <div className="text-sm text-slate-600">{activity}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Accountability */}
        <Card>
          <CardHeader>
            <CardTitle>Accountability Steps</CardTitle>
            <CardDescription>Stay on track with these check-in points</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              {plan.accountability_steps.map((step, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span className="text-green-800">{step}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Justification */}
        <Card>
          <CardHeader>
            <CardTitle>Why This Plan Works for You</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-700 leading-relaxed">{plan.justification}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('hero'); // hero, questionnaire, results
  const [questionnaireId, setQuestionnaireId] = useState(null);

  const handleStartQuestionnaire = () => {
    setCurrentView('questionnaire');
  };

  const handleQuestionnaireComplete = (id) => {
    setQuestionnaireId(id);
    setCurrentView('results');
  };

  return (
    <div className="App">
      {currentView === 'hero' && (
        <HeroSection onStartQuestionnaire={handleStartQuestionnaire} />
      )}
      
      {currentView === 'questionnaire' && (
        <Questionnaire onComplete={handleQuestionnaireComplete} />
      )}
      
      {currentView === 'results' && questionnaireId && (
        <Results questionnaireId={questionnaireId} />
      )}
    </div>
  );
}

export default App;