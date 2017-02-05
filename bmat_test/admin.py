from django.contrib import admin
from bmat_test.models import RadioStation, Performer, Song, Play
# Register your models here.

class PerformerAdmin(admin.ModelAdmin):
    list_display = ('name',)

class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'performer',)

class PlayAdmin(admin.ModelAdmin):
    list_display = ('id' , 'song' , 'start', 'end', 'song_title', 'performer', 'radio_station' )

admin.site.register(RadioStation)
admin.site.register(Performer, PerformerAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Play, PlayAdmin)