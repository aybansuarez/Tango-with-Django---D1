from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserProfileForm
from datetime import datetime
from rango.bing_search import run_query, read_bing_key
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rango.models import UserProfile
from django.contrib.auth.models import User

def index(request):
    # COOKIES
    # request.session.set_test_cookie()
    # category_list = Category.objects.order_by('-likes')[:5]
    # page_list = Page.objects.order_by('-views')[:5]
    # context_dict = {'categories': category_list, 'pages': page_list, 'visits': int(request.COOKIES.get('visits', '1'))}
    # # Obtain our Response object early so we can add cookie information.
    # response = render(request, 'rango/index.html', context_dict)
    # # Call the helper function to handle the cookies
    # visitor_cookie_handler(request, response)
    # # Return response back to the user, updating any cookies that need changed.
    # return response

    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list, 'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    context_dict['second_cats'] = Category.objects.all()

    response = render(request, 'rango/index.html', context=context_dict)
    return response

# def about(request):
#     # context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
#     # return render(request, 'rango/about.html', context=context_dict)
#     if request.session.test_cookie_worked():
#         print("TEST COOKIE WORKED!")
#         request.session.delete_test_cookie()
#     # prints out whether the method is GET or POST
#     print(request.method)
#     # prints out the user name, if no one is logged in, it prints 'AnonymousUser'
#     print(request.user)

#     visitor_cookie_handler(request)
#     context_dict = {'visits': request.session['visits']}

#     response = render(request, 'rango/about.html', context_dict)
#     return response

class AboutView(View):
    def get(self, request):
        # view logic
        visitor_cookie_handler(request)
        return render(request, 'rango/about.html', context={'visits': request.session['visits']})

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # # to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        
        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category).order_by('-views')
        
        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
        # the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None

    # New code added here to handle POST request

    # create a default query based on the category name
    # to be shown in the search box
    context_dict['query'] = category.name

    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our search API functions to get results
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)

# def add_category(request):
#     form = CategoryForm()

#     # A HTTP POST?
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)

#         # Have we been provided with valid form?
#         if form.is_valid():
#             # Save the new category to the database
#             form.save(commit=True)
#             # Now that the category is saved
#             # We could give a confirmation message
#             # But since the most recent category added is on the index page # Then we can direct the user back to the index page.
#             return index(request)
#         else:
#             # The supplied form contained errors -
#             # # just print them to the terminal.
#             print(form.errors)

#     # Will handle the bad form, new form, or no form supplied cases.
#     # Render the form with error messages (if any).
#     return render(request, 'rango/add_category.html', {'form': form})

class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm()
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)

        return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug): 
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST) 
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else: 
            print(form.errors)
            
    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)

# # Not technically a view, but a helper function
# def visitor_cookie_handler(request, response):
#     # Get the number of visits to the site.
#     # We use the COOKIES.get() function to obtain the visits cookie.
#     # If the cookie exists, the value returned is casted to an integer.
#     # If the cookie doesn't exist, then the default value of 1 is used.
#     visits = int(request.COOKIES.get('visits', '1'))
    
#     last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
#     last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    
#     # If it's been more than a day since the last visit...
#     if (datetime.now() - last_visit_time).seconds > 0:
#         visits = visits + 1
#         # Update the last visit cookie now that we have updated the count
#         response.set_cookie('last_visit', str(datetime.now()))
#     else:
#         # Set the last visit cookie
#         response.set_cookie('last_visit', last_visit_cookie)
    
#     # Update/set the visits cookie
#     response.set_cookie('visits', visits)

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val
    
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        # update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits

def search(request):
    result_list = []
    query = None

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the result list
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'query': query, 'result_list': result_list})

def goto_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    
    return redirect(url)

@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('index')
        else:
            print(form.errors)

    context_dict = {'form': form}

    return render(request, 'rango/profile_registration.html', context_dict)

class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('index')

        userprofile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': userprofile.website, 'picture': userprofile.picture})
        return (user, userprofile, form)

    @method_decorator(login_required)
    def get(self, request, username):
        (user, userprofile, form) = self.get_user_details(username)
        return render(request, 'rango/profile.html', {'userprofile': userprofile, 'selecteduser': user, 'form': form})

    @method_decorator(login_required)
    def post(self, request, username):
        (user, userprofile, form) = self.get_user_details(username)
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)
        
        return render(request, 'rango/profile.html', {'userprofile': userprofile, 'selecteduser': user, 'form': form})

@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()
    return render(request, 'rango/list_profiles.html', {'userprofile_list' : userprofile_list})

@login_required
def like_category(request):
    cat_id = None
    if request.method == "GET":
        cat_id = request.GET['category_id']
        likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)

def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if len(starts_with.strip())>0:
        cat_list = Category.objects.filter(name__contains=starts_with)
    
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list

def suggest_category(request):
    cat_list = []
    starts_with = ''
    
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
        
    cat_list = get_category_list(8, starts_with)
    if len(cat_list) == 0:
        cat_list = Category.objects.order_by('-likes')
    
    return render(request, 'rango/cats.html', {'cats': cat_list })

@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages
    
    return render(request, 'rango/page_list.html', context_dict)