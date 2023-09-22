from django.contrib.auth.decorators import user_passes_test


def blocked(f):
    
    return user_passes_test(lambda u: u.is_blocked==False and u.is_anonymous==False, login_url='blocked')(f)