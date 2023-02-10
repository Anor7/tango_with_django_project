from audioop import reverse
from contextlib import _RedirectStream
from imaplib import _Authenticator
from os import login_tty
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.shortcuts import HttpResponseRedirect

# Import the Category model
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage matches to {{ boldmessage }} in the template!
    # Query the database for a list of ALL categories currently stored.
    ## Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    
    #Render the response and send it back!
    return render(request, 'rango/index.html', context=context_dict)

    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context=context_dict)
    return HttpResponse("Rango says hey there partner!" + "<a href='/rango/about/'>About</a>")

# Create your views here.
def about(request):
    return HttpResponse("Rango says here is the about page." + "<a href='/rango/'>Index</a>")

def show_category(request, category_name_slug):
# Create a context dictionary which we can pass
# to the template rendering engine.
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages

        # We also add the category object from
        # the database to the context dictionary.
        #We'll use this in the template to verify that the category exists.
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)

def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

    if form.is_valid():
        # Save the new category to the database.
        form.save(commit=True)
        # Now that the category is saved, we could confirm this.
        # For now, just redirect the user back to the index view.
        return _RedirectStream('/rango/')
    else:
        print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})

def register(request):

    registered = False

    if request.method == 'POST':

        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
        # Save the user's form data to the database.
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
                    'rango/register.html',
                    context = {'user_form': user_form,
                                'profile_form': profile_form,
    '                           registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = _Authenticator(username=username, password=password)

        if user:
            if user.is_active:
                login_tty(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

# Use the login_required() decorator to ensure only those logged in can
# access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))