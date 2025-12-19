from django.contrib import admin
from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.timezone import localtime  

from .models import Category, Question, Option, Result 


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


class OptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        correct_count = 0
        total_options = 0

        for form in self.forms:
            if form.cleaned_data.get('DELETE', False):
                continue
            total_options += 1
            if form.cleaned_data.get('is_correct'):
                correct_count += 1

        if total_options != 4:
            raise ValidationError("Each question must have exactly 4 options.")

        if correct_count != 1:
            raise ValidationError("Exactly one option must be marked as correct.")


class OptionInlineForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ("text", "is_correct")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_correct'].widget = forms.RadioSelect(
            choices=[(True, "Correct"), (False, "Incorrect")]
        )


class OptionInline(admin.TabularInline):
    model = Option
    form = OptionInlineForm
    formset = OptionInlineFormSet
    extra = 4
    min_num = 4
    max_num = 4
    can_delete = False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "category", "difficulty")
    list_filter = ("category", "difficulty")
    search_fields = ("text",)
    inlines = [OptionInline]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_display_name", 
        "category", 
        "score",
        "correct_answers", 
        "incorrect_answers",
        "format_time",
        "format_created_at"
    )
    list_filter = ("category", "created_at")
    search_fields = ("user__username", "guest_name", "category__name")

    def get_display_name(self, obj):
        if obj.guest_name:
            return f"{obj.guest_name} (Guest)"
        if obj.user:
            return obj.user.username
        return "Anonymous"

    get_display_name.short_description = 'User Name'
    get_display_name.admin_order_field = 'guest_name' 

    def format_time(self, obj):
        if not obj.time_taken:
            return '00:00'
        total_seconds = int(obj.time_taken.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"
    
    format_time.short_description = 'Time Taken (MM:SS)' 
    format_time.admin_order_field = 'time_taken'

    def format_created_at(self, obj):
        if not obj.created_at:
            return 'N/A'
        return localtime(obj.created_at).strftime("%b %d, %Y - %H:%M")  
    
    format_created_at.short_description = 'Created At'
    format_created_at.admin_order_field = 'created_at'
