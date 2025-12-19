# QuizApp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Static pages
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),

    # Category and Quiz flow
    path('categories/', views.categories, name='categories'),
    path('quiz/<int:category_id>/', views.quiz, name='quiz'),
    
    # Submission and Results
    path('submit/<int:category_id>/', views.submit_quiz, name='submit_quiz'),
    
    # NEW LINE ADDED: This resolves the NoReverseMatch error
    path('results/<int:result_id>/', views.results, name='results'),
    
    # Leaderboard
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # API Endpoints (Optional, based on your previous code)
    path('api/quiz_data/<int:category_id>/', views.quiz_data, name='quiz_data'),
    path('api/get_questions/<int:category_id>/', views.get_questions, name='get_questions'),
]