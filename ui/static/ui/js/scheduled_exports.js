jobs = {};
jobs.list = (function(){
    var map;
    var job_extents;
    var bbox;
    var filtering = false;
    var searchForm = $('form#search');

    /*
     * Handle stickiness of map on window scroll
     */
    var stickyTop = $('#map-column').offset().top;
    $(window).scroll(function(){
        var windowTop = $(window).scrollTop();
        // only make sticky on larger screens
        if (stickyTop < windowTop && $(window).width() > 992) {
            $('#map-column').css({
                position: 'fixed',
                top: 0,
                right: 0
            });
        }
        else {
            $('#map-column').css({
                position: 'relative',
            });
        }

    });

    return {
        main: function(){
            $('div#search').css('display','none');
            $('div#spinner').css('display','block');
            initListMap();
            initDataTable();
            runSearch();
        },
    }


    /**
     * Initialize the job list map
     */
    function initListMap(){
        var maxExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");
        var mapOptions = {
                displayProjection: new OpenLayers.Projection("EPSG:4326"),
                controls: [new OpenLayers.Control.Attribution(),
                           new OpenLayers.Control.ScaleLine()],
                maxExtent: maxExtent,
                scales:[500000,350000,250000,100000,25000,20000,15000,10000,5000,2500,1250],
                units: 'm',
                sphericalMercator: true,
                noWrap: true // don't wrap world extents
        }
        map = new OpenLayers.Map('list-export-map', {
            options: mapOptions
        });

        // restrict extent to world bounds to prevent panning..
        map.restrictedExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");

        // add base layers
        var osm = new OpenLayers.Layer.OSM("OpenStreetMap");
        osm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayer(osm);
        map.zoomToMaxExtent();


        
        var geojson = new OpenLayers.Layer.Vector("GeoJSON",{
              strategies: [new OpenLayers.Strategy.Fixed()],
              protocol: new OpenLayers.Protocol.HTTP({
                url: "https://s3.us-east-2.amazonaws.com/bdon-osm2hdx/SEN_simplified.geojson",
                format: new OpenLayers.Format.GeoJSON()
              })
          });
        map.addLayer(geojson);
      
    }



    /**
     * Lists the jobs.
     *
     * url: the search endpoint.
     *
     */
    function listJobs(url){
        if (!url) {
            // default search endpoint
            url = Config.SCHEDULED_EXPORTS_URL;
        }
        $.ajax({
            url: url,
            cache: false,
        })
        .done(function(data, textStatus, jqXHR){
            // generate pagination on UI
            paginate(jqXHR);

            // clear the existing data on results table and add new page
            var tbody = $('table#jobs tbody');
            var table = $('table#jobs').DataTable();
            table.clear();
            table.rows.add(data).draw();
            $('div#spinner').css('display', 'none');
            $('div#search').css('display', 'block');
            $('div#search').fadeIn(1500);
        });
    }

    /*
     * Creates the pagination links based on the Content-Range and Link headers.
     *
     * jqXHR: the ajax xhr
     */
    function paginate(jqXHR){

        // get the pagination ul
        var paginate = $('ul.pager');
        paginate.empty();
        var info = $('#info');
        info.empty();

        // set the content range info
        var rangeHeader = jqXHR.getResponseHeader('Content-Range');
        var total = rangeHeader.split('/')[1];
        var range = rangeHeader.split('/')[0].split(' ')[1];
        info.append('<span>Displaying ' + range + ' of ' + total + ' results');

        // check if we have a link header
        var a, b;
        var link = jqXHR.getResponseHeader('Link');
        if (link) {
            var links = link.split(',');
            a = links[0];
            b = links[1];
        }
        else {
            // no link header so only one page of results returned
            return;
        }

        /*
         * Configure next/prev links for pagination
         * and handle pagination events
         */
        if (b) {
            var url = b.split(';')[0].trim();
            url = url.slice(1, url.length -1);
            var rel = b.split(';')[1].split('=')[1];
            rel = rel.slice(1, rel.length -1);
            paginate.append('<li id="prev" data-url="' + url + '"><a href="#"><span class="glyphicon glyphicon-chevron-left"/> ' + gettext('Prev') + '</a></li>&nbsp;');
            $('li#prev').on('click', function(){
                var u = this.getAttribute('data-url');
                u == 'undefined' ? listJobs() : listJobs(u);
            });
        }

        if (a) {
            var url = a.split(';')[0].trim();
            url = url.slice(1, url.length -1);
            var rel = a.split(';')[1].split('=')[1];
            rel = rel.slice(1, rel.length -1);
            if (rel == 'prev') {
                paginate.append('<li id="prev" data-url="' + url + '"><a href="#"><span class="glyphicon glyphicon-chevron-left"/> ' + gettext('Prev') + '</a></li>');
                $('li#prev').on('click', function(){
                    var u = this.getAttribute('data-url');
                    u == 'undefined' ? listJobs() : listJobs(u);
                });
            }
            else {
                paginate.append('<li id="next" data-url="' + url + '"><a href="#">Next <span class="glyphicon glyphicon-chevron-right"/></a></li>');
                $('li#next').on('click', function(){
                    var u = this.getAttribute('data-url');
                    u == 'undefined' ? listJobs() : listJobs(u);
                });
            }
        }
    }

    /*
     * Initialize the exports list data table.
     */
    function initDataTable(){
        $('table#jobs').DataTable({
            paging: false,
            info: false,
            filter: false,
            ordering: false,
            searching: false,
            rowId: 'uid',
            "order": [[ 0, "desc" ]],
            columns: [
                {data: 'hdx_dataset_name'},
                {data: 'last_run_at',
                    render: function(data, type, row){
                        var m = moment(data)
                        return m.format('YYYY-MM-DD h:mm') + " (" + m.fromNow() + ")";
                    }  
                },
                {data: 'next_run_at',
                    render: function(data, type, row){
                        var m = moment(data)
                        return m.format('YYYY-MM-DD h:mm') + " (" + m.fromNow() + ")";
                    }  
                },
                {data: null,
                  defaultContent: "Edit",
                  render: function(data,type,row) {
                    return "<a href='/scheduled_exports/edit'>Edit</a>";
                  }
                }
            ]
           });
        // clear the empty results message on initial draw..
        $('td.dataTables_empty').html('');
    }


    /*
     * update the bbox extents on the form
     * used in bbox filtering of results.
     */
    function setBounds(bounds) {
        fmt = '0.0000000000' // format to 10 decimal places
        bounds.transform('EPSG:3857', 'EPSG:4326');
        var xmin = numeral(bounds.left).format(fmt);
        var ymin = numeral(bounds.bottom).format(fmt);
        var xmax = numeral(bounds.right).format(fmt);
        var ymax = numeral(bounds.top).format(fmt);
        var extents = xmin + ',' + ymin + ',' + xmax + ',' + ymax;
        // set the bbox extents on the form and trigger search..
        $('input#bbox').val(extents).trigger('input');
    }

    /*
     * Runs a search.
     * Takes query params from serialized form inputs.
     */
    function runSearch(){
        var url = Config.SCHEDULED_EXPORTS_URL + '?';
        url += searchForm.serialize();
        listJobs(url); // update results table
    }


}());

$(document).ready(function() {
    // initialize the app..
    jobs.list.main();
});
