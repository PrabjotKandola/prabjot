from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UploadDataForm, ExplorationForm, ProfileForm, TransformForm, MatchingForm
from .models import DataFiles, ExplorationFiles, RulesBasedProfileFiles, TransformedFiles, MatchFiles, UnmatchedFiles
from django.contrib import messages
from .backend.profilit.profilit_functions.rules import rules_profile
from .backend.profilit.profilit_functions.exploration import explore
from .backend.profilit.profilit_functions.transform import transform_data
from .backend.profilit.profilit_functions.data_matching import match as backend_match
from itertools import chain
from dashboard.models import RuleTemplateErrors
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages

import re

@login_required
def home(request):
    return render(request, 'profilit/home.html')
""""
@login_required
def exploration(request):
    if request.method == 'POST':
        form = YourForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            # Perform exploration and error highlighting logic here
            highlighted_contents = highlight_errors(file)  # Replace with your error highlighting logic
            file_url = file.file.url  # Get the URL of the uploaded file

            return render(request, 'profilit/exploration.html', {'e_form': form, 'highlighted_contents': highlighted_contents, 'file_url': file_url})
    else:
        form = YourForm()
    return render(request, 'profilit/exploration.html', {'e_form': form})

"""
def highlight_duplicates(contents):
    pattern = r'<(\w+)[^>]*>(.*?)<\/\1>'
    duplicate_pattern = re.compile(r'({0}).*?(\1)'.format(pattern))
    highlighted_contents = duplicate_pattern.sub(r'<\1 class="highlight">\2</\1>', contents)
    return highlighted_contents



@login_required
def exploration(request):
    files = ExplorationFiles.objects.filter(person=request.user.id).order_by('-date_created')
    context = {'files': files}

    if request.method == 'POST' and 'explore' in request.POST:
        e_form = ExplorationForm(request.POST)
        if e_form.is_valid():
            file_pk = request.POST['files']
            explore.main(file_pk, request.user)
            messages.success(request, f'Your file has been Explored!')
            return redirect('profilit-exploration')

    elif request.method == 'POST' and 'delete' in request.POST:
        ExplorationFiles.objects.get(pk=request.POST['primary_key']).delete()
        messages.warning(request, f'Your file has been Deleted!', extra_tags='danger')
        return redirect('profilit-exploration')
    else:
        e_form = ExplorationForm()

    e_form.fields['files'].queryset = DataFiles.objects.filter(person=request.user.id, file_type='df')
    context['e_form'] = e_form
    return render(request, 'profilit/exploration.html', context)


@login_required
def about(request):
    return render(request, 'profilit/about.html')


@login_required
def rules(request):
    files = RulesBasedProfileFiles.objects.filter(person=request.user.id).order_by('-date_created')
    context = {'files': files}
    context['errors'] = RuleTemplateErrors.objects.filter(person=request.user.id)

    if request.method == 'POST' and 'rules' in request.POST:
        p_form = ProfileForm(request.POST)
        if p_form.is_valid():
            data_file_pk = request.POST['data_files']
            rules_template_pk = request.POST['rules_template']
            data_id = request.POST['data_id']
            rules_profile.main(data_file_pk, rules_template_pk, data_id, request.user)
            if RuleTemplateErrors.objects.filter(person=request.user.id).exists():
                return redirect('check-rules')
            else:
                messages.success(request, f'Your file has been Profiled!')
            return redirect('profilit-rules')

    elif request.method == 'POST' and 'delete' in request.POST:
        RulesBasedProfileFiles.objects.get(pk=request.POST['primary_key']).delete()
        messages.warning(request, f'Your file has been Deleted!', extra_tags='danger')
        return redirect('profilit-rules')
    else:
        p_form = ProfileForm()

    p_form.fields['data_files'].queryset = DataFiles.objects.filter(person=request.user.id, file_type='df')
    p_form.fields['rules_template'].queryset = DataFiles.objects.filter(person=request.user.id, file_type='rt')
    context['p_form'] = p_form
    return render(request, 'profilit/rules.html', context)


