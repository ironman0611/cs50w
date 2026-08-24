from django.shortcuts import render, redirect
from markdown2 import Markdown

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry_content = util.get_entry(title)
    if entry_content is None:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": "Entry not found"
        })
    
    markdowner = Markdown()
    entry_content = markdowner.convert(entry_content)
    
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": entry_content,
    })

def search(request):
    q = request.GET.get('q', '')
    entries = util.list_entries()

    for entry in entries:
        if q.lower() == entry.lower():
            return redirect("entry", title=entry)

    search_results = []
    for entry in entries:
        if q.lower() in entry.lower():
            search_results.append(entry)

    return render(request, "encyclopedia/search.html", {
        "q": q,
        "entries": search_results
    })

def create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/create.html", {
                "error": "Entry already exists.",
                "title": title,
                "content": content,
            })
        util.save_entry(title, content)
        return redirect("entry", title=title)
    return render(request, "encyclopedia/create.html")

def edit(request, title):
    if request.method == "POST":
        content = request.POST.get("content")
        util.save_entry(title, content)
        return redirect("entry", title=title)
    
    entry_content = util.get_entry(title)
    if entry_content is None:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": "Entry not found"
        })
    
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "entry": entry_content
    })

def random_page(request):
    import random
    entries = util.list_entries()
    if entries:
        random_entry = random.choice(entries)
        return redirect("entry", title=random_entry)
    else:
        return redirect("index")