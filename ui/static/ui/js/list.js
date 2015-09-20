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


jobs = {};
jobs.list = (function(){
    var map;
    var job_extents;
    var bbox;
    var filtering = false;
    var searchForm = $('form#search');
    
    // override unselect so hidden features don't get reset with 'default'
    // style on unselect. 
    OpenLayers.Control.SelectFeature.prototype.unselect = function(feature){
        var layer = feature.layer;
        if (feature.renderIntent == 'hidden') {
            OpenLayers.Util.removeItem(layer.selectedFeatures, feature);
            layer.events.triggerEvent("featureunselected", {feature: feature});
            this.onUnselect.call(this.scope, feature);
        }
        else {
            // Store feature style for restoration later
            this.unhighlight(feature); // resets the renderIntent to 'default'
            OpenLayers.Util.removeItem(layer.selectedFeatures, feature);
            layer.events.triggerEvent("featureunselected", {feature: feature});
            this.onUnselect.call(this.scope, feature);
        }
    }
    
    return {
        main: function(){
            $('div#search').css('display','none');
            $('div#spinner').css('display','block');
            initListMap();
            initPopovers();
            initDataTable();
            initDatePickers();
            loadRegions();
            initSearch();
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
        map = new OpenLayers.Map('list-export-map', {options: mapOptions});
        
        // restrict extent to world bounds to prevent panning..
        map.restrictedExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");
        
        // add base layers
        var osm = new OpenLayers.Layer.OSM("OpenStreetMap");
        osm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayer(osm);
        map.zoomToMaxExtent();
        
        job_extents = new OpenLayers.Layer.Vector('extents', {
            displayInLayerSwitcher: false,
            styleMap: getExtentStyles()
        });
        // add export extents to map
        map.addLayer(job_extents);
        
        /* required to fire selection events on waypoints */
        var selectControl = new OpenLayers.Control.SelectFeature(job_extents,{
            id: 'selectControl'
        });
        map.addControl(selectControl);
        selectControl.activate();
        
        job_extents.events.register("featureselected", this, function(e) {
            var uid = e.feature.data.uid;
            $('tr#' + uid).css('background-color', '#E8E8E8');
        });
        
        job_extents.events.register("featureunselected", this, function(e) {
            var uid = e.feature.data.uid;
            $('tr#' + uid).css('background-color', '#FFF');
        });
        
        /*
         * Double-click handler.
         * Does redirection to export detail page on feature double click.
         */
        var dblClickHandler = new OpenLayers.Handler.Click(selectControl,
                {
                    dblclick: function(e){
                        var feature = this.layer.selectedFeatures[0];
                        var uid = feature.attributes.uid;
                        window.location.href = '/jobs/' + uid;
                    }
                },
                {
                    single: false,
                    double: true,
                    stopDouble: true,
                    stopSingle: false
                }
        )
        dblClickHandler.activate();
        
        
        // add filter selection layer
        bbox = new OpenLayers.Layer.Vector("filter", {
           displayInLayerSwitcher: false,
           styleMap: getTransformStyleMap(),
        });
        map.addLayers([bbox]);
        
        // add a draw feature control for bbox selection.
        var box = new OpenLayers.Control.DrawFeature(bbox, OpenLayers.Handler.RegularPolygon, { 
           handlerOptions: {
              sides: 4,
              snapAngle: 90,
              irregular: true,
              persist: true
           }
        });
        map.addControl(box);
       
       
        // add a transform control to enable modifications to bounding box (drag, resize)
        var transform = new OpenLayers.Control.TransformFeature(bbox, {
           rotate: false,
           irregular: true,
           renderIntent: "transform",
        });
        
        // listen for selection box being added to bbox layer
        box.events.register('featureadded', this, function(e){
            // get selection bounds
            bounds = e.feature.geometry.bounds.clone();
            
            // clear existing selection features
            bbox.removeAllFeatures();
            box.deactivate();
            
            // add a bbox feature based on user selection
            var feature = new OpenLayers.Feature.Vector(bounds.toGeometry());
            bbox.addFeatures(feature);
            
            // enable bbox modification
            transform.setFeature(feature);
            
            // filter the results by bbox
            filtering = true;
            setBounds(bounds);
            map.zoomToExtent(bbox.getDataExtent());
            
        });
        
        // filter results after bbox is moved / modified
        transform.events.register("transformcomplete", this, function(e){
            var bounds = e.feature.geometry.bounds.clone();
            // filter the results by bbox
            filtering = true;
            setBounds(bounds);
        });
        
        // add the transform control
        map.addControl(transform);
        
        // handles click on filter area button
        $("#filter-area").bind('click', function(e){
            /*
             * activate the draw box control
             */
            bbox.removeAllFeatures();
            transform.unsetFeature();
            box.activate();
        });
        
        // clears the search selection area
        $('#clear-filter').bind('click', function(e){
            /*
             * Unsets the bounds on the form and
             * remove features and transforms
             */
            if (filtering) {
                // clear the filter extents
                filtering = false;
                bbox.removeAllFeatures();
                box.deactivate();
                transform.unsetFeature();
                // reset the bounds and reload default search results.
                $('input#bbox').val('-180,-90,180,90');
                runSearch();
            }
        });
        
        // make map div sticky
        /*
        var $mapColumn = $('#map-column');
        var mapTop = $mapColumn.offset().top;
        $(window).scroll(function(){ // scroll event
            var bannerHeight = $('#banner').height();
            var navHeight = $('.navbar.navbar-inverse').height();
            var headerHeight = bannerHeight + navHeight;
            var windowTop = $(window).scrollTop(); // returns number
            if (mapTop < windowTop) {
                $mapColumn.css({ 'position': 'fixed', 'right': '0px', 'top': '0px' });
                $('#list-export-map').css({'right': '0', 'z-index': '-1000'});
            }
            else {
                $mapColumn.css({'position': 'static', 'right': '0px'});
                $('#list-export-map').css('right', '0');
            }
        });
        */
    }
    
    
    /*
     * get the style map for the filter bounding box.
     */
    function getTransformStyleMap(){
        return new OpenLayers.StyleMap({
                    "default": new OpenLayers.Style({
                        fillColor: "blue",
                        fillOpacity: 0.05,
                        strokeColor: "blue",
                        graphicZIndex : 1,
                    }),
                    // style for the select extents box
                    "transform": new OpenLayers.Style({
                        display: "${getDisplay}",
                        cursor: "${role}",
                        pointRadius: 6,
                        fillColor: "blue",
                        fillOpacity: 1,
                        strokeColor: "blue",
                        graphicZIndex : -1,
                    },
                    {
                        context: {
                            getDisplay: function(feature) {
                                // hide the resize handles except at the south-east corner
                                return  feature.attributes.role === "n-resize"  ||
                                        feature.attributes.role === "ne-resize" ||
                                        feature.attributes.role === "e-resize"  ||
                                        feature.attributes.role === "s-resize"  ||
                                        feature.attributes.role === "sw-resize" ||
                                        feature.attributes.role === "w-resize"  ||
                                        feature.attributes.role === "nw-resize" ? "none" : ""
                            }
                        }
                    })
                });
    }
    
    
    /**
     * Returns the styles for job extent display.
     */
    function getExtentStyles(){
        // default style for export extents
        var defaultStyle = new OpenLayers.Style({
            strokeWidth: 3.5,
            strokeColor: '#D73F3F',
            fillColor: '#D73F3F',
            fillOpacity: 0.1,
            //graphicZIndex : 50,
        });
        // export extent selection style
        var selectStyle = new OpenLayers.Style({
            strokeWidth: 3.5,
            strokeColor: 'blue',
            fillColor: 'blue',
            fillOpacity: 0.1,
            //graphicZIndex : 40,
        });
        
        var hiddenStyle = new OpenLayers.Style({
            display: 'none'
        });
        
        var styles = new OpenLayers.StyleMap(
        {
            "default": defaultStyle,
            "select": selectStyle,
            "hidden": hiddenStyle
        });
        
        return styles;
        
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
            url = Config.JOBS_URL;
        }
        $.ajax(url)
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
            
            // toggle feature visibility
            $('span.toggle-feature').on('click', function(e){
                var selectControl = map.getControlsBy('id','selectControl')[0];
                var uid = $(e.target).attr('id');
                for(var f=0; f < job_extents.features.length; f++){
                    var feature = job_extents.features[f];
                    if(feature.attributes.uid === uid){;
                        var visible = feature.getVisibility();
                        if (visible) {
                            feature.renderIntent = 'hidden';
                            selectControl.unselect(feature);
                            job_extents.redraw();
                            $('tr#' + uid).addClass('warning');
                        }
                        else {
                            feature.renderIntent = 'default';
                            $('tr#' + uid).removeClass('warning');
                            job_extents.redraw();
                        }
                   }
                }
                $(this).toggleClass('glyphicon-eye-open glyphicon-eye-close');
            });
            
            // clear the existing export extent features and add the new ones..
            job_extents.destroyFeatures();
            $.each(data, function(idx, job){
                 var extent = job.extent;
                 var geojson = new OpenLayers.Format.GeoJSON({
                         'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                         'externalProjection': new OpenLayers.Projection("EPSG:4326")
                 });
                 var feature = geojson.read(extent);
                 job_extents.addFeatures(feature);
             });
           
            /*
             * Zoom to extents depending on whether
             * bbox filtering is applied or not..
             */
            if (filtering) {
                map.zoomToExtent(bbox.getDataExtent());
            }
            else {
                var bounds = job_extents.getDataExtent();
                if (bounds) {
                    map.zoomToExtent(job_extents.getDataExtent());
                }
                else {
                    // zoom to max if no results
                    map.zoomToMaxExtent();
                }
            }
            
            // select bbox features based on row hovering
            $('table#jobs tbody tr').hover(
                // mouse in
                function(e){
                    var selectControl = map.getControlsBy('id','selectControl')[0];
                    var uid = $(this).attr('id');                    
                    for(var f=0; f < job_extents.features.length; f++){
                        var feature = job_extents.features[f];
                        if(feature.attributes.uid === uid && feature.renderIntent != 'hidden'){
                            selectControl.select(feature);  
                        }
                        else {
                            selectControl.unselect(feature);
                        }
                    }
                },
                // mouse out
                function(e){
                    var selectControl = map.getControlsBy('id','selectControl')[0];
                    selectControl.unselectAll();
                }
            );
            
            // set message if no results returned from this url..
            $('td.dataTables_empty').html('No search results found.'); 
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
            ordering: true,
            searching: false,
            rowId: 'uid',
            "order": [[ 3, "desc" ]],
            columns: [
                {
                    data: 'name',
                    render: function(data, type, row){
                        return '<a id="' + row.uid + '" href="/jobs/' + row.uid + '">' + data + '</a>';
                    }
                },
                {data: 'description'},
                {data: 'event'},
                {
                    data: 'created_at',
                    render: function(data, type, row){
                        return moment(data).format('YYYY-MM-DD hh:mm a');
                    }
                },
                {data: 'region.name'},
                {
                    data: 'published',
                    orderable:false,
                    render: function(data, type, row){
                        var published = row.published;
                        var owner = $('span#user').text();
                        var $div = $('<div>');
                        var $toggleSpan = $('<span id="' + row.uid + '" class="toggle-feature glyphicon glyphicon-eye-open"></span>');
                        var $pubSpan = $('<span class="glyphicon"></span>');
                        $div.append($pubSpan);
                        if (owner === row.owner) {
                            var $userSpan = $('<span class="glyphicon glyphicon-user"></span>');
                            $div.append($userSpan);
                        }
                        else {
                            //$div.append($('<span class="glyphicon glyphicon-none">&nbsp;</span>'));
                            var $userSpan = $('<span class="fa fa-users"></span>');
                            $div.append($userSpan);
                        }
                        if (published) {
                            $pubSpan.addClass('glyphicon-globe');
                        }
                        else {
                            $pubSpan.addClass('glyphicon-time');
                        }
                        $div.append($toggleSpan);
                        
                        // return the html
                        return $div[0].outerHTML;
                    }
                }
            ],
            rowCallback: function(row, data, index){
                var user = $('span#user').text();
                var owner = user === data.owner ? 'me' : data.owner;
                if (data.published) {
                    $(row).tooltip({
                        'html': true,
                        'title': gettext('Published export.') + '<br/>' + gettext('Created by: ') + owner
                    });
                }
                else {
                    var expires = moment(data.created_at).add(2, 'days').format('YYYY-MM-DD hh:mm a');
                    $(row).tooltip({
                        'html': true,
                        'title': gettext('Unpublished export.') + '<br/>' + gettext('Expires: ') + expires + '.<br/>' + gettext('Created by: ') + owner
                    });
                }
            }
           });
        // clear the empty results message on initial draw..
        $('td.dataTables_empty').html('');
    }
    
    /**
     * Initialize the start / end date pickers.
     */
    function initDatePickers(){
        $('#start-date').datetimepicker({
            showTodayButton: true,
            // show one month of exports by default
            defaultDate: moment().subtract(1, 'month'),
            format: 'YYYY-MM-DD HH:MM'
        });
        $('#end-date').datetimepicker({
            showTodayButton: true,
            // default end-date to now.
            defaultDate: moment(),
            format: 'YYYY-MM-DD HH:MM'
        });
        $("#start-date").on("dp.change", function(e){
            runSearch();
        });
        $("#end-date").on("dp.change", function(e){
            runSearch();
        });
        
    }
    
    /**
     * Populates the search form's region selection input.
     */
    function loadRegions(){
        $.ajax(Config.REGIONS_URL)
        .done(function(data, textStatus, jqXHR){
            var regionSelect = $('select#region-select');
            $.each(data.features, function(idx, feature){
                var name = feature.properties.name;
                regionSelect.append('<option name="' + name + '">' + name + '</option>');
            })
        });
    }
    
    /**
     * Initializes the feature tag filter.
     */
    function initFeatureTagFilter() {
        
        var cities = new Bloodhound({
            /*
            datumTokenizer: function(d) {
                return Bloodhound.tokenizers.whitespace(d.value); 
            },
            */
            datumTokenizer: Bloodhound.tokenizers.whitespace,
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            prefetch: {
                url: Config.HDM_TAGS_URL,
                /*
                filter: function(data) {
                    return $.map(data, function(str) {
                        return { value: str };
                    });
                },
                */
            }
        });
        
        $('#features').tagsinput({
            typeaheadjs: {
              name: 'cities',
              displayKey: 'value',
              valueKey: 'value',
              source: cities.ttAdapter()
            }
        });
        
        
        function lookupOSMTags(q, sync) {
            if (q === '') {
                sync(osm_tags.get('Detroit Lions', 'Green Bay Packers', 'Chicago Bears'));
            }
            else {
                osm_tags.search(q, sync);
            }
        }

        var input = $('input#features');
        /*
        tgsinput.tagsinput({
            typeaheadjs: {
                name: 'tags',
                displayKey: 'name',
                valueKey: 'name',
                source: tags.ttAdapter()
            }
        });
        */
        
        $(".twitter-typeahead").css('display', 'inline');
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
     * Search export jobs.
     */ 
    function initSearch(){
        // update state on filter toggle button
        $('a#filter-toggle').click(function(e){
            $(e.target).children("i.indicator").toggleClass(
                'glyphicon-chevron-down glyphicon-chevron-up'
            );
        });
        
        // run search on search form input events
        $('form#search input').bind('input', function(e){
            runSearch();
        });
        
        // run search on selection changes
        $('select').bind('change', function(e){
           runSearch(); 
        });
        
        // run search on user filtering state change
        $('input#user-check').bind('click', function(e){
            // pull the username out of the dom
            var username = $('span#user').text();
            var $this = $(this);
            // $this will contain a reference to the checkbox   
            if ($this.is(':checked')) {
                // set the username on the form input
                $('input#user').val(username);
                runSearch(); 
            } else {
                $('input#user').val('');
                runSearch();
            }
        });
    }
    
    /*
     * Runs a search.
     * Takes query params from serialized form inputs.
     */
    function runSearch(){
        var url = Config.JOBS_URL + '?';
        url += searchForm.serialize();
        listJobs(url); // update results table
    }
    
    /*
     * Initialise UI popovers.
     */
    function initPopovers(){
        $('a#filter-toggle').popover({
            //title: 'Select Formats', 
            content: gettext("Filter the exports based on keywords in the search box and/or between a start and end date"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'right'
        });
        $('div#myexports').popover({
            //title: 'Select Formats', 
            content: gettext("Show your personal export(s)"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'top'
        });
    }
    
}());


$(document).ready(function() {
    // initialize the app..
    jobs.list.main();
});

