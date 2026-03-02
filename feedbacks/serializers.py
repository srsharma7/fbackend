from rest_framework import serializers
from .models import College, Course, Class, FeedbackForm, Feedback, FeedbackAggregate


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"


class FeedbackFormSerializer(serializers.ModelSerializer):
    frontend_link = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackForm
        fields = "__all__"

    def get_frontend_link(self, obj):
        return obj.frontend_link()


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"


class FeedbackAggregateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackAggregate
        fields = "__all__"