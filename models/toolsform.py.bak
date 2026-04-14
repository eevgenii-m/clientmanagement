from django import forms
from django.conf import settings
import collections, copy, pytz
from clientmanagement import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime
from models import tools
from clientmanagement.widget import clear_file_input
from clientmanagement.widget import form_switch

class FileToolForm(forms.ModelForm):
    order = ("name", "public", "publicinlist", "version", "uplfile", "description")
    inf_page_title = "Add file tool: CMS infotek"
    inf_subm_button = "Submit"
    inf_action='add'
    inf_minititle = 'Add a file tool'
    inf_delete_button = False

    public = form_switch.SwitchOnOffField(label="Public link?", required=False)
    publicinlist = form_switch.SwitchOnOffField(label="Public tool in list?", required=False)
    class Meta:
        model = tools.FileTool
        fields = ("name", "public", "publicinlist", "version", "uplfile", "description")
        widgets = {
            'uplfile': clear_file_input.ClearFileInput,
        }    

    def __init__(self, *args, **kwargs): 
        form = super(FileToolForm, self).__init__(*args, **kwargs) 
        self.fields['public'].label_classes = ('switch-paddle', 'class_b', )
        self.fields['publicinlist'].label_classes = ('switch-paddle', 'class_b', )
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.inf_page_title = "Change file tool: CMS infotek"
            self.inf_action='changed'
            self.inf_minititle = 'Change the file tool'
            self.inf_delete_button = "Delete tool"
            if 'uplfile' in self.changed_data:
                if not instance.uplfile is None:
                    try:
                        instance.uplfile.delete()
                    except Exception as a:
                        pass
            if instance.uplfile is not None and instance.createdon is not None:
                try:
                    self.fields['uplfile'].widget.add_to_filename = instance.uploaded_on_text()
                except:
                    pass

    def save(self, commit=True):
        model = super().save(commit=False)
        if 'uplfile' in self.changed_data:
            model.createdon = datetime.now(pytz.utc)
        if commit:
            model.save()
        return model

class LinkToolForm(forms.ModelForm):
    order = ("name", "public", "publicinlist", "url", "description")
    inf_page_title = "Add link tool: CMS infotek"
    inf_subm_button = "Submit"
    inf_action='add'
    inf_minititle = 'Add a link to a tool'
    inf_delete_button = False

    public = form_switch.SwitchOnOffField(label="Public link?", required=False)
    publicinlist = form_switch.SwitchOnOffField(label="Public tool in list?", required=False)
    class Meta:
        model = tools.LinkTool
        fields = ("name", "public", "publicinlist", "url", "description")

    def __init__(self, *args, **kwargs): 
        super(LinkToolForm, self).__init__(*args, **kwargs)
        self.fields['public'].label_classes = ('switch-paddle', 'class_b', )
        self.fields['publicinlist'].label_classes = ('switch-paddle', 'class_b', ) 

        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.inf_page_title = "Change link tool: CMS infotek"
            self.inf_action='changed'
            self.inf_minititle = 'Change a link to a tool'
            self.inf_delete_button = "Delete tool"
            


def ToolFormParser(request, form_type):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data={}
    back_link = reverse('all_tools', kwargs={'tool_type':''})
    if (form_type == 'f'):
        form_class = FileToolForm
        obj_class = tools.FileTool
    if (form_type == 'l'):
        form_class = LinkToolForm
        obj_class = tools.LinkTool
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(back_link)
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curobj=obj_class.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(back_link)
            form = form_class(instance=curobj)
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curobj=obj_class.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(back_link)
            form = form_class(request.POST, request.FILES, instance=curobj)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(back_link)
        elif (request.POST['action']=='delete'):
            if('targetid' in request.POST):
                try:
                    curobj=obj_class.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(back_link)
            curobj.delete()
            return redirect(back_link)
        else:
            return redirect(back_link)
    else:
        form = form_class()
    data['PAGE_TITLE'] = form.inf_page_title
    data['action'] = form.inf_action
    data['minititle'] = form.inf_minititle
    data['submbutton'] = form.inf_subm_button
    data['deletebutton'] = form.inf_delete_button
    data['backurl'] = back_link
    if('targetid' in request.POST):
        data['targetid'] = request.POST['targetid']
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S")
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
