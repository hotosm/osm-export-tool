/*
    Copyright (C) 2015  Humanitarian OpenStreetMap Team

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/
jobs = {}
jobs.list = (function(){
    
    return {
        init: function(){
            initMap();
            initDataTable();
            listJobs();
        },
    }
    
    function initMap(){
        maxExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");
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
        map = new OpenLayers.Map('map', {options: mapOptions});
        // restrict extent to world bounds to prevent panning..
        map.restrictedExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");
        
        // add base layers
        osm = Layers.OSM
        osm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayer(osm);
        map.zoomToMaxExtent();
        
        job_extents = new OpenLayers.Layer.Vector('extents', {
            displayInLayerSwitcher: false,
            style: {
                strokeWidth: 3.5,
                strokeColor: '#D73F3F',
                fillColor: '#D73F3F',
                fillOpacity: 0.5,
            }
        });
        
        /* required to fire selection events on waypoints */
        var selectControl = new OpenLayers.Control.SelectFeature(job_extents,{
            id: 'selectControl'
        });
        map.addControl(selectControl);
        selectControl.activate();
        
        $("tbody > tr").hover(function() {
            var uid = $(this).attr("id");
            var feature = job_extents.getFeatureByFid(uid);
            selectControl.unselectAll();
            selectControl.select(feature);
        });
        
        job_extents.events.register("featureselected", this, function(e) {
        });
        
        map.addLayer(job_extents);
        return map;
    }
  
    /**
     * Lists the jobs.
     *
     * page: the page number to display
     *
     */
    function listJobs(page){
        var url = Config.JOBS_URL;
        if (page) {
            url += '?page=' + page;
        }
        $.ajax(url)
        .done(function(data, textStatus, jqXHR){
           paginate(jqXHR);
           var tbody = $('table#jobs tbody');
           var table = $('table#jobs').DataTable();
           // clear the existing data and add new page
           table.clear();
           table.rows.add(data).draw();
           // clear the existing features and add the new ones..
           job_extents.destroyFeatures();
           $.each(data, function(idx, job){
                var created = moment(job.created_at).format('MMMM Do YYYY, h:mm:ss');
                var extent = job.extent;
                var geojson = new OpenLayers.Format.GeoJSON({
                        'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                        'externalProjection': new OpenLayers.Projection("EPSG:4326")
                });
                var feature = geojson.read(extent);
                job_extents.addFeatures(feature);
            });
            // zoom to page extents..
            map.zoomToExtent(job_extents.getDataExtent());
        });
        
        /*
        $.ajax(Config.JOBS_URL, {
           
        }).done(function(data, textStatus, jqXHR){
           paginate(jqXHR);
           var tbody = $('table#jobs tbody');
           $.each(data, function(idx, job){
                var created = moment(job.created_at).format('MMMM Do YYYY, h:mm:ss');
                tbody.append('<tr id="' + job.uid + '">' +
                             '<td><a href="/jobs/' + job.uid + '">' + job.name + '</a></td>' +
                             '<td>' + job.description + '</td>' +
                             '<td>' + created + '</td>' +
                             '<td>' + job.region.name + '</td></tr>');
                var extent = job.extent;
                var geojson = new OpenLayers.Format.GeoJSON({
                        'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                        'externalProjection': new OpenLayers.Projection("EPSG:4326")
                });
                var feature = geojson.read(extent);
                job_extents.addFeatures(feature);
            });
            
            map.zoomToExtent(job_extents.getDataExtent());
        });
        */
    }
    
    /*
     * Creates the pagination links based on the Content-Range and Link headers.
     *
     * jqXHR: the ajax xhr
     */
    function paginate(jqXHR){
        var link = jqXHR.getResponseHeader('Link');
        var links = link.split(',');
        var next = links[0];
        var prev = links[1];
        /*
        var rangeHeader = jqXHR.getResponseHeader('Content-Range');
        var total = rangeHeader.split('/')[1];
        var range = rangeHeader.split('/')[0];
        var first = range.split('-')[0].split(' ')[1];
        var last = range.split('-')[1];
        var page_size = (parseInt(last) - parseInt(first)) + 1;
        var num_pages = total / page_size;
        if (total % page_size > 0) {
             num_pages += 1;
        }
        */
        var paginate = $('ul.pagination');
        if (prev) {
            var l = prev.replace('<','');
            var url = l.split(';')[0]
            var page = url.split('=')[1]
            paginate.append('<li id="prev"><a href="#"><span class="glyphicon glyphicon-chevron-left"/> Prev </a></li>');
            $('li#prev').on('click', function(){
                $('ul.pagination').empty();
                listJobs(page);
            });
        }
        if (next) {
            var l = next.replace('<','');
            var url = l.split(';')[0]
            var page = url.split('=')[1]
            paginate.append('<li id="next"><a href="#">Next <span class="glyphicon glyphicon-chevron-right"/></a></li> ');
            $('li#next').on('click', function(){
                $('ul.pagination').empty();
                listJobs(page);
            });
        }
        
    }
    
    /*
     * Initialize the job data table.
     */
    function initDataTable(){
        $('table#jobs').DataTable({
            //data: data,
            paging: false,
            "info": false,
            "filter": false,
            "searching": false,
            "deferLoading": true,
            columns: [
                {
                    data: 'name',
                    render: function(data, type, row){
                        return '<a href="/jobs/' + row.uid + '">' + data + '</a>';
                    }
                },
                {data: 'description'},
                {
                    data: 'created_at',
                    render: function(data, type, row){
                        return moment(data).format('MMMM Do YYYY, h:mm:ss a');
                    }
                },
                {data: 'region.name'}
            ]
           });
    }
    
})();


$(document).ready(function() {
    // initialize the app..
    jobs.list.init();
});

