CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_bubblechart`()
BEGIN

select airline as Airline
    , case 
		when weekday(STR_TO_DATE(tweet_date, '%m/%d/%Y')) = 0 then 'Monday'
        when weekday(STR_TO_DATE(tweet_date, '%m/%d/%Y')) = 1 then "Tuesday"
        when weekday(STR_TO_DATE(tweet_date, '%m/%d/%Y')) = 2 then 'Wednesday'
        when weekday(STR_TO_DATE(tweet_date, '%m/%d/%Y')) = 3 then 'Thursday'
        when weekday(STR_TO_DATE(tweet_date, '%m/%d/%Y')) = 4 then "Friday"
        when weekday(STR_TO_DATE(tweet_date, '%m/%d/%Y')) = 5 then 'Saturday'
        else 'Sunday'
	  end as WeekDay
    , count(*) as TweetCount
from airlinetwitter.tweets
where weekday(STR_TO_DATE(tweet_date, '%m/%d/%Y')) is not null
group by airline, WeekDay
order by airline, weekday(STR_TO_DATE(tweet_date, '%m/%d/%Y'));

END