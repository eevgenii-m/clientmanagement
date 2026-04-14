from django import forms
from clientmanagement import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime
from models import wikiarticle
from clientmanagement.widget import quill
import pytz, json


class WikiArticleForm(forms.ModelForm):
    article = quill.QuillField(label="Article text*", widget=quill.QuillWidget({'toolbar': {'image': True, 'video': True}}))
    class Meta:
        model = wikiarticle.WikiArticle
        fields = ('title', 'article')


def _get_editable_content(raw_text):
    """
    Return content suitable for editing in EasyMDE (plain text / markdown).
    If the stored content is legacy Quill JSON, extract the plain text from ops.
    If it's already markdown/plain text, return as-is.
    """
    if not raw_text:
        return ''
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict) and 'ops' in parsed:
            # Legacy Quill Delta — extract plain text from insert ops
            parts = []
            for op in parsed['ops']:
                insert = op.get('insert', '')
                if isinstance(insert, str):
                    parts.append(insert)
            return ''.join(parts).strip()
    except (ValueError, TypeError):
        pass
    # Already plain text / markdown
    return raw_text


def WikiArticleFormParse(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = {}
    data['PAGE_TITLE'] = 'Change posted article: CMS infotek'
    if (request.method == 'POST') and ('action' in request.POST):
        if request.POST['action'] == 'add':
            form = WikiArticleForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.author = request.user.get_full_name()
                model.save()
                return redirect(model.get_link())
            else:
                data['action'] = 'add'
                data['PAGE_TITLE'] = 'Post an article: CMS infotek'
                data['minititle'] = 'Post Article'
                data['submbutton'] = 'Post Article'
                data['article_initial'] = request.POST.get('article', '')

        elif request.POST['action'] == 'change':
            if 'targetid' in request.POST:
                try:
                    curpost = wikiarticle.WikiArticle.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('all_wiki'))
                form = WikiArticleForm(instance=curpost)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Post an article: CMS infotek'
                data['minititle'] = 'Change Posted Article'
                data['submbutton'] = 'Change posted article'
                data['backurl'] = curpost.get_link()
                data['deletebutton'] = 'Delete article'
                data['article_initial'] = _get_editable_content(curpost.article)
            else:
                return redirect(reverse('all_wiki'))

        elif request.POST['action'] == 'changed':
            if 'targetid' in request.POST:
                try:
                    curpost = wikiarticle.WikiArticle.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('all_wiki'))
                form = WikiArticleForm(request.POST, instance=curpost)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.updatedon = datetime.now(pytz.utc)
                    model.save()
                    return redirect(model.get_link())
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Post an article: CMS infotek'
                data['minititle'] = 'Change Posted Article'
                data['submbutton'] = 'Change posted article'
                data['backurl'] = curpost.get_link()
                data['deletebutton'] = 'Delete article'
                data['article_initial'] = request.POST.get('article', '')
            else:
                return redirect(reverse('all_wiki'))

        elif request.POST['action'] == 'delete':
            if 'targetid' in request.POST:
                try:
                    curpost = wikiarticle.WikiArticle.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('all_wiki'))
                curpost.delete()
                return redirect(reverse('all_wiki'))
            else:
                return redirect(reverse('all_wiki'))
        else:
            return redirect(reverse('all_wiki'))
    else:
        form = WikiArticleForm()
        data['action'] = 'add'
        data['PAGE_TITLE'] = 'Post Article: CMS infotek'
        data['minititle'] = 'Post Article'
        data['submbutton'] = 'Post article'
        data['article_initial'] = ''

    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S")
    if 'backurl' not in data:
        data['backurl'] = reverse('all_wiki')
    # Use EasyMDE-based wiki editor (not the shared Quill unimodelform)
    return render(request, 'forms/wikieditform.html', data, content_type='text/html')
