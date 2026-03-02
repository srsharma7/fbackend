import uuid
from django.db import models
from django.db.models import Avg, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q


# Common 1-5 rating choices
RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]


class College(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Class(models.Model):
    college = models.ForeignKey(
        College, on_delete=models.CASCADE, related_name="classes"
    )
    name = models.CharField(max_length=255)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return f"{self.name} - {self.college.name}"


class FeedbackForm(models.Model):
    """
    This generates a shareable link for feedback
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def frontend_link(self):
        return f"http://localhost:3000/feedback/{self.id}"

    def __str__(self):
        return f"Feedback Form - {self.course.name}"


class Feedback(models.Model):
    form = models.ForeignKey(
        FeedbackForm, on_delete=models.CASCADE, related_name="responses"
    )

    # Rating fields (1-5)
    communication = models.IntegerField(choices=RATING_CHOICES)
    pace = models.IntegerField(choices=RATING_CHOICES)
    hands_on = models.IntegerField(choices=RATING_CHOICES)
    trainer_rating = models.IntegerField(choices=RATING_CHOICES)
    knowledge_before = models.IntegerField(choices=RATING_CHOICES)
    knowledge_after = models.IntegerField(choices=RATING_CHOICES)
    topic_rating = models.IntegerField(choices=RATING_CHOICES)

    # Text fields
    feedback = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.form.course.name}"


# class FeedbackAggregate(models.Model):
#     form = models.OneToOneField(
#         "FeedbackForm", on_delete=models.CASCADE, related_name="aggregate"
#     )

#     total_responses = models.IntegerField(default=0)

#     avg_communication = models.FloatField(default=0)
#     avg_pace = models.FloatField(default=0)
#     avg_hands_on = models.FloatField(default=0)
#     avg_trainer_rating = models.FloatField(default=0)
#     avg_topic_rating = models.FloatField(default=0)

#     avg_knowledge_before = models.FloatField(default=0)
#     avg_knowledge_after = models.FloatField(default=0)

#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Aggregate - {self.form.id}"


# @receiver(post_save, sender=Feedback)
# def update_aggregate(sender, instance, created, **kwargs):
#     if not created:
#         return

#     form = instance.form
#     responses = form.responses.all()

#     aggregate, _ = FeedbackAggregate.objects.get_or_create(form=form)

#     aggregate.total_responses = responses.count()

#     averages = responses.aggregate(
#         avg_communication=Avg("communication"),
#         avg_pace=Avg("pace"),
#         avg_hands_on=Avg("hands_on"),
#         avg_trainer_rating=Avg("trainer_rating"),
#         avg_topic_rating=Avg("topic_rating"),
#         avg_knowledge_before=Avg("knowledge_before"),
#         avg_knowledge_after=Avg("knowledge_after"),
#     )

#     for key, value in averages.items():
#         setattr(aggregate, key, value or 0)

#     aggregate.save()


class FeedbackAggregate(models.Model):
    form = models.OneToOneField(
        "FeedbackForm", on_delete=models.CASCADE, related_name="aggregate"
    )

    total_responses = models.IntegerField(default=0)

    communication_distribution = models.JSONField(default=dict)
    pace_distribution = models.JSONField(default=dict)
    hands_on_distribution = models.JSONField(default=dict)
    trainer_distribution = models.JSONField(default=dict)
    topic_distribution = models.JSONField(default=dict)

    avg_knowledge_before = models.FloatField(default=0)
    avg_knowledge_after = models.FloatField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

@receiver(post_save, sender=Feedback)
def update_aggregate(sender, instance, created, **kwargs):
    if not created:
        return

    form = instance.form
    responses = form.responses.all()

    aggregate, _ = FeedbackAggregate.objects.get_or_create(form=form)

    # Total responses
    aggregate.total_responses = responses.count()

    # -------- DISTRIBUTION FUNCTION (Optimized) --------
    def get_distribution(field_name):
        distribution = {str(i): 0 for i in range(1, 6)}

        counts = (
            responses.values(field_name)
            .annotate(count=Count(field_name))
        )

        for item in counts:
            distribution[str(item[field_name])] = item["count"]

        return distribution

    aggregate.communication_distribution = get_distribution("communication")
    aggregate.pace_distribution = get_distribution("pace")
    aggregate.hands_on_distribution = get_distribution("hands_on")
    aggregate.trainer_distribution = get_distribution("trainer_rating")
    aggregate.topic_distribution = get_distribution("topic_rating")

    # -------- AVERAGES (Single Query) --------
    averages = responses.aggregate(
        avg_knowledge_before=Avg("knowledge_before"),
        avg_knowledge_after=Avg("knowledge_after"),
    )

    aggregate.avg_knowledge_before = averages["avg_knowledge_before"] or 0
    aggregate.avg_knowledge_after = averages["avg_knowledge_after"] or 0

    aggregate.save()