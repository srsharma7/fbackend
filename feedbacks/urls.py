from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    CollegeViewSet,
    CourseViewSet,
    ClassViewSet,
    FeedbackFormViewSet,
    FeedbackViewSet,
    DashboardView,
)

router = DefaultRouter()
router.register(r"colleges", CollegeViewSet)
router.register(r"courses", CourseViewSet)
router.register(r"classes", ClassViewSet)
router.register(r"feedback-forms", FeedbackFormViewSet)
router.register(r"feedbacks", FeedbackViewSet)

urlpatterns = [
    path("dashboard/<uuid:id>/", DashboardView.as_view())
] + router.urls
