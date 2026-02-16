from django.shortcuts import render
from django.views import View

class My400View(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'layouts/400.html', status=400)

class My403View(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'layouts/403.html', status=403)

class My404View(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'layouts/404.html', status=404)

class My500View(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'layouts/500.html', status=500)
