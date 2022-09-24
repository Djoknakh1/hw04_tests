import datetime


def сurrent_date(request):
    return {"year": datetime.date.today().year}
