from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def home(request):
	return(render(request,'home.html',{"hidden": "hidden"}))

def form(request):
    #If request type is get, then redirect to home
    if request.method == 'GET':
        return render(request,'home.html',{"hidden": "hidden"})
    elif request.method == 'POST':
        #Get the value of the input field
        input_value = request.POST.get('access_code')
        with open(BASE_DIR / '../../keys/secret') as f:
            access_code = f.read().strip()
        #if access code is equal access_code, then render the form.html
        if input_value == access_code:
            return(render(request,'form.html',{}))
        else:
            return(render(request,'home.html',{"hidden": ""}))