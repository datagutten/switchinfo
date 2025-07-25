accesslog = "/dev/stdout"
errorlog = "/dev/stderr"
workers = 4
bind = '0.0.0.0:8000'
wsgi_app = 'switch_info.wsgi:application'
secure_scheme_headers = {'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}
