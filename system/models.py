class EmailConfig(models.Model):
    provider = models.CharField(max_length=64, default="mailjet")
    api_key_encrypted = models.TextField()
    api_secret_encrypted = models.TextField()
    token_ttl_seconds = models.PositiveIntegerField(default=120)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)