from django.shortcuts import render
from django.conf import settings

def main(request):
    return render(request,'main.html', {
        'MEDIA_URL': settings.MEDIA_URL,
    })
    
def parentsPage(request):
    return render(request, 'parents_page.html', {
        'MEDIA_URL': settings.MEDIA_URL,
    })

def teachersPage(request):
    return render(request, 'teachers_page.html', {
        'MEDIA_URL': settings.MEDIA_URL,
    })

def createIdPage(request):
    return render(request, 'createId_page.html', {
        'MEDIA_URL': settings.MEDIA_URL,
    })