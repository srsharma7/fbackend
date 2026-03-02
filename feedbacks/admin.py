from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg

from .models import College, Course, Class, FeedbackForm, Feedback


# ----------------------------
# College Admin
# ----------------------------
@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# ----------------------------
# Course Admin
# ----------------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# ----------------------------
# Class Admin
# ----------------------------
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "college")
    list_filter = ("college",)
    search_fields = ("name",)
    filter_horizontal = ("courses",)


# ----------------------------
# Inline Feedback (inside form)
# ----------------------------
class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0
    readonly_fields = (
        "communication",
        "pace",
        "hands_on",
        "trainer_rating",
        "knowledge_before",
        "knowledge_after",
        "topic_rating",
        "feedback",
        "suggestions",
        "submitted_at",
    )
    can_delete = False


# ----------------------------
# Feedback Form Admin
# ----------------------------
@admin.register(FeedbackForm)
class FeedbackFormAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "college",
        "course",
        "class_name",
        "is_active",
        "created_at",
        "total_responses",
        "average_trainer_rating",
        "frontend_link_clickable",
    )

    list_filter = ("college", "course", "class_name", "is_active")
    search_fields = ("college__name", "course__name", "class_name__name")
    readonly_fields = ("created_at", "frontend_link_clickable")

    inlines = [FeedbackInline]

    def frontend_link_clickable(self, obj):
        url = obj.frontend_link()
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)

    frontend_link_clickable.short_description = "Frontend Link"

    def total_responses(self, obj):
        return obj.responses.count()

    def average_trainer_rating(self, obj):
        avg = obj.responses.aggregate(Avg("trainer_rating"))["trainer_rating__avg"]
        return round(avg, 2) if avg else 0

    average_trainer_rating.short_description = "Avg Trainer Rating"


# ----------------------------
# Feedback Admin
# ----------------------------
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "form",
        "trainer_rating",
        "communication",
        "pace",
        "hands_on",
        "topic_rating",
        "submitted_at",
    )

    list_filter = (
        "form__college",
        "form__course",
        "form__class_name",
        "trainer_rating",
        "communication",
    )

    search_fields = (
        "form__college__name",
        "form__course__name",
        "feedback",
        "suggestions",
    )

    readonly_fields = (
        "form",
        "communication",
        "pace",
        "hands_on",
        "trainer_rating",
        "knowledge_before",
        "knowledge_after",
        "topic_rating",
        "feedback",
        "suggestions",
        "submitted_at",
    )

    def has_add_permission(self, request):
        return False  # Prevent manual admin creation

    def has_delete_permission(self, request, obj=None):
        return True  # Allow delete if needed
