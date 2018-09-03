def register_jinja_filters(app):
    app.jinja_env.filters["datetimefmt"] = datetimefmt

def datetimefmt(value, format='%d-%m-%Y/%H:%M '):
    return value.strftime(format)
