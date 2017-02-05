import datetime
import ast
from django.db.models import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from bmat_test.models import RadioStation, Performer, Song, Play
from bmat_test.serializers import RadioStationSerialzer, PerformerSerializer, SongSerializer, PlaySerializer, SongPlaySerializer, \
    ChannelPlaySerializer, TopPlaySerializer

class BmatListAPIView(generics.ListAPIView):
    """
    We are overriding Django Rest Framework's ListAPIView for our list views (for the "get_" endpoints).
    We want to reformat the output to match the format given in the spec
    """
    def list(self, request, *args, **kwargs):
        # return super(BmatListAPIView, self).list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self.reformat_data(serializer=serializer.data , code=0))
        serializer = self.get_serializer(queryset, many=True)

        return Response(self.reformat_data(serializer=serializer, code=0))

    def reformat_data(self, serializer=None, code=1):
        result = serializer.data
        result =   {"result": result , "code": code, "errors": [] }
        return result



class BmatCreateApiView(generics.CreateAPIView):
    """
    We are overriding Django Rest Framework's CreateAPIView for our create views (for the "add_" endpoints).
    We want to reformat the output to match the format given in the spec
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=False):
            self.perform_create(serializer)  #Actually a get or create now
            current_status = status.HTTP_201_CREATED
            code = 0
        else :
#            current_status = status.HTTP_422_UNPROCESSABLE_ENTITY  # url lib in the test script doesn't like this even though it seems to be the most "correct" code to use
            current_status = status.HTTP_400_BAD_REQUEST
            code = 1

        formatted_data = self.reformat_data(serializer=serializer, code=code)
        return Response(formatted_data  , status=current_status )#, headers=headers)


    def reformat_data(self, serializer=None, code=1):

        errors = []
        for type, curr_errors in serializer.errors.items() :
            errors.extend(curr_errors)

        if not code :
            result = serializer.data
        else :
            result = {}
        return  {"result": result , "code": code, "errors": errors }



# POST /add_channel, data={name: 'channel_name'}
# curl -H "Content-Type: application/json" -X POST -d '{"name":"first station"}' http://127.0.0.1:8000/add_channel/
class CreateChannelView(BmatCreateApiView):
    queryset = RadioStation.objects.all()
    serializer_class = RadioStationSerialzer


# POST /add_performer, data={name: 'performer'}
# curl -H "Content-Type: application/json" -X POST -d '{"name":"Colly"}' http://127.0.0.1:8000/add_performer
class CreatePerformerView(BmatCreateApiView):
    queryset = Performer.objects.all()
    serializer_class = PerformerSerializer

# POST /add_song, data={title: 'song_name, performer: 'performer_name'}

class CreateSongView(BmatCreateApiView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer


# POST /add_play, data={ title: 'song_name',
#                        performer: performer_name',
#                        start: '2014-10-21T18:41:00',
#                        end: '2014-10-21T18:44:00',
#                        channel: 'channel_name'}
class CreatePlayView(BmatCreateApiView):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer


# GET /get_song_plays,
# data = {title: 'song_name',
#         performer: performer_name',
#         start: '2014-10-21T00:00:00',
#         end: '2014-10-28T00:00:00'}
# Returns:
#     { result: [{channel: 'channel',
#       start: '2014-01-10T01:00:00',
#       end: '2014-01-10T01:03:00'],...],
#       code: 0}
class SongListView(BmatListAPIView):

    serializer_class = SongPlaySerializer

    def get_queryset(self):

        data = self.request.query_params

        title = data.get('title', None)
        performer  = data.get('performer', None)
        start = data.get('start', None)
        end   = data.get('end', None)

        # question, do we want to include songs that are partially in the time range, or only songs that have been
        # played entirely within the time range?
        qs = Play.objects.filter(song__title=title,
                                 song__performer__name=performer,
                                 start__gte=start ,
                                 end__lte=end)
        return qs



# GET /get_channel_plays,
# data = {start: '2014-10-21T00:00:00',
#         end: '2014-10-28T00:00:00',
#         channel: 'channel'}
# Returns:
#     {result: [{performer: 'performer_name',
#      title: 'title',
#      start: '2014-10-21T00:00:00',
#      end: '2014-10-21T00:03:00'},...],
#      code: 0}
class ChannelPlaysListView(BmatListAPIView):

    serializer_class = ChannelPlaySerializer

    def get_queryset(self):

        data = self.request.query_params
        start = data.get('start', None)
        end  = data.get('end' , None)
        channel = data.get('channel', None)

        qs = Play.objects.filter(start__gte=start,
                                 end__lte=end,
                                 radio_station__name=channel)
        return qs



# GET /get_top,
# data = {channels: ['channel_name'],
#         start: '2014-10-21T00:00:00',
#         limit: 40}
# Returns:
#     { result: [{performer: 'performer',
#       title: 'title',
#       plays: plays,
#       previous_plays: previous_plays,
#       rank: rank,
#       previous_rank: previous_rank], ...],
#       code: 0}
#
# curl -H "Content-Type: application/json" -X GET -d '{ "start": "2014-01-10T00:00:00", "channels": ["Channel2"] , "limit" : 40 }' http://127.0.0.1:8000/get_top

class GetTopListView(BmatListAPIView):
    serializer_class = TopPlaySerializer
    def get_queryset(self):
        data = self.request.query_params

        start = data.get('start', None)

        seven_days  = datetime.timedelta(days=7)
        start_dt = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
        end_dt = start_dt + seven_days
        prev_start_dt = start_dt - seven_days

        limit = data.get('limit', None)
        channels_str = data.get('channels', None) # yuk, the script passes a string representation of teh array, rather than separate items
        channels = ast.literal_eval(channels_str)


        # 1: first get last weeks top songs, to use for previous rank
        prev_week_qs = Song.objects.filter(play__radio_station__name__in=channels,
                                           play__start__gte=prev_start_dt,
                                           play__end__lte=start_dt
                                           )\
                                        .distinct()\
                                        .annotate(play_count=Count('play__id'))\
                                        .order_by("-play_count")
        if limit :
            prev_week_qs = prev_week_qs[0:int(limit)]

        # 2: put the results in a dictionary for retrieval later
        prev_plays_dict = { song.id : {'plays' : song.play_count, 'rank' : i   } for i, song in enumerate(prev_week_qs) }

        # 3: get this weeks top songs
        qs = Song.objects.filter(play__start__gte=start_dt,
                                 play__end__lte=end_dt  ,  ## remove this as its not in the spec
                                 play__radio_station__name__in=channels)\
                                .distinct()\
                               .annotate(play_count=Count('play__id'))\
                               .order_by('-play_count')

        if limit :
            qs= qs[0:int(limit)]

        # 4: add the previous weeks plays / ranks
        for i , song in enumerate(qs) :
            song.rank = i
            if song.id in prev_plays_dict:
                song.previous_plays = prev_plays_dict[song.id]['plays']
                song.previous_rank = prev_plays_dict[song.id]['rank']

            else:
                song.previous_plays = 0
                song.previous_rank = 'null'

        return qs

