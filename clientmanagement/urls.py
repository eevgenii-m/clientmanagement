"""visualanalyticsplatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.shortcuts import reverse

from clientmanagement import views as clientmanagement_views
from clientmanagement import loginform as clientmanagement_loginform
from clientmanagement import generatefileviews as generate_files
from models import views as models_views
from models import projectviews as project_views
from models import sharedfileviews
from models import adminviews
from models.email import mailbox


urlpatterns = [
    path('clients/', clientmanagement_views.allclientsview, name='allclients'),
    path('computers/', clientmanagement_views.allcomputersview, name='allcomputers'),
    path('people/', clientmanagement_views.allpeopleview, name='allpeople'),

    path('clients/<int:clientid>', clientmanagement_views.clientview, name='oneclient'),
    path('clients/<int:clientid>/printer', models_views.printerForm, name='clientprinter'),
    path('clients/<int:clientid>/computer', models_views.computerForm, name='clientcomputer'),
    path('people/new', models_views.personForm, name='newperson'),
    path('clients/<int:clientid>/person', models_views.personForm, name='clientperson'),
    path('clients/<int:clientid>/domain', models_views.domainForm, name='clientdomain'),
    path('clients/<int:clientid>/router', models_views.routerForm, name='clientrouter'),
    path('clients/<int:clientid>/netequipment', models_views.otherNetEquipmentForm, name='clientothernetequip'),
    path('clients/<int:clientid>/joindomainfile', generate_files.downloadConnectDomainFile, name='clientjoindomainfile'),
    path('clients/<int:clientid>/addcomputersoftware', generate_files.downloadAddComputerSoftware, name='clientaddcomputersoftware'),
    path('clients/<int:clientid>/addcomputerconfig', generate_files.downloadAddComputerConfigFile, name='clientaddcomputerconfig'),

    path('tickets/submit', models_views.submitTicketForm, name='ticket_submit'),
    path('tickets/submitted', clientmanagement_views.ticketdoneview, name='ticket_submitted'),
    path('tickets/<int:ticketid>/change', models_views.changeTicketForm, name='ticket_change'),
    path('tickets/<uuid:ticketuuid>', models_views.viewTicketDirectView, name='ticket_view_direct'),
    re_path(r'^tickets/(?P<ticketuuid>\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)/files/(?P<filename>[a-zA-Z0-9\.\(\)_\-+=!@#%]+)', models_views.downloadFileFromTicket, name='get_ticket_file'),
    re_path(r'^tickets/(?P<ticketuuid>\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)/v/files/(?P<filename>[a-zA-Z0-9\.\(\)_\-+=!@#%]+)', models_views.viewFileFromTicket, name='get_ticket_file_view'),
    re_path(r'^tickets/(?P<ticketuuid>\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)/(?P<commentid>\d+)/files/(?P<filename>[a-zA-Z0-9\.\(\)_\-+=!@#%]+)', models_views.downloadFileFromComment, name='get_comment_file'),
    re_path(r'^tickets/(?P<ticketuuid>\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)/(?P<commentid>\d+)/v/files/(?P<filename>[a-zA-Z0-9\.\(\)_\-+=!@#%]+)', models_views.viewFileFromComment, name='get_comment_file_view'),
    path('tickets/<uuid:ticketuuid>/addcomment', models_views.addCommentToTicketView, name='ticket_add_comment'),
    re_path(r'^tickets/(?P<reqtype>(a|c|o|))', clientmanagement_views.allticketsview, name='alltickets'),

    path('note', models_views.AddSecretNoteView, name='new_note'),
    path('notes/', models_views.allSecretNotesView, name='all_notes'),
    re_path(r'^notes/(?P<reqtype>(|a|u))$', models_views.allSecretNotesView, name='all_notes'),
    path('notes/<int:noteid>', models_views.SecretNoteInternalView, name='note_internal'),
    path('notes/<int:noteid>/change', models_views.changeTicketForm, name='note_change'),
    path('notes/c/<uuid:noteuuid>', models_views.viewSecretNoteViewClose, name='note_close'),
    path('notes/o/<uuid:noteuuid>', models_views.viewSecretNoteViewOpen, name='note_open'),

    re_path(r'^tool/(?P<tool_type>(l|f))$', models_views.AddNewToolView, name='new_tool'),
    path('tool/<int:toolid>/view', models_views.toolView, name='tool_view'),
    re_path(r'^tools/(?P<tool_type>(l|f|))$', clientmanagement_views.allToolsView, name='all_tools'),
    path('tool/f/d/<uuid:tooluuid>', models_views.downloadToolPublic, name='download_tool_public'),
    path('tool/f/d/p/<uuid:tooluuid>', models_views.downloadTool, name='download_tool'),

    path('files/', models_views.allSharedFilesView, name='all_shared_files'),
    path('files/upload', models_views.uploadSharedFileView, name='upload_shared_file'),
    path('files/links/', sharedfileviews.all_upload_links, name='all_upload_links'),
    path('files/links/create', sharedfileviews.create_upload_link, name='create_upload_link'),
    path('files/links/<uuid:linkuuid>', sharedfileviews.view_upload_link, name='view_upload_link'),
    path('files/links/<uuid:linkuuid>/delete', sharedfileviews.delete_upload_link, name='delete_upload_link'),
    path('files/links/<uuid:linkuuid>/edit', sharedfileviews.edit_upload_link, name='edit_upload_link'),
    path('files/<uuid:fileuuid>/download', models_views.downloadSharedFilePublic, name='download_shared_file'),
    path('files/<uuid:fileuuid>/edit', models_views.editSharedFileView, name='shared_file_edit'),
    path('files/<int:fileid>/delete', models_views.deleteSharedFileView, name='delete_shared_file'),
    path('files/<uuid:fileuuid>', models_views.viewSharedFileView, name='shared_file_view'),
    path('upload/<uuid:linkuuid>', sharedfileviews.client_upload_page, name='client_upload_page'),

    path('projects/', project_views.all_projects, name='all_projects'),
    path('projects/reorder', project_views.reorder_projects, name='reorder_projects'),
    path('projects/archived', project_views.archived_projects, name='archived_projects'),
    path('projects/<int:project_id>/edit', project_views.edit_project, name='edit_project'),
    path('projects/<int:project_id>/delete', project_views.delete_project, name='delete_project'),
    path('projects/<int:project_id>/task/add', project_views.add_task, name='add_task'),
    path('projects/task/<int:task_id>/edit', project_views.edit_task, name='edit_task'),
    path('projects/task/<int:task_id>/delete', project_views.delete_task, name='delete_task'),

    path('todo/', project_views.all_todos, name='all_todos'),
    path('todo/add', project_views.add_todo, name='add_todo'),
    path('todo/archived', project_views.archived_todos, name='archived_todos'),
    path('todo/reorder', project_views.reorder_todos, name='reorder_todos'),
    path('todo/<int:todo_id>/edit', project_views.edit_todo, name='edit_todo'),

    path('help/', clientmanagement_views.helpview, name='help'),
    path('statistics/', clientmanagement_views.statisticsview, name='statistics'),
    path('client', models_views.clientForm, name='newclient'),
    path('client/<int:clientid>/r', models_views.downloadRouterSettings, name='download_router_settings'),

    path('wiki/', clientmanagement_views.allWikiArticlesView, name='all_wiki'),
    path('wiki/new', models_views.createWikiArticle, name='wiki_new'),
    path('wiki/<uuid:wikiuuid>', clientmanagement_views.wikiArticleView, name='wiki_art'),

    path('updates/', clientmanagement_views.systemupdatesview, name='updates'),
    path('updates/post', models_views.PostSystemUpdate, name='postupdate'),

    path('usermanagement/', adminviews.admin_portal, name='usermanagement'),
    path('usermanagement/users/', adminviews.admin_users, name='admin_users'),
    path('usermanagement/users/add', adminviews.admin_user_add, name='admin_user_add'),
    path('usermanagement/users/<int:user_id>/edit', adminviews.admin_user_edit, name='admin_user_edit'),
    path('usermanagement/users/<int:user_id>/delete', adminviews.admin_user_delete, name='admin_user_delete'),
    path('usermanagement/login-logs/', adminviews.admin_login_logs, name='admin_login_logs'),
    path('usermanagement/adduser', models_views.addUserForm, name='adduser'),  # legacy
    path('', clientmanagement_views.homepage, name='homepage'),

    path('me', clientmanagement_views.userpersonalpage, name='personal_page'),
    path('me/<int:deleted>/<int:deletedpage>', clientmanagement_views.userpersonalpage, name='personal_page_uri'),
    path('me/delete_api', clientmanagement_views.deletepersonalapikey, name='delete_my_api_key'),
    path('me/cms_interactive', generate_files.downloadUserCMSInteractionSoftware, name='cms_interactive_software'),

    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(form_class=clientmanagement_loginform.my_reset_password_form, 
    html_email_template_name='registration/forgot_password.htm'), 
    {'password_reset_form':clientmanagement_loginform.my_reset_password_form, 
    'form_class': clientmanagement_loginform.my_reset_password_form}, 'password_reset'),
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=clientmanagement_loginform.MyAuthLoginForm), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/', include('api_app.urls')),
    re_path(r'^.*$', clientmanagement_views.homepage),
    path('testmodule/', include('clientmanagement.testmodule.urls')),
]


mailbox.initiateEmailCheck()
