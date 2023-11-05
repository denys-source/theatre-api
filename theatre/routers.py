from rest_framework.routers import DefaultRouter

from theatre.views import APIRootView


class Router(DefaultRouter):
    include_format_suffixes = False 

    def get_api_root_view(self, api_urls):
        return APIRootView.as_view()
