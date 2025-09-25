# user_profile/templatetags/badge_utils.py
from django import template

register = template.Library()

@register.filter
def badge_color(badge_type):
    return badge_type.color if badge_type and badge_type.color else '#6c757d'

@register.filter
def badge_icon(badge_type):
    return badge_type.icon if badge_type and badge_type.icon else 'fas fa-medal'

@register.filter
def badge_name(badge_type):
    return badge_type.name if badge_type and badge_type.name else 'Özel'