var submit = d3.select("#filter-btn");
var table = d3.select("#tweet-table");
var tbody = d3.select("#tweet-table tbody");

$(document).ajaxStart(function () {
  $("#loaddiv").show();
});

$(document).ajaxComplete(function () {
  $("#loaddiv").hide();
});

/**
 * Initialize 
 */
function init() {
  d3.select("#alertError").attr("class", "alert alert-danger alert-dismissable hide in fade");
  d3.select("#alertSuccess").attr("class", "alert alert-success alert-dismissable hide in fade");
  tbody.html('');
  apiCall('All','');
}
/**
 *  API Call
 */
function apiCall(airlineValue,tweetValue) {

  $("#loaddivData").show();
  $.getJSON('/api/data', {
    airline: airlineValue,
    tweet: tweetValue
  }, function (data) {
    populateData(data.all_tweets);
    $("#loaddivData").hide();
  });

  $("#loaddivWord").show();
  $.getJSON('/api/wordcloud', {
    airline: airlineValue,
    tweet: tweetValue
  }, function (data) {
    wordcloud(data.wordcloud_data);
    $("#loaddivWord").hide();
  });

  $("#loaddivPie").show();
  $.getJSON('/api/pie', {
    airline: airlineValue,
    tweet: tweetValue
  }, function (data) {
    pieChart(data.piechart_data);
    $("#loaddivPie").hide();
  });

  $("#loaddivBar").show();
  $.getJSON('/api/bar', {
    airline: airlineValue,
    tweet: tweetValue
  }, function (data) {
    barChart(data.barchart_data);
    $("#loaddivBar").hide();
  });

  $("#loaddivLine").show();
  $.getJSON('/api/line', {
    airline: airlineValue,
    tweet: tweetValue
  }, function (data) {
    lineChart(data.linechart_data);
    $("#loaddivLine").hide();
  });
}
/**
 * Word Cloud
 */
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
/**
 * Pie Chart
 */
function pieChart(pieData) {
  //Pie chart
  data = [{
    labels: pieData.map(t => t.sentiment),
    values: pieData.map(t => t.count),
    text: pieData.map(t => t.sentiment),
    hoverinfo: 'text+percent',
    textinfo: 'text+percent',
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

/**
 * Bar Chart
 */
function barChart(barData) {
  airline = [...new Set(barData.map(t => t.airline))];
  var trace1 = {
    x: airline,
    y: barData.filter(t => t.sentiment == 'negative').map(t => t.count),
    name: 'negative',
    type: 'bar'
  };

  var trace2 = {
    x: airline,
    y: barData.filter(t => t.sentiment == 'positive').map(t => t.count),
    name: 'positive',
    type: 'bar'
  };

  var trace3 = {
    x: airline,
    y: barData.filter(t => t.sentiment == 'neutral').map(t => t.count),
    name: 'neutral',
    type: 'bar'
  };

  var data = [trace1, trace2, trace3];

  var layout = {
    height: 550,
    width: 650,
    barmode: 'stack',
    xaxis: {
      title: {
        text: 'Airline',
        font: {
          family: 'Courier New, monospace',
          size: 18,
          color: '#7f7f7f'
        }
      },
    },
    yaxis: {
      title: {
        text: 'Tweet count',
        font: {
          family: 'Courier New, monospace',
          size: 18,
          color: '#7f7f7f'
        }
      }
    }
  };

  Plotly.newPlot('barchart', data, layout);
}

/**
 * Line Chart
 */
function lineChart(lineData) {
  var trace1 = {
    x: lineData.filter(t => t.sentiment=='negative').map(t=> t.date),
    y: lineData.filter(t => t.sentiment=='negative').map(t=> t.count),
    name: 'negative',
    type: 'line'
  };
  
  var trace2 = {
    x: lineData.filter(t => t.sentiment=='positive').map(t=> t.date),
    y: lineData.filter(t => t.sentiment=='positive').map(t=> t.count),
    name: 'positive',
    type: 'line'
  };
  
  var trace3 = {
    x: lineData.filter(t => t.sentiment=='neutral').map(t=> t.date),
    y: lineData.filter(t => t.sentiment=='neutral').map(t=> t.count),
    name: 'neutral',
    type: 'line'
  };
  
  var data = [trace1, trace2,trace3];
  var layout ={
    height: 550,
    width: 650,
    xaxis: {
      title: {
        text: 'Date tweet',
        font: {
          family: 'Courier New, monospace',
          size: 18,
          color: '#7f7f7f'
        }
      },
    },
    yaxis: {
      title: {
        text: 'Tweet count',
        font: {
          family: 'Courier New, monospace',
          size: 18,
          color: '#7f7f7f'
        }
      }
    }
  };

  Plotly.newPlot('linechart', data, layout);
}

/**
 * Complete the click handler for the form
 */
submit.on("click", function () {
  // Prevent the page from refreshing
  d3.event.preventDefault();

  // airline
  var airline = d3.select("#airline");
  var airlineValue = airline.property("value");

  // tweet
  var tweet = d3.select("#tweet");
  var tweetValue = tweet.property("value");

  apiCall(airlineValue,tweetValue);
});

/**
 * Populate grid
 */
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

  $('#tweet-table').dataTable({
    destroy: true,
    "pageLength": 25
  });
}

init();