from django.db import models
from django.utils.translation import gettext_lazy as _

class Keyword(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ContentItem(models.Model):
    title = models.CharField(max_length=500)
    source = models.CharField(max_length=100)
    body = models.TextField()
    last_updated = models.DateTimeField()

    class Meta:
        # Assumption: A content item is uniquely identified by its title and source
        unique_together = ('title', 'source')

    def __str__(self):
        return self.title

class Flag(models.Model):
    class ReviewStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        RELEVANT = 'relevant', _('Relevant')
        IRRELEVANT = 'irrelevant', _('Irrelevant')

    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='flags')
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name='flags')
    score = models.IntegerField()
    status = models.CharField(
        max_length=20, 
        choices=ReviewStatus.choices, 
        default=ReviewStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('keyword', 'content_item')

    def __str__(self):
        return f"{self.keyword.name} -> {self.content_item.title} ({self.score})"