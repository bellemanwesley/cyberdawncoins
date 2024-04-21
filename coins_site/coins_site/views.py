from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path
import boto3

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
            #Get the AWS keys from the file
            with open(BASE_DIR / '../../keys/aws') as f:
                aws_keys = f.read().splitlines()
            #The key starts at index 8
            aws_access_key = aws_keys[0][8:].strip()
            aws_secret_key = aws_keys[1][8:].strip()
            s3 = boto3.client(
                's3',
                region_name='us-west-2',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            #Get a list of files in the folder cyberdawncoins which is in the bucket evenstarsites.wes
            purchased = len(s3.list_objects(Bucket='evenstarsites.wes', Prefix='cyberdawncoins')['Contents'])
            num_coins = 300 - purchased
            return(render(request,'form.html',{"num_coins": num_coins}))
        else:
            return(render(request,'home.html',{"hidden": ""}))