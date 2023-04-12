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
]
