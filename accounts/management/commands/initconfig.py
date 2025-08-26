from django.core.management.base import BaseCommand
from accounts.models import AdminConfig  # adjust if your model is elsewhere

class Command(BaseCommand):
    help = "Initialize default superadmin configuration"

    def handle(self, *args, **kwargs):
        # Set up your default values
        defaults = {
            "mailjet_api_key": "165bd0c5dc77c75cbf5728847585fda0",
            "mailjet_api_secret": "3ec59cb933761f573916f1e8f30f70df",
            "other_setting": "default-value",
        }

        # Create or update the config
        config, created = AdminConfig.objects.get_or_create(id=1, defaults=defaults)

        if not created:
            # only update missing values, keep what’s already set in DB
            for key, value in defaults.items():
                if not getattr(config, key):
                    setattr(config, key, value)
            config.save()

        self.stdout.write(self.style.SUCCESS("✅ Admin config initialized/updated."))
