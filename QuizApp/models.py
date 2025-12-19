from django.db import models
from django.contrib.auth.models import User

# ================================
# Category Model
# ================================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    fa_icon = models.CharField(
        max_length=50,
        default='fas fa-question',
        help_text="Font Awesome class, e.g., 'fas fa-laptop', 'fab fa-python'"
    )

    def __str__(self):
        return self.name


# ================================
# Question Model
# ================================
class Question(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    text = models.TextField()
    difficulty = models.CharField(
        max_length=10,
        choices=(("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")),
        default="easy"
    )

    def __str__(self):
        return f"{self.text[:50]}..."


# Option Model
class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        status = 'Correct' if self.is_correct else 'Wrong'
        return f"{self.text} ({status})"


# ================================
# Result Model 
# ================================
class Result(models.Model):
    # Null=True, Blank=True allows guests (unregistered users)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # NEW FIELD: Stores the name provided in the popup for guest users
    guest_name = models.CharField(max_length=100, null=True, blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)
    # Changed to models.DurationField for tracking time
    time_taken = models.DurationField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Improved string representation to prioritize guest_name
        display_name = self.guest_name if self.guest_name else (self.user.username if self.user else "Anonymous")
        return f"{display_name} - {self.category.name}: {self.score}"