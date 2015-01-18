
$(document).ready(function(){
	ajaxload()
	get_currentspeed()

	//loaddb3()
});


function makeArrayDate2(ary) {
	d = {}
	data = []
	dtx = []
	drx = []
	dt = []

	$.each(ary, function(i, a) {
		// all xml results are in kibi convert to gibi
		var rx = parseInt(a.rx) / 1024 / 1024,
		tx = parseInt(a.tx) / 1024 / 1024;
		getReadableFileSizeString(tx)
		dtx.push(tx)
		drx.push(rx)
		dt.push((rx + tx))


	})
	d.dtx = dtx
	d.drx = drx
	d.dt = dt

	console.log("d")
	console.log(d)
	return d

}

function get_currentspeed() {
	$.get(WEBDIR + 'vnstat/tr', function(data) {
		if (data.rx && data.tx) {
			$("#vnstat-rx").text(data.rx);
			$("#vnstat-tx").text(data.tx);

		} else {
			return
		}

	})
}

// loads from db and makes html
function ajaxload() {
    $.ajax({
    	// change url to test
        url: WEBDIR + 'vnstat/dumpdb',
        async: false,
        success: function (data) {
        	t = $('.content')
        	console.log("ajaxload")
        	console.log("data.vnstat.interface")
        	console.log(data.vnstat.interface)
        	var interf = data["vnstat"]["interface"]
        	// check if its a dict or list
        	if (typeof(interf.id) !== 'undefined'){
        		var interf = [data["vnstat"]["interface"]]
        	}

            	$.each(interf, function (ii, dd) {

                    var p = $('<div>').addClass('row-fluid').attr('id', dd.id);
                    // below fucks up alignment, fix it
                    //p.append($('<span>').addClass('pull-left').text(dd.id))
                    //p.append($('<span>').addClass('pull-right').text(dd.id))
                    // w h needs to hardcoded in canvas
                    m = $('<div>').addClass("span4").append($('<canvas width=400px; height=400px">').attr('id', 'month_' + dd.id));
                    d = $('<div>').addClass("span4").append($('<canvas width=400px; height=400px">').attr('id', 'day_' + dd.id));
                    h = $('<div>').addClass("span4").append($('<canvas width=400px; height=400px">').attr('id', 'hour_' + dd.id));

                    // Inside m, d, h make a table or something for tab data


                    p.append(m);
                    p.append(d);
                    p.append(h);
                    t.append(p);

                });

        }

    });

    loaddb()
}


function loaddb() {
    $.ajax({
        url: WEBDIR + 'vnstat/dumpdb',
        async: false,
        success: function (data) {
        	var interf = data["vnstat"]["interface"]
        	if (typeof(data.vnstat["interface"].id) !== 'undefined'){
        		var interf = [data["vnstat"]["interface"]]
        	}


            $.each(interf, function (n, ainterf) {
                var z = ainterf;
                console.log("z");
                console.log(z);
                var interfaceid = z.id;
                var created = z.created.date;
                var date = moment(created.day + created.month + created.year, "DD.MM.YYYY").format('DD.MM.YYYY');

                var traffic = z.traffic;
                var months = traffic.months.month;
                var days = traffic.days.day;
                var hour = traffic.hours.hour;


                var twelve = makeArrayDate2(months);
                var dday = makeArrayDate2(days);
                var hour2 = makeArrayDate2(hour);

                makechart2("month", interfaceid, twelve);
                makechart2("day", interfaceid, dday);
                makechart2("hour", interfaceid, hour2);


            });

        }
    });
}

function makechart2(selector, interfaceid, d) {
	console.log("makechart")
	console.log(selector);
	console.log(d)
	if (selector == "day") {
		l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

	} else if (selector == "month") {
		l = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]

	} else if (selector == "hour") {
		l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
	}

	sel = selector + '_' + interfaceid
	var ctx = $('#' + sel).get(0).getContext("2d");
	parentwidth = $('#' + sel).parent().width()
	parentheight = $('#' + sel).parent().height()

	var data = {
		labels: l,

	    datasets: [
	        {

	            label: "Download",
	            fillColor: "rgba(220,220,220,0.2)",
	            strokeColor: "#56ff00",//"rgba(220,220,220,1)", // green #56ff00
	            pointColor: "rgba(220,220,220,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(220,220,220,1)",
	            data: d.drx,
	            title: "Download", //
	            scaleLabel: "<%=value%> TB", //
	            showScale: true //
	        },
	        {

	            label: "Upload",
	            fillColor: "rgba(151,187,205,0.2)",
	            strokeColor: "#0038ff",//"rgba(151,187,205,1)", // blue #0038ff
	            pointColor: "rgba(151,187,205,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(151,187,205,1)",
	            data: d.dtx,
	            xPos: d.dtx, // just a test
	            title: "Upload", //
	            scaleLabel: "<%=value%> TB", //
	            showScale: true //
	        },
	        {
	        	title: "Total",
	            label: "Total",
	            fillColor: "rgba(151,187,205,0.2)", // red #FF0000
	            strokeColor: "#EC7886", //rgba(151,187,205,1)",
	            pointColor: "rgba(151,187,205,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(151,187,205,1)",
	            data: d.dt,//[28, 48, 40, 19, 86, 27, 90]
	            title: "Total", //
	            scaleLabel: "<%=value%> TB", //
	            showScale: true //
	        }
	    ]
	};
	//graphTitle : "default animation",
	//inGraphDataShow:true
	options = {showScale: true, scaleLabel: "<%=value%> TB", graphTitle : selector, legend : true, responsive: true} // can be removed
	new Chart(ctx).Line(data, options);
}

// grab form default.js instead? use math.pow
function getReadableFileSizeString(fileSizeInBytes) {
    var i = -1;
    var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB'];
    do {
        fileSizeInBytes = fileSizeInBytes / 1024;
        i++;
    } while (fileSizeInBytes > 1024);
    return fileSizeInBytes.toFixed(1) + byteUnits[i];
};