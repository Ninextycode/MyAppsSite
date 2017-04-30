;
$(document).ready(function() {
    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/chrome");
    editor.getSession().setMode("ace/mode/python");

    var csrftoken = Cookies.get('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function get_selected_shares(){
        selected_shares = [];
        $('.checkbox').each(function(i, obj) {
            if( $(obj).find("input").prop('checked')){
                selected_shares.push($(obj).find("label").text());
            }
        });
        return selected_shares;
    }

    function format_date(date){
       return date.getFullYear() + "-" + (date.getMonth()+1) + "-" + date.getDate()
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    $('#start-date').datetimepicker({
                format: 'DD/MM/YYYY',
                defaultDate: new Date(2016, 05, 01)
           });

    $('#end-date').datetimepicker({
                format: 'DD/MM/YYYY',
                defaultDate:  new Date(2016, 05, 05)
           });

    var start_date_calendar = $('#start-date').data("DateTimePicker");
    var end_date_calendar = $('#end-date').data("DateTimePicker");

    start_date_calendar.minDate(start_date_calendar.date());
    start_date_calendar.maxDate(end_date_calendar.date());
    end_date_calendar.minDate(start_date_calendar.date());
    end_date_calendar.maxDate(end_date_calendar.date());

    $("#start-date").on("dp.change", function (e) {
        $('#end-date').data("DateTimePicker").minDate(e.date);
    });
    $("#end-date").on("dp.change", function (e) {
        $('#start-date').data("DateTimePicker").maxDate(e.date);
    });

    $("#example-button").click(function(){
        editor.setValue(example_strategy, -1);
    });

    $("#test-button").click(function(){
        if(get_selected_shares().length == 0){
            return;
        }
        $("#downolad-results").attr("disabled", true);
        $("#test-button").attr("disabled", true);
        $("#logs-area").val("");
        $("#image_row").empty();
        strategy=editor.getValue();

        sent = $.ajax({
            type: "POST",
            url: "/evaluate/",
            data: {"strategy" : strategy,
                  "selected_shares" : JSON.stringify(get_selected_shares()),
                  "start_date": format_date(new Date(start_date_calendar.date())),
                  "end_date": format_date(new Date(end_date_calendar.date()))
            },
            success: function(response) {
                for (var title in response["plots"]) {
                    if (title === "LIQUIDATION VALUE") {
                        $("#image_row").prepend("<img id=lv>");
                        $("#lv").attr('src', "data:image/png;base64,"+response["plots"][title]);
                    } else {
                        $("#image_row").append("<div class='row'><img id="+title+"></div>");
                        $("#"+title).attr('src', "data:image/png;base64,"+response["plots"][title]);
                    }
                }
                if(response["plots"]){
                    $("#downolad-results").attr("disabled", false);
                }
                $("#logs-area").val(response["logs"]);
            }
        })
        .fail(function(){
            alert("fail");
        })
        .always(function(){
            $("#test-button").attr("disabled", false);
        });
    });

    $("#show-data-button").click(function(){
        $("#share_row").empty();
        if(get_selected_shares().length == 0){
            return;
        }

        $("#show-data-button").attr("disabled", true);

        sent = $.ajax({
            type: "POST",
            url: "/get_shares_graphs/",
            data: {
                  "selected_shares" : JSON.stringify(get_selected_shares()),
                  "start_date": format_date(new Date(start_date_calendar.date())),
                  "end_date": format_date(new Date(end_date_calendar.date()))
              },
            success: function(response) {
                for (var share in response) {
                    $("#share_row").append("<div class='row'><img id="+share+"_graph></div>");
                    $("#"+share+"_graph").attr('src', "data:image/png;base64,"+response[share]);
                }
            }
        })
        .fail(function(){alert("fail")})
        .always(function(){
            $("#show-data-button").attr("disabled", false);
        })
    });

    $("#choose-data-button").click(function(){
        $( "#data-form" ).slideToggle("fast");
    });

        var example_strategy =
"class MyTrader(bt.Trader):\n"+
"    def __init__(self, name):\n"+
"        super().__init__(name)\n"+
"        self.short_length = 600\n"+
"        self.long_length = 1800\n"+
"\n"+
"        self.trading_tickers = [\"SI\", \"BR\"]\n"+
"\n"+
"        self.sh_last = {}\n"+
"        self.sh_now = {}\n"+
"        self.lo_last = {}\n"+
"        self.lo_now = {}\n"+
"        self.close = {}\n"+
"\n"+
"        for ticker in  self.trading_tickers:\n"+
"            self.sh_last[ticker] = 0\n"+
"            self.sh_now[ticker] = 0\n"+
"            self.lo_last[ticker] = 0\n"+
"            self.lo_now[ticker] = 0\n"+
"            self.close[ticker] = np.array([])\n"+
"\n"+
"\n"+
"    def new_candles_action(self, ticker, candles):\n"+
"        if ticker in  self.trading_tickers:\n"+
"            self.lo_last[ticker] = self.lo_now[ticker]\n"+
"            self.sh_last[ticker] = self.sh_now[ticker]\n"+
"\n"+
"            self.lo_now[ticker] = self.close[ticker][- self.long_length:].mean()\n"+
"            self.sh_now[ticker] = self.close[ticker][- self.short_length:].mean()\n"+
"\n"+
"            self.close[ticker] = np.append(self.close[ticker], candles[0].close)\n"+
"\n"+
"            if len(self.close[ticker]) > self.long_length:\n"+
"                self.work_around_new_candle(ticker)\n"+
"\n"+
"\n"+
"\n"+
"    def work_around_new_candle(self, ticker):\n"+
"        if self.fast_cross_bottom_top(ticker):\n"+
"            self.buy(ticker)\n"+
"        elif self.fast_cross_top_bottom(ticker):\n"+
"            self.sell(ticker)\n"+
"\n"+
"    def fast_cross_bottom_top(self, ticker):\n"+
"        return\\\n" +
"            self.sh_last[ticker] <= self.lo_last[ticker] and \\\n" +
"            self.sh_now[ticker] > self.lo_now[ticker]\n"+
"\n" +
"    def fast_cross_top_bottom(self, ticker):\n"+
"        return\\\n" +
"            self.sh_last[ticker] >= self.lo_last[ticker] and \\\n" +
"            self.sh_now[ticker] < self.lo_now[ticker]\n"+
"\n" +
"    def buy(self, ticker):\n"+
"        self.make_order(self.create_market_order(ticker,  10 - self.get_portfolio().get(ticker, 0)))\n"+
"\n"+
"    def sell(self, ticker):\n"+
"        self.make_order(self.create_market_order(ticker, -10 - self.get_portfolio().get(ticker, 0)))\n"+
"\n"+
"    def new_tick_action(self, matches, depths):\n"+
"        for ticker in  self.trading_tickers:\n"+
"            self.request_candles(ticker, 1)\n"
});
