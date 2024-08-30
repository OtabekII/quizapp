from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from main import models
from django.utils import timezone


def getQuiz(request, id):
    quiz = models.Quiz.objects.get(id=id)
    return render(request, 'answer/get-quiz.html', {'quiz':quiz})

def makeAnswer(request, id):
    quiz = models.Quiz.objects.get(id=id)
    answer = models.Answer.objects.create(quiz=quiz, author=request.user)
    for key, value in request.POST.items():
        if key.isdigit():
            models.AnswerDetail.objects.create(
                answer=answer, 
                question=models.Question.objects.get(id=int(key)), 
                user_choice=models.Option.objects.get(id=int(value)))
    return redirect('getQuiz', quiz.id)


@login_required
def check_quiz(request, quiz_id):
    try:
        quiz = models.Quiz.objects.get(id=quiz_id)
    except models.Quiz.DoesNotExist:
        return redirect('quiz_not_found')

    user = request.user
    answer, created = models.Answer.objects.get_or_create(quiz=quiz, author=user)
    
    if created:
        answer.start_time = timezone.now()

    models.AnswerDetail.objects.filter(answer=answer).delete()

    for question in quiz.questions.all():
        selected_option_id = request.POST.get(f'question_{question.id}')
        if selected_option_id:
            try:
                selected_option = models.Option.objects.get(id=selected_option_id)
            except models.Option.DoesNotExist:
                continue

            models.AnswerDetail.objects.create(
                answer=answer,
                question=question,
                user_choice=selected_option,
                correct=selected_option.correct
            )

    answer.end_time = timezone.now()
    answer.save()

    return redirect('result_detail', quiz_id=quiz.id)

@login_required
def result(request):
    quizzes = models.Quiz.objects.filter(author=request.user)
    results = []

    for quiz in quizzes:
        total_questions = quiz.questions_count
        answer_details = models.AnswerDetail.objects.filter(answer__quiz=quiz)
        correct_answers_count = answer_details.filter(correct=True).count()
        incorrect_answers_count = total_questions - correct_answers_count
        percentage_correct = (correct_answers_count / total_questions) * 100 if total_questions else 0

        results.append({
            'quiz': quiz,
            'questions_count': total_questions,
            'correct_answers_count': correct_answers_count,
            'incorrect_answers_count': incorrect_answers_count,
            'percentage_correct': percentage_correct,
        })

    return render(request, 'result.html', {'results': results, 'quizzes': quizzes})

@login_required
def result_detail(request, quiz_id):
    try:
        quiz = models.Quiz.objects.get(id=quiz_id)
        answer = models.Answer.objects.get(quiz=quiz, author=request.user)
    except (models.Quiz.DoesNotExist, models.Answer.DoesNotExist):
        return redirect('quiz_not_found')

    answer_details = models.AnswerDetail.objects.filter(answer=answer)

    correct_count = 0
    total_questions = answer_details.count()
    results = []

    for detail in answer_details:
        is_correct = detail.correct
        if is_correct:
            correct_count += 1
        results.append({
            'question': detail.question,
            'user_choice': detail.user_choice,
            'is_correct': is_correct,
            'correct': detail.question.correct_option.name,
        })

    correct_percentage = (correct_count / total_questions) * 100 if total_questions else 0

    context = {
        'quiz': quiz,
        'results': results,
        'percentage_correct': correct_percentage,
    }
    return render(request, 'result_detail.html', context)