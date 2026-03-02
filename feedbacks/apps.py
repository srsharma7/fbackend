from django.apps import AppConfig


class FeedbacksConfig(AppConfig):
    name = "feedbacks"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import feedbacks.signals
