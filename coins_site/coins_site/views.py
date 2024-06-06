from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from pathlib import Path
import boto3
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def home(request):
	return(render(request,'home.html',{"incorrect_code": "hidden","error": "hidden"}))

def admin(request):
    #Return the admin page
    return(render(request,'admin.html',{}))

def get_available(s3):
    #Get a list of files in the folder cyberdawncoins which is in the bucket evenstarsites.wes
    files_list = s3.list_objects(Bucket='evenstarsites.wes', Prefix='cyberdawncoins')['Contents']
    #Iterate through each file in the list and get the coins and patches
    total_coins = 0
    total_patches = 0
    for file in files_list[1:]:
        obj = s3.get_object(Bucket='evenstarsites.wes', Key=file['Key'])
        data = obj['Body'].read().decode('utf-8')
        data = json.loads(data)
        coins = int(data['coins'])
        patches = int(data['patches'])
        total_coins += coins
        total_patches += patches
    num_coins = 300 - total_coins
    num_patches = 200 - total_patches
    return(num_coins,num_patches)

def initiate_s3():
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
    return(s3)

def form(request):
    #If request type is get, then redirect to home
    if request.method == 'GET':
        return(redirect('home'))
    elif request.method == 'POST':
        #Get the value of the input field
        input_value = request.POST.get('access_code')
        #Get email too
        email = request.POST.get('email')
        with open(BASE_DIR / '../../keys/secret') as f:
            access_code = f.read().strip()
        #if access code is equal access_code, then render the form.html
        if input_value == access_code:
            s3 = initiate_s3()
            num_coins,num_patches = get_available(s3)
            #See if the email is in the bucket
            try:
                obj = s3.get_object(Bucket='evenstarsites.wes', Key='cyberdawncoins/' + email)
                data = obj['Body'].read().decode('utf-8')
                data = json.loads(data)
                coins = data['coins']
                patches = data['patches']
                name = data['name']
                return(render(request,'form.html',{"email": email, "num_coins": num_coins, "num_patches": num_patches, "coins": coins, "patches": patches, "name": name}))
            except:
                return(render(request,'form.html',{"email": email, "num_coins": num_coins, "num_patches": num_patches}))
        else:
            return(render(request,'home.html',{"incorrect_code": "", "error": "hidden"}))

def form_submit(request):
    #if the request method is get, then redirect to home
    if request.method == 'GET':
        return(redirect('home'))
    elif request.method == 'POST':
        #Get all of the input fields
        #name, email, coins, patches, confirm, and access_token
        name = request.POST.get('name')
        email = request.POST.get('email')
        coins = request.POST.get('coins')
        patches = request.POST.get('patches')
        confirm = request.POST.get('confirm')
        access_token = request.POST.get('access_code')
        s3 = initiate_s3()
        num_coins,num_patches = get_available(s3)
        #first we will validate entries
        validation = True
        #The value of input "name" should only be letters, spaces, hyphens, and periods
        if not name.replace(" ", "").replace("-", "").replace(".","").isalpha():
            validation = False
            print("Name error for:", name)
        #The value of input "email" should be a valid email address
        if not "@" in email or not "." in email:
            validation = False
            print("Email error for:",email)
        #If coins is null or patches is null, then set them to 0
        if coins == "":
            coins = "0"
        if patches == "":
            patches = "0"
        #The value of input "coins" should be a number between 1 and 300
        if not coins.isdigit() or int(coins) < 0 or int(coins) > num_coins:
            validation = False
            print("Coins error for:",coins)
        #The value of input "patches" should be a number between 0 and num_patches
        if not patches.isdigit() or int(patches) < 0 or int(patches) > num_patches:
            validation = False
            print("Patches error for:",patches)
        #The value of input "confirm" should be "on"
        if confirm != "on":
            validation = False
            print("Confirm error for:",confirm)
        #The value of input "access_token" should be the same as the access code
        with open(BASE_DIR / '../../keys/secret') as f:
            access_code = f.read().strip()
        if access_token != access_code:
            validation = False
            print("Access token error for:",access_token)
        #If the validation is false, then render the form.html with the error message
        if not validation:
            return(render(request,'home.html',{"error": "", "incorrect_code": "hidden"}))
        else:
            #Turn this data into a dictionary
            data = {
                "name": name,
                "email": email,
                "coins": coins,
                "patches": patches
            }
            #Turn the dictionary into a json string
            data_string = json.dumps(data)
            #Put the data into the bucket cyberdawncoins in the bucket evenstarsites.wes
            s3 = initiate_s3()
            s3.put_object(Bucket='evenstarsites.wes', Key='cyberdawncoins/' + email, Body=data_string)
            #Render form_submit.html
            return(render(request,'form_submit.html',{"name": name, "email": email, "coins": coins, "patches": patches}))
