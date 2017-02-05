from django.db import models


# Todo add some indexes so that it woill run at a decent speed

class RadioStation(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    def __str__(self):
        return self.name

class Performer(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    performer = models.ForeignKey(Performer)
    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('title', 'performer')


class Play(models.Model):
    song = models.ForeignKey(Song)
    radio_station = models.ForeignKey(RadioStation)
    start = models.DateTimeField()  # need to work out how to get second precision
    end = models.DateTimeField()

    def __str__(self):
        return "%s - %s : %s" % (self.song.title , self.radio_station, self.start)

    def performer(self):
        return self.song.performer.name

    def song_title(self):
        return self.song.title

    class Meta:
        unique_together = ('song', 'radio_station', 'start')

    # todo, add some unique contrains, I assume the same station can't play the same song at the same time