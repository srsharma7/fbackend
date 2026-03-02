from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import College, Course, Class, FeedbackForm, Feedback
from .serializers import (
    CollegeSerializer,
    CourseSerializer,
    ClassSerializer,
    FeedbackFormSerializer,
    FeedbackSerializer,
)

from rest_framework.generics import RetrieveAPIView
from .models import FeedbackAggregate
from .serializers import FeedbackAggregateSerializer


class CollegeViewSet(viewsets.ModelViewSet):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer


class FeedbackFormViewSet(viewsets.ModelViewSet):
    queryset = FeedbackForm.objects.all()
    serializer_class = FeedbackFormSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        form_id = request.data.get("form")

        try:
            form = FeedbackForm.objects.get(id=form_id, is_active=True)
        except FeedbackForm.DoesNotExist:
            return Response(
                {"error": "Invalid or inactive feedback form"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(form=form)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardView(RetrieveAPIView):
    queryset = FeedbackAggregate.objects.all()
    serializer_class = FeedbackAggregateSerializer
    lookup_field = "form__id"
    lookup_url_kwarg = "id"