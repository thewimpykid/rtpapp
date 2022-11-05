from django.shortcuts import render, redirect
from django.http import HttpResponse

def redir(request):
    return redirect('/home')