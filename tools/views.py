from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import StudyNote
from .forms import StudyNoteForm
from django.views.generic import DetailView


def tools_home(request):
    return render(request, 'tools/home.html')

def calculator(request):
    return render(request, 'tools/calculator.html')

def stopwatch(request):
    return render(request, 'tools/stopwatch.html')

def timer(request):
    return render(request, 'tools/timer.html')

# Çalışma Notları View'ları
class StudyNoteListView(LoginRequiredMixin, ListView):
    model = StudyNote
    template_name = 'tools/study_notes_list.html'
    context_object_name = 'notes'
    
    def get_queryset(self):
        return StudyNote.objects.filter(user=self.request.user)

class StudyNoteCreateView(LoginRequiredMixin, CreateView):
    model = StudyNote
    form_class = StudyNoteForm
    template_name = 'tools/study_note_form.html'
    success_url = reverse_lazy('tools:study_notes_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class StudyNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = StudyNote
    form_class = StudyNoteForm
    template_name = 'tools/study_note_form.html'
    success_url = reverse_lazy('tools:study_notes_list')
    
    def get_queryset(self):
        return StudyNote.objects.filter(user=self.request.user)

class StudyNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = StudyNote
    template_name = 'tools/study_note_confirm_delete.html'
    success_url = reverse_lazy('tools:study_notes_list')
    
    def get_queryset(self):
        return StudyNote.objects.filter(user=self.request.user)
    
class StudyNoteDetailView(LoginRequiredMixin, DetailView):
    model = StudyNote
    template_name = 'tools/study_note_detail.html'
    context_object_name = 'note'
    
    def get_queryset(self):
        return StudyNote.objects.filter(user=self.request.user)