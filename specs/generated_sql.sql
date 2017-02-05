SELECT DISTINCT "bmat_test_song"."id", "bmat_test_song"."title", "bmat_test_song"."performer_id", COUNT("bmat_test_play"."id") AS "play_count"
FROM "bmat_test_song"
  INNER JOIN "bmat_test_play" ON ("bmat_test_song"."id" = "bmat_test_play"."song_id")
  INNER JOIN "bmat_test_radiostation" ON ("bmat_test_play"."radio_station_id" = "bmat_test_radiostation"."id")

WHERE ("bmat_test_play"."start" >= 2014-01-01 00:00:00
        AND "bmat_test_radiostation"."name" IN (Channel1, Channel2)
        AND "bmat_test_play"."end" <= 2014-01-08 00:00:00)
GROUP BY "bmat_test_song"."id", "bmat_test_song"."title", "bmat_test_song"."performer_id" ORDER BY "