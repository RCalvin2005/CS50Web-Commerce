from django.contrib import admin
from .models import Listing, Bid, Comment

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "current_price", "seller")
    filter_horizontal = ("watchers",)


class BidAdmin(admin.ModelAdmin):
    list_display = ("listing", "value", "bidder")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "message", "author")


# Register your models here.
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
