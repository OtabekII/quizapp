from django.urls import path
from . import views

urlpatterns = [
    path('get-quiz/<int:id>', views.getQuiz, name='getQuiz'),
    path('make-answer/<int:id>', views.makeAnswer, name='makeAnswer'),
    path('check-quiz/<int:quiz_id>/', views.check_quiz, name='check_quiz'),
    path('results/', views.result, name='results'),
    path('result-detail/<int:quiz_id>/', views.result_detail, name='result_detail'),
]