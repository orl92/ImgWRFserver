from django.shortcuts import render

def my400_view(request, exception=None):
    return render(request, 'layouts/400.html', status=400)

def my403_view(request, exception=None):
    return render(request, 'layouts/403.html', status=403)

def my404_view(request, exception=None):
    return render(request, 'layouts/404.html', status=404)

def my500_view(request, exception=None):
    return render(request, 'layouts/500.html', status=500)