var submit = d3.select("#filter-btn");
var table = d3.select("#tweet-table");
var tbody = d3.select("#tweet-table tbody");


function init() {

  var date = new Date();
  date.setDate(date.getDate() + 30);

  var year_val = 2015;
  $('#tweetfrom, #tweetto').datepicker({
    dateFormat: "yy-mm-dd",
    autoclose: true,
    format: "mm-yyyy",
    viewMode: "months",
    minViewMode: "months",
    minDate: date
  });

  d3.select("#alertError").attr("class", "alert alert-danger alert-dismissable hide in fade");
  d3.select("#alertSuccess").attr("class", "alert alert-success alert-dismissable hide in fade");
  tbody.html('');

  $.getJSON('/api/search', {
    airline: 'All',
    tweet: '',
    tweetfrom: '',
    tweetto: ''
  }, function (data) {
    populateData(data.all_tweets);
    wordcloud(data.wordcloud_data);
    pieChart(data.piechart_data);
  });

}

function wordcloud(wordsData) {
  /*
  / Generate Word Cloud from tweet words 
  */
  d3.select('#wordcloud').html('');
  wordsData.forEach(function (v) { delete v.attr });
  if ($('#wordcloud').hasClass("jqcloud")) {
    $('#wordcloud').jQCloud('update', wordsData);
  }
  else {
    $('#wordcloud').jQCloud(wordsData, {
      delay: 10,
      autoResize: true,
      fontSize: {
        from: 0.6,
        to: 0.03
      }
    });
  }
}

function pieChart(pieData) {
    //Pie chart
    data = [{
      labels: pieData.map(t=>t[0]),
      values: pieData.map(t=>t[1]),
      text: pieData.map(t=>t[0]),
      hoverinfo: 'text+percent',
      textinfo: 'percent',
      type: 'pie'
    }];
    var layout = {
      hovermode: 'closest',
      margin: { t: 0 },
      height: 550,
      width: 650
    };
    Plotly.newPlot("piechart", data, layout);
}


function barChart(barData) {
}




// Complete the click handler for the form
submit.on("click", function () {
  // Prevent the page from refreshing
  d3.event.preventDefault();

  // airline
  var airline = d3.select("#airline");
  var airlineValue = airline.property("value");

  // tweet
  var tweet = d3.select("#tweet");
  var tweetValue = tweet.property("value");

  // tweetfrom
  var tweetfrom = d3.select("#tweetfrom");
  var tweetfromValue = tweetfrom.property("value");

  // tweetto
  var tweetto = d3.select("#tweetto");
  var tweettoValue = tweetto.property("value");

  $.getJSON('/api/search', {
    airline: airlineValue,
    tweet: tweetValue,
    tweetfrom: tweetfromValue,
    tweetto: tweettoValue
  }, function (data) {
    populateData(data.all_tweets);
    wordcloud(data.wordcloud_data);
    pieChart(data.piechart_data);
  });

});

function populateData(filteredData) {
  /*
  // Adds new rows of data for each tweet.
  */
  table.attr("class", "table table-striped hide in fade");
  d3.select("#alertError").attr("class", "alert alert-danger alert-dismissable hide in fade");
  d3.select("#alertSuccess").attr("class", "alert alert-success alert-dismissable hide in fade");
  tbody.html('');

  if (filteredData.length == 0) {
    d3.select("#alertError").attr("class", "alert alert-danger alert-dismissable");
    d3.select("#alertErrorText").text("No data found.")
    return;
  }

  console.log(filteredData.length);
  table.attr("class", "table table-striped");
  d3.select("#alertSuccess").attr("class", "alert alert-success alert-dismissable");
  d3.select("#alertSuccessText").text(`${filteredData.length} record(s) found.`);

  filteredData.forEach((tweet) => {
    var row = tbody.append("tr");
    var cell = row.append("td");
    cell.text(tweet.airline);
    var cell = row.append("td");
    cell.text(tweet.tweet);
    var cell = row.append("td");
    cell.text(tweet.sentiment);
    var cell = row.append("td");
    cell.text(tweet.date);
    var cell = row.append("td");
    cell.text(tweet.lat);
    var cell = row.append("td");
    cell.text(tweet.lng);
  });
}


init();