from django.contrib import admin
from basiccontent.models import *

@admin.register(BasicPost)
class BasicPostAdmin(admin.ModelAdmin):
    pass
    # list_display = ('title', 'post_type', 'created_at')
    # search_fields = ('title',)
    # list_filter = ('post_type',)
    # ordering = ('-created_at',)
    # list_per_page = 10

@admin.register(PostContent)
class PostContentAdmin(admin.ModelAdmin):
    pass

@admin.register(PostOptions)
class PostOptionsAdmin(admin.ModelAdmin):
    pass