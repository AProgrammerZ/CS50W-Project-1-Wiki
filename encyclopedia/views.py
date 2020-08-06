from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from . import util

import markdown2

import random

class SearchForm(forms.Form):
    search_input = forms.CharField(label='',
                                   widget=forms.TextInput(
                                        attrs={'placeholder': 'Search Encyclopedia', 
                                        'class': 'search'}))

class NewPageForm(forms.Form):
    title = forms.CharField(label='Title')
    content = forms.CharField(label='Content (in Markdown)',
                                    widget=forms.Textarea)

class EditPageForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.old_content = kwargs.pop('old_content')
        super(EditPageForm, self).__init__(*args, **kwargs)
        self.fields['content'].initial = self.old_content

    content = forms.CharField(label='Content (in Markdown)', widget=forms.Textarea)

def index(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search_input = form.cleaned_data["search_input"]
            if util.get_entry(search_input):            
                return HttpResponseRedirect(reverse("entry", args=[search_input]))                
            else:
                return render(request, "encyclopedia/search_results.html", {
                    "entries": [ entry for entry in util.list_entries() 
                                 if (
                                    search_input in entry 
                                    or search_input.capitalize() in entry
                                    or search_input.upper() in entry
                                    or search_input.lower() in entry
                                )],
                    "title": search_input,
                    "form": SearchForm()
                })                
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(),
            "form": SearchForm()
        })

def entry(request, title):
    if title.capitalize() in util.list_entries():
        title = title.capitalize()
    if title.upper() in util.list_entries():
        title = title.upper()
    if title.lower() in util.list_entries():
        title = title.lower()    

    if util.get_entry(title):
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(util.get_entry(title)),
            "title": title,
            "form": SearchForm()
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "form": SearchForm()
        })

def new_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title):                
                messages.error(
                    request, 'An encyclopedia entry already exists with the provided title.'
                )
                return render(request, "encyclopedia/new_page.html", {
                    "form": SearchForm(),
                    "new_page_form": form
                })
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", args=[title]))
    else:    
        return render(request, "encyclopedia/new_page.html", {
            "form": SearchForm(),
            "new_page_form": NewPageForm()
        })

def edit(request):
    title = request.GET.get('title')    

    if request.method == "POST":
        form = EditPageForm(request.POST, old_content=None)
        if form.is_valid():
            content = form.cleaned_data["content"]    
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', args=[title]))
    else:        
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(),
            "title": title,
            "edit_page_form": EditPageForm(old_content=util.get_entry(title))
        })

def random_page(request):    
    random_entry = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse('entry', args=[random_entry]))
