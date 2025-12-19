from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Category, Question, Option, Result
from datetime import timedelta
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator


# ==============================
# BASIC STATIC VIEWS
# ==============================
def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


# ==============================
# CATEGORY VIEW
# ==============================
def categories(request):
    categories = Category.objects.all()
    return render(request, "categories.html", {"categories": categories})


# ==============================
# QUIZ VIEW – Display Quiz Questions
# ==============================
@never_cache
def quiz(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        # Capture guest name (if entered)
        guest_name = request.POST.get('name') or request.POST.get('guest_name')

        if guest_name:
            # Save guest name to session (even if logged in)
            request.session['guest_name'] = guest_name

        # Retrieve all questions in this category
        questions = category.questions.all()

        return render(request, 'quiz.html', {
            'category': category,
            'questions': questions
        })

    # Redirect to categories if accessed directly
    return redirect('categories')


# ==============================
# SUBMIT QUIZ – Process Answers
# ==============================
@never_cache
def submit_quiz(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=category_id)

        # Prevent submission if no questions exist
        if not Question.objects.filter(category=category).exists():
            return redirect('categories')

        # --- CALCULATE SCORE & TIME ---
        final_score = 0
        correct_count = 0
        incorrect_count = 0

        time_taken_seconds_str = request.POST.get('time_taken', '0')
        try:
            time_taken_seconds = float(time_taken_seconds_str)
            time_taken = timedelta(seconds=time_taken_seconds)
        except ValueError:
            time_taken = timedelta(seconds=0)

        # Evaluate each question
        for question in Question.objects.filter(category=category):
            submitted_option_id = request.POST.get(f'question_{question.id}')

            try:
                correct_option = question.options.get(is_correct=True)
            except Option.DoesNotExist:
                continue

            if submitted_option_id and int(submitted_option_id) == correct_option.id:
                correct_count += 1
                final_score += 1
            elif submitted_option_id:
                incorrect_count += 1

        # --- DETERMINE USER OR GUEST ---
        guest_name_to_save = None
        user_to_save = None

        if 'guest_name' in request.session:
            guest_name_to_save = request.session['guest_name']
            del request.session['guest_name']  # Clear after use
        elif request.user.is_authenticated:
            user_to_save = request.user

        # --- SAVE RESULT ---
        result = Result.objects.create(
            user=user_to_save,
            guest_name=guest_name_to_save,
            category=category,
            score=final_score,
            correct_answers=correct_count,
            incorrect_answers=incorrect_count,
            time_taken=time_taken,
        )

        return redirect('results', result_id=result.id)

    return redirect('categories')


# ==============================
# RESULTS VIEW
# ==============================
@never_cache
def results(request, result_id):
    result = get_object_or_404(Result, pk=result_id)
    total_questions = Question.objects.filter(category=result.category).count()

    percentage = (result.score / total_questions) * 100 if total_questions > 0 else 0

    # Format time (mm:ss)
    time_taken_seconds = result.time_taken.total_seconds()
    minutes = int(time_taken_seconds // 60)
    seconds = int(time_taken_seconds % 60)
    formatted_time = f"{minutes:02}:{seconds:02}"

    context = {
        'result': result,
        'category': result.category,
        'percentage': percentage,
        'score': result.score,
        'total': total_questions,
        'correct': result.correct_answers,
        'incorrect': result.incorrect_answers,
        'time_taken': formatted_time,
    }
    return render(request, 'results.html', context)


# ==============================
# LEADERBOARD VIEW
# ==============================
def leaderboard(request):
    all_results = Result.objects.order_by('-score', 'time_taken', '-created_at').select_related('user', 'category')

    paginator = Paginator(all_results, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'leaderboard.html', {'page_obj': page_obj})


# ==============================
# API ENDPOINTS (AJAX / JSON)
# ==============================
def quiz_data(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        questions = Question.objects.filter(category=category).prefetch_related("options")

        data = []
        for q in questions:
            options = [{"id": opt.id, "text": opt.text} for opt in q.options.all()]
            data.append({"id": q.id, "text": q.text, "options": options})

        return JsonResponse({"category": category.name, "questions": data})
    except Category.DoesNotExist:
        return JsonResponse({"error": "Category not found"}, status=404)


def get_questions(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        questions = Question.objects.filter(category=category).prefetch_related("options")

        data = []
        for q in questions:
            data.append({
                "id": q.id,
                "text": q.text,
                "difficulty": q.difficulty,
                "options": [
                    {"id": opt.id, "text": opt.text, "is_correct": opt.is_correct}
                    for opt in q.options.all()
                ],
            })

        return JsonResponse({"category": category.name, "questions": data})
    except Category.DoesNotExist:
        return JsonResponse({"error": "Category not found"}, status=404)
