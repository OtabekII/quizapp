from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('quiz-list', views.quizList, name='quizList'),
    path('quiz-detail/<int:id>/', views.quizDetail, name='quizDetail'),
    path('questionDelete/<int:id>/<int:pk>/', views.questionDelete, name='questionDelete'),
    path('optionDelete/<int:ques>/<int:option>/', views.deleteOption, name='optionDelete'),
    path('question-detail/<int:id>/', views.questionDetail, name='questionDetail'),
    path('create-quiz', views.createQuiz, name='createQuiz'),
    path('create-question/<int:id>/', views.questionCreate, name='questionCreate'),
    path('question-delete/<int:id>/', views.question_delete_view, name='questionDelete'),
    path('quiz-users/<int:quiz_id>/', views.quiz_users_view, name='quizUsers'),
    path('export-quiz-answers/<int:quiz_id>/', views.export_quiz_answers_to_excel, name='exportQuizAnswers'),
    path('export-answer-details/<int:answer_id>/', views.export_answer_detail_to_excel, name='exportAnswerDetails'),
    path('export-quiz-pdf/<int:quiz_id>/', views.render_quiz_to_pdf, name='exportQuizPDF')
]