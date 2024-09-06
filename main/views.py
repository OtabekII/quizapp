from django.shortcuts import render, redirect, get_object_or_404
from main import models
from .models import Quiz, Question, Answer, AnswerDetail
from random import choice, sample
from django.http import HttpResponse
import openpyxl
from django.contrib.auth.models import User

def index(request):
    return render(request, 'index.html')


def quizList(request):
    images = [
        'https://st2.depositphotos.com/2769299/7314/i/450/depositphotos_73146775-stock-photo-a-stack-of-books-on.jpg',
        'https://img.freepik.com/free-photo/creative-composition-world-book-day_23-2148883765.jpg',
        'https://profit.pakistantoday.com.pk/wp-content/uploads/2018/04/Stack-of-books-great-education.jpg',
        'https://live-production.wcms.abc-cdn.net.au/73419a11ea13b52c6bd9c0a69c10964e?impolicy=wcms_crop_resize&cropH=1080&cropW=1918&xPos=1&yPos=0&width=862&height=485',
        'https://live-production.wcms.abc-cdn.net.au/398836216839841241467590824c5cf1?impolicy=wcms_crop_resize&cropH=2813&cropW=5000&xPos=0&yPos=0&width=862&height=485',
        'https://images.theconversation.com/files/45159/original/rptgtpxd-1396254731.jpg?ixlib=rb-4.1.0&q=45&auto=format&w=1356&h=668&fit=crop'
    ]
    
    quizes = models.Quiz.objects.filter(author=request.user)
    # images = sample(len(quizes), images)

    quizes_list = []

    for quiz in quizes:
        quiz.img = choice(images)
        quizes_list.append(quiz)

    return render(request, 'quiz-list.html', {'quizes':quizes_list})


def quizDetail(request, id):
    quiz = models.Quiz.objects.get(id=id)
    return render(request, 'quiz-detail.html', {'quiz':quiz})

def questionDelete(request, id, pk):
    models.Question.objects.get(id=id).delete()
    return redirect('quizDetail', id=pk)


def createQuiz(request):
    if request.method == 'POST':
        quiz = models.Quiz.objects.create(
            name = request.POST['name'],
            amount = request.POST['amount'],
            author = request.user
        )
        return redirect('quizDetail', quiz.id)
    return render(request, 'quiz-create.html')


def questionCreate(request, id):
    quiz = models.Quiz.objects.get(id=id)
    if request.method == 'POST':
        question_text = request.POST['name']
        true = request.POST['true']
        false_list = request.POST.getlist('false-list')

        question = models.Question.objects.create(
            name = question_text,
            quiz = quiz,
        )
        question.save()
        models.Option.objects.create(
            question = question,
            name = true,
            correct = True,
        )

        for false in false_list:
            models.Option.objects.create(
                name = false,
                question = question,
            )
        return redirect('quizList')

    return render(request, 'question-create.html', {'quiz':quiz})


def questionDetail(request, id):
    question = models.Question.objects.get(id=id)
    return render(request, 'question-detail.html', {'question':question})


def deleteOption(request, ques, option):
    question = models.Question.objects.get(id=ques)
    models.Option.objects.get(question=question, id=option).delete()
    return redirect('questionDetail', id=ques)


def delete_question_by_id(question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id
    question.delete()
    return quiz_id

# Delete question (Function-based View)
def question_delete_view(request, id):
    if request.method == 'POST':
        quiz_id = delete_question_by_id(id)
        return redirect('quizDetail', id=quiz_id)

# Helper function to get distinct users for a quiz
def get_users_by_quiz(quiz_id):
    answers = Answer.objects.filter(quiz_id=quiz_id)
    users = User.objects.filter(answer__in=answers).distinct()
    return users

# Get users and their results for a quiz
def get_user_results_for_quiz(quiz):
    answers = Answer.objects.filter(quiz=quiz)
    results = []

    for answer in answers:
        answer_details = get_answer_details(answer)
        results.append({
            'user': answer.author.username,
            'results': answer_details
        })

    return results

# Helper function to get answer details for a user
def get_answer_details(answer):
    details = AnswerDetail.objects.filter(answer=answer)
    return [{
        'question': detail.question.name,
        'correct_option': detail.question.correct_option.name if detail.question.correct_option else 'No option',
        'user_choice': detail.user_choice.name,
        'is_correct': detail.is_correct
    } for detail in details]

# View to show quiz participants and their results
def quiz_users_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    results = get_user_results_for_quiz(quiz)
    context = {'quiz': quiz, 'results': results}
    return render(request, 'quiz_users.html', context)

# Helper function to create Excel workbook for quiz answers
def create_quiz_answers_excel(quiz, answers):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Answers'

    # Headers
    sheet['A1'] = 'Author'
    sheet['B1'] = 'Start Time'
    sheet['C1'] = 'End Time'
    sheet['D1'] = 'Is Late?'

    # Data rows
    for idx, answer in enumerate(answers, start=2):
        sheet[f'A{idx}'] = answer.author.username
        sheet[f'B{idx}'] = answer.start_time.strftime("%Y-%m-%d %H:%M:%S") if answer.start_time else ''
        sheet[f'C{idx}'] = answer.end_time.strftime("%Y-%m-%d %H:%M:%S") if answer.end_time else ''
        sheet[f'D{idx}'] = 'Yes' if answer.is_late else 'No'

    return workbook

# Export quiz answers to Excel
def export_quiz_answers_to_excel(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    answers = Answer.objects.filter(quiz=quiz)
    workbook = create_quiz_answers_excel(quiz, answers)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={quiz.name}_answers.xlsx'
    workbook.save(response)
    return response

# Helper function to create Excel for answer details
def create_answer_details_excel(answer, details):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Answer Details'

    # Headers
    sheet['A1'] = 'Question'
    sheet['B1'] = 'User Choice'
    sheet['C1'] = 'Correct?'

    # Data rows
    for idx, detail in enumerate(details, start=2):
        sheet[f'A{idx}'] = detail.question.name
        sheet[f'B{idx}'] = detail.user_choice.name
        sheet[f'C{idx}'] = 'Yes' if detail.is_correct else 'No'

    return workbook

# Export answer details to Excel
def export_answer_detail_to_excel(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    answer_details = answer.answerdetail_set.all()
    workbook = create_answer_details_excel(answer, answer_details)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={answer.quiz.name}_answer_details.xlsx'
    workbook.save(response)
    return response

# Helper function to generate PDF for quiz results
def create_quiz_results_pdf(quiz, answers):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={quiz.name}_results.pdf'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Quiz Name: {quiz.name}")
    p.drawString(100, 780, f"Author: {quiz.author.username}")
    p.drawString(100, 760, "Results:")

    y = 740
    for answer in answers:
        p.drawString(100, y, f"{answer.author.username}: {'Late' if answer.is_late else 'On Time'}")
        y -= 20

    p.showPage()
    p.save()

    return response

# Export quiz results to PDF
def render_quiz_to_pdf(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    answers = Answer.objects.filter(quiz=quiz)
    return create_quiz_results_pdf(quiz, answers)