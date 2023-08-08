from django.contrib import admin
from .models import DataFiles, RulesBasedProfileFiles, ExplorationFiles, TransformedFiles, MatchFiles, UnmatchedFiles


admin.site.register(DataFiles)
admin.site.register(RulesBasedProfileFiles)
admin.site.register(ExplorationFiles)
admin.site.register(TransformedFiles)
admin.site.register(MatchFiles)
admin.site.register(UnmatchedFiles)

# Register your models here.