@login_required
def transform(request):
    files = TransformedFiles.objects.filter(person=request.user.id).order_by('-date_created')
    context = {'files': files}

    if request.method == 'POST' and 'transform' in request.POST:
        t_form = TransformForm(request.POST)

        if t_form.is_valid():
            data_file_pk = request.POST['data_files']
            transform_template_pk = request.POST['transform_template']
            transform_data.main(data_file_pk, transform_template_pk, request.user)
            messages.success(request, f'Your file has been Transformed!')
            return redirect('profilit-transform')

    elif request.method == 'POST' and 'delete' in request.POST:
        TransformedFiles.objects.get(pk=request.POST['primary_key']).delete()
        messages.warning(request, f'Your file has been Deleted!', extra_tags='danger')
        return redirect('profilit-transform')
    else:
        t_form = TransformForm()

    t_form.fields['data_files'].queryset = DataFiles.objects.filter(person=request.user.id, file_type='df')
    t_form.fields['transform_template'].queryset = DataFiles.objects.filter(person=request.user.id, file_type='tt')
    context['t_form'] = t_form

    return render(request, 'profilit/transform.html', context)


@login_required
def match(request):
    match_files = MatchFiles.objects.filter(person=request.user.id)
    unmatch_files = UnmatchedFiles.objects.filter(person=request.user.id)
    files = sorted(chain(match_files, unmatch_files), key=lambda instance: instance.date_created, reverse=True)
    context = {'files': files}

    if request.method == 'POST' and 'match' in request.POST:
        m_form = MatchingForm(request.POST)

        if m_form.is_valid():
            data_file_1_pk = request.POST['data_files_1']
            data_file_2_pk = request.POST['data_files_2']
            match_template_pk = request.POST['match_template']
            backend_match.main(data_file_1_pk, data_file_2_pk, match_template_pk, request.user)
            messages.success(request, f'Data matching has been completed!')
            return redirect('profilit-match')

    elif request.method == 'POST' and 'matched' in request.POST:
        print(request.POST)
        print('hello')
        MatchFiles.objects.get(pk=request.POST['matched']).delete()
        messages.warning(request, f'Your file has been Deleted!', extra_tags='danger')
        return redirect('profilit-match')

    elif request.method == 'POST' and 'unmatched' in request.POST:
        print(request.POST)
        UnmatchedFiles.objects.get(pk=request.POST['unmatched']).delete()
        messages.warning(request, f'Your file has been Deleted!')
        return redirect('profilit-match')
    else:
        m_form = MatchingForm()

    m_form.fields['data_files_1'].queryset = DataFiles.objects.filter(person=request.user.id, file_type='df')
    m_form.fields['data_files_2'].queryset = DataFiles.objects.filter(person=request.user.id, file_type='df')
    m_form.fields['match_template'].queryset = DataFiles.objects.filter(person=request.user.id, file_type='mt')
    context['m_form'] = m_form

    return render(request, 'profilit/Match.html', context)

# @login_required
# def data(request):
#     context = {}
#     if request.method == 'POST':
#         uploaded_file = request.FILES['document']
#         fs = FileSystemStorage()
#         name = fs.save(name=uploaded_file.name, content=uploaded_file)
#         context['url'] = fs.url(name)
#         print(uploaded_file.name)
#         print(uploaded_file.size)
#
#     return render(request, 'profilit/data.html', context)

@login_required
def data(request):
    data_files = DataFiles.objects.filter(person=request.user.id)
    files = sorted(data_files, key=lambda instance: instance.date_created, reverse=True)
    context = {'files': files}
    if request.method == 'POST' and 'upload' in request.POST:
        u_form = UploadDataForm(request.POST,
                                request.FILES)

        if u_form.is_valid():
            new_form = u_form.save(commit=False)  # save form so far but don't commit
            new_form.person_id = request.user.id  # fill in the foreign key field
            new_form.save()  # save the form to database
            messages.success(request, f'Your file has been uploaded!')
            return redirect('profilit-data')
    elif request.method == 'POST' and 'delete' in request.POST:
        DataFiles.objects.get(pk=request.POST['primary_key']).delete()
        messages.warning(request, f'Your file has been Deleted!', extra_tags='danger')
        return redirect('profilit-data')
    else:
        u_form = UploadDataForm()

    context['u_form'] = u_form
    return render(request, 'profilit/data.html', context)




















