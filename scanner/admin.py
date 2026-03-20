from django.contrib import admin
from .models import Keyword, ContentItem, Flag

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'last_updated')
    list_filter = ('source', 'last_updated')
    search_fields = ('title', 'body', 'source')
    ordering = ('-last_updated',)

@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    # Display key info at a glance
    list_display = ('keyword', 'content_item', 'score', 'status', 'created_at')
    
    # Allow reviewers to filter by what needs attention
    list_filter = ('status', 'keyword__name')
    
    # Search by keyword or content title
    search_fields = ('keyword__name', 'content_item__title')
    
    # BONUS: Allow reviewers to change status directly from the list view without opening the record
    list_editable = ('status',)
    
    # Keep the highest scores and newest flags at the top
    ordering = ('-score', '-created_at')
    
    # Optimize database queries in the admin panel
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('keyword', 'content_item')