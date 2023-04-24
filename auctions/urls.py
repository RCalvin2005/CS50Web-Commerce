from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/add", views.add_listing, name="add_listing"),
    path("listing/<int:listing_id>", views.listing_page, name="listing_page"),
    path("listing/<int:listing_id>/bid", views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/comment", views.post_comment, name="post_comment"),
    path("listing/<int:listing_id>/close", views.close_listing, name="close_listing"),
    path("listing/<int:listing_id>/watchlist/add", views.watchlist_add, name="watchlist_add"),
    path("listing/<int:listing_id>/watchlist/remove", views.watchlist_remove, name="watchlist_remove"),
    path("user/<str:username>/listings", views.user_listings, name="user_listings"),
    path("user/<str:username>/watchlist", views.watchlist, name="watchlist"),
    path("user/<str:username>/comments", views.user_comments, name="user_comments"),
    path("categories", views.categories, name="categories")
]
