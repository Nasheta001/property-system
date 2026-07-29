from django.urls import path

from apps.calendar_app.views import CalendarEventsView

urlpatterns = [
    path("calendar/events/", CalendarEventsView.as_view(), name="calendar-events"),
]
