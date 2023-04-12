from django import template
from django.utils import timezone

import re

# https://www.geeksforgeeks.org/custom-template-filters-in-django/

register = template.Library()

@register.filter()
def time_ago(date_created):
    """Returns X days/minutes etc. ago"""

    diff = timezone.now() - date_created

    # https://stackoverflow.com/questions/2119472/convert-a-timedelta-to-days-hours-and-minutes
    if diff.days:
        if diff.days >= 30:
            diff_str = f"{diff.days // 30} months ago"
        elif diff.days >= 14:
            diff_str = f"{diff.days // 7} weeks ago"
        else:
            diff_str = f"{diff.days} days ago"
    else:
        if diff.seconds >= 3600:
            diff_str = f"{diff.seconds // 3600} hours ago"
        elif diff.seconds >= 60:
            diff_str = f"{diff.seconds // 60} minutes ago"
        else:
            diff_str = f"{diff.seconds} seconds ago"
        
    return re.sub(r"^1 (\w+)s ago$", r"1 \1 ago", diff_str)
