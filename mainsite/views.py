from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.http import Http404
# --------- Views --------------------
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .mixins import OwnerCheck
# -------------------------------------
from django.contrib.auth import login, logout # authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Group, Post
from .forms import (
    UserCreationForm,
    UserEditForm,
    UserMoreInfoForm,
    LoginForm,
    GroupForm,
    PostForm,
    )


class MainView(View):
    def get(self, request):
        return render(request, 'index.html')
#------------- profile -------------------
class SignUp(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main')
        return super().dispatch(request, *args, **kwargs)
    def get(self, request):
        mainform = UserCreationForm()
        addform = UserMoreInfoForm()
        return render(request, 'signup.html', context={'main_form': mainform, 'add_form': addform})
    def post(self, request):
        mainform = UserCreationForm(request.POST)
        addform = UserMoreInfoForm(request.POST, request.FILES) # how to save?????
        if mainform.is_valid() and addform.is_valid():
            user = mainform.save()
            addform.save(user=user)
            login(request, user)
            return redirect('main')
        return render(request, 'signup.html', context={'main_form': mainform, 'add_form': addform})

class Login(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main')
        return super().dispatch(request, *args, **kwargs)
    def get(self, request):
        form = LoginForm()
        context={'form': form}
        if request.GET.get('next') is not None:
            context['next'] = True
        return render(request, 'login.html', context=context)
    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user() # походу авторизация происходит "под капотом")
            login(request, user)
            redir = request.GET.get('next', 'main')
            return redirect(redir)
        return render(request, 'login.html', context={'form': form})

@login_required(login_url='login')
def logoutview(request):
    logout(request)
    return redirect('main')

class ProfileInfo(LoginRequiredMixin, DetailView): 
    # get_object() - по умолчанию ищет сначало по pk, можно переопределить
    # get_context_data() - если хотим задать дополнитульную инфу в контекст, например список комментов 
    login_url = '/login/' 
    model = User
    template_name = 'mainsite/profileinfo.html'
    def get_object(self):
        try:
            object = super().get_object()
            return object
        except:
            return self.request.user

class ProfileEdit(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        mainform = UserEditForm(instance=request.user) # base user info
        addform = UserMoreInfoForm(instance=request.user.account) # additional user info(model Account)
        return render(request, 'mainsite/profile_edit.html', context={'mainform': mainform, 'addform': addform})
    def post(self, request):
        mainform = UserEditForm(request.POST, instance=request.user)
        addform = UserMoreInfoForm(request.POST, request.FILES, instance=request.user.account)
        if mainform.is_valid() and addform.is_valid():
            user = mainform.save()
            addform.save(user=user)
            if mainform.cleaned_data.get('password1'):
                login(request, user)
            return redirect('myprofile')
        return render(request, 'mainsite/profile_edit.html', context={'mainform': mainform, 'addform': addform})

# ---------- group ----------------------

class GroupList(ListView):
    allow_empty = True
    model = Group
    paginate_by = 5
    context_object_name = 'groups'
    template_name = 'mainsite/group_list.html'
    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        page = self.request.GET.get('page') or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            elif page == 'first':
                page_number = 1
            else:
                raise Http404(u"Page is not 'last' or 'first', nor can it be converted to an int.")
        page = paginator.get_page(page_number) # get_page исключает ошибки, вместо просто page()
        return (paginator, page, page.object_list, page.has_other_pages())

class GroupView(DetailView):
    # allow_empty = True <-- зачем она???
    model = Group
    template_name = 'mainsite/group_info.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['posts'] = Post.objects.filter(group=context['object'])
        context['colors'] = ('primary', 'secondary', 'success', 'danger', 'warning', 'info', 'dark')
        return context

class GroupCreate(LoginRequiredMixin, CreateView):
    login_url = 'login'
    form_class = GroupForm
    template_name = 'mainsite/group_create.html'
    def form_valid(self, form):
        obj = form.save()
        obj.owners.add(self.request.user.account)
        return redirect(obj) # <-- get_absolute_url() does my code easy, because i don't override get_success_url() method!

class GroupUpdate(LoginRequiredMixin, OwnerCheck, UpdateView):
    login_url = 'login'
    form_class = GroupForm
    model = Group
    template_name = 'mainsite/group_edit.html'

    def form_valid(self, form):
        obj = form.save() # FIXME if we save default slug(with dot simbols), will be raised a error!!!
        print('kek')
        return redirect(obj)

class GroupDelete(LoginRequiredMixin, OwnerCheck, DeleteView):
    login_url = 'login'
    model = Group
    success_url = reverse_lazy('group_list')
    template_name = 'mainsite/obj_delete_confirm.html'

# ------------- post ----------------------

class PostCreate(LoginRequiredMixin, OwnerCheck, CreateView):
    login_url = 'login'
    form_class = PostForm
    template_name = 'mainsite/post_create.html'
    def form_valid(self, form):
        obj = form.save(author=self.request.user.account, group=self.group)
        return redirect(obj) # TODO: redirect to post absolute url

class PostView(DetailView):
    model = Post
    template_name = 'mainsite/post_detail.html'
    def get_queryset(self):
        group = get_object_or_404(Group, slug__iexact=self.kwargs.get('slug'))
        return Post.objects.filter(group=group)
    def get_object(self):
        return get_object_or_404(self.get_queryset(), slug__iexact=self.kwargs.get('postslug'))
""" Крч, сверху почти говнокод. Я сделал чтобы ссылка на пост содержал слаг группы, но можно сделать тупо ссылку без
слага группы и кода меньше, и юзабилити сайта повысится
я даун("""

@login_required(login_url='login')
def group_join(request, slug):
    group = get_object_or_404(Group, slug__iexact=slug)
    group.owners.add(request.user.account)
    return redirect(group)

@login_required(login_url='login')
def group_left(request, slug):
    group = get_object_or_404(Group, slug__iexact=slug)
    group.owners.remove(request.user.account)
    return redirect(group)