from django.contrib import admin
from basiccontent.models import *

@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    pass
    # list_display = ('title', 'post_type', 'created_at')
    # search_fields = ('title',)
    # list_filter = ('post_type',)
    # ordering = ('-created_at',)
    # list_per_page = 10

@admin.register(MainPost)
class MainPostAdmin(admin.ModelAdmin):
    pass

@admin.register(SubPost)
class SubPostAdmin(admin.ModelAdmin):
    pass

@admin.register(PostContent)
class PostContentAdmin(admin.ModelAdmin):
    pass

@admin.register(PostOptions)
class PostOptionsAdmin(admin.ModelAdmin):
    pass