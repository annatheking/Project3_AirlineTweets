SELECT * 
	, date(tweet_created) as tweet_date
    , time(tweet_created) as tweet_time
    , substring_index(replace(tweet_coord,'[',''), ',', 1) as lat
    , substring_index(replace(tweet_coord,']',''), ',', -1) as lng
FROM airlinetwitter.tweets;