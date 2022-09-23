import datetime


def CurrentDate(request):
    return {"date": datetime.date.today().year}
