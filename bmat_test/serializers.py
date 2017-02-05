from rest_framework import serializers, renderers, validators
from bmat_test.models import RadioStation, Performer, Song, Play

class GetOrCreateSerializer(serializers.ModelSerializer):
    """
    We want get or create functionality rather than just get, so disable unique
    """
    def __init__(self, *args, **kwargs):
        super(GetOrCreateSerializer, self).__init__(*args, **kwargs)

        if 'name' in self.fields :
            for validator in self.fields['name'].validators :
                self.fields['name'].validators.remove(validator)# = []


    def run_validators(self, value):
        """
        DRF is running all validators, which causes errors when sending the same data more than once.
        remove the unique validator as we have implemented a get_or_create, rather than just get
        """
        for validator in self.validators:
            if isinstance(validator, validators.UniqueTogetherValidator):
                self.validators.remove(validator)
        super(GetOrCreateSerializer, self).run_validators(value)

class RadioStationSerialzer(GetOrCreateSerializer):

    class Meta:
        model = RadioStation
        fields = ('name',)


    def create(self, validated_data):
        name = validated_data.pop('name')
        return RadioStation.objects.get_or_create(name=name)[0]



class PerformerSerializer(GetOrCreateSerializer):

    class Meta:
        model = Performer
        fields = ('name', )

    def create(self, validated_data):
        name = validated_data.pop('name')
        return Performer.objects.get_or_create(name=name)[0]




class PerformerField(serializers.Field):
    """
    Custom field as we want the 'performer_name' field to be a foreign key to the performer on the Song endpoint
    """
    def to_internal_value(self, data):
        return Performer.objects.get(name=data)

    def to_representation(self, value):
        return value.name


class SongSerializer(GetOrCreateSerializer):

    performer = PerformerField(read_only=False)

    def create(self, validated_data):
        performer_name = validated_data.pop('performer')
        title = validated_data.pop('title')
        # validated_data.update(performer=performer['name'])
        performer = Performer.objects.get(name=performer_name) ;
        return Song.objects.get_or_create(title=title, performer=performer, defaults=validated_data )[0]


    class Meta:
        model = Song
        fields = ('title', 'performer',)

class ChannelField(serializers.Field):
    def to_internal_value(self, data):
        return None



class PlaySerializer(serializers.Serializer):
    title     = serializers.CharField(read_only=False)
    performer = serializers.CharField(read_only=False)
    channel   = serializers.CharField(read_only=False)
    start     = serializers.DateTimeField(read_only=False)
    end       = serializers.DateTimeField(read_only=False)

    def create(self, validated_data):
        song_name = validated_data.pop('title')
        performer_name = validated_data.pop('performer')
        song_dict = {'title' : song_name , 'performer__name' : performer_name }
        song = Song.objects.get(**song_dict) # do we want get or get_or_create? Not clear from the spec

        station_name  = validated_data.pop('channel')
        station, created = RadioStation.objects.get_or_create(name=station_name)

        start = validated_data.pop('start')
        end = validated_data.pop('end')
        play, created = Play.objects.get_or_create(song=song,
                                          radio_station=station,
                                          start=start,
                                          end=end)
        return play


    def to_representation(self, instance):
        data = {"start": instance.start ,
                "end"  : instance.end ,
                "title"     : instance.song.title ,
                "performer" : instance.song.performer.name
                }
        return data

#  ---- Subclass the play serializer for the  different responses we need ------
class SongPlaySerializer(PlaySerializer):

    def to_representation(self, instance):
        data = {"start": instance.start ,
                "end"  : instance.end ,
                "channel"   : instance.radio_station.name ,
                }
        return data


class ChannelPlaySerializer(PlaySerializer):

    def to_representation(self, instance):
        data = {"start": instance.start ,
                "end"  : instance.end ,
                "title"     : instance.song.title ,
                "performer" : instance.song.performer.name
                }
        return data


class TopPlaySerializer(SongSerializer):
    def to_representation(self, instance):
        data = {
                "performer": instance.performer.name,
                "plays" : instance.play_count ,
                "previous_plays" : instance.previous_plays ,
                "previous_rank" : instance.previous_rank,
                "rank"   : instance.rank,
                "title"  : instance.title,
        }
        return data

