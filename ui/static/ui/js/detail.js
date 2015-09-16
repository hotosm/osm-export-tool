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
exports = {}
exports.detail = (function(){
    
        
    return {
        init: function(){
            parts = window.location.href.split('/');
            var job_uid = parts[parts.length -2];
            exports.detail.job_uid = job_uid;
            exports.detail.timer = false;
            initMap();
            initPopovers();
            loadJobDetail();
            loadSubmittedRunDetails();
            loadCompletedRunDetails();
        },
    }
    
    /**
     * Initialize the export overview map.
     */
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
        map = new OpenLayers.Map('extents', {options: mapOptions});
        
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
                fillColor: 'transparent',
                fillOpacity: 0.8,
            }
        });
        
        map.addLayer(job_extents);
        map.restrictedExtent = map.getExtent();
        return map;
    }
  
    /**
     * Loads the job details.
     */
    function loadJobDetail(){
        var job_uid = exports.detail.job_uid;
        $.getJSON(Config.JOBS_URL + '/' + job_uid, function(data){
            // keep a reference to the job..
            exports.detail.job = data;
            $('#uid').html(data.uid);
            $('#name').html(data.name);
            $('#description').html(data.description);
            $('#event').html(data.event);
            $('#created_by').html(data.owner);
            var published = data.published ? 'Publicly' : 'Privately';
            $('#published').html(published);
            var created = moment(data.created_at).format('h:mm:ss a, MMMM Do YYYY');
            $('#created').html(created);
            var formats = data.exports;
            for (i = 0; i < formats.length; i++){
                $('#formats').append(formats[i].name + '<br/>');
            }
            
            // features
            var model = data.tags.length > 0 ? data.tags[0].data_model : null;
            
            switch (model){
                case 'HDM':
                    $('#osm-feature-tree').css('display','none');
                    $('#hdm-feature-tree').css('display','block');
                    $('#filelist').css('display', 'none');
                    initHDMFeatureTree(data.tags);
                    break;
                case 'OSM':
                    $('#hdm-feature-tree').css('display','none');
                    $('#osm-feature-tree').css('display','block');
                    $('#filelist').css('display', 'none');
                    initOSMFeatureTree(data.tags);
                    break;
                case 'PRESET':
                    $('#hdm-feature-tree').css('display','none');
                    $('#osm-feature-tree').css('display','none');
                    $('#filelist').css('display', 'block');
                    initPresetList(data.configurations);
                    break;
                default:
                    break;
            }
            
            var extent = data.extent;
            var geojson = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
            });
            var feature = geojson.read(extent, 'Feature');
            job_extents.addFeatures(feature);
            map.zoomToExtent(job_extents.getDataExtent());
            var bounds = feature.geometry.bounds.clone();
            var area = bounds.transform('EPSG:3857', 'EPSG:4326').toGeometry().getGeodesicArea() / 1000000; // sq km
            // format the area and max bounds for display..
            var area_str = numeral(area).format('0,0');
            $('#extent').html(area_str + ' sq km');
            /*
             * Check for current user.
             * Display delete button if
             * current user matches the owner of the job.
             */
            var user = $('span#user').html();
            if (user === data.owner) {
                $('button#delete').css('display', 'block');
            }
            buildDeleteDialog();
            buildFeatureDialog();
            
        }).fail(function(jqxhr, textStatus, error) {
            if (jqxhr.status == 404) {
                $('#details-row').css('display', 'none');
                // display error info..
                $('#error-info').css('display', 'block'); 
            }
        });
        
        // handle re-run click events..
        $('button#rerun').bind('click', function(e){
            $.ajax({
                cache: false,
                url: Config.RERUN_URL + exports.detail.job_uid,
                success: function(data){
                    // initialize the submitted run panel immediately
                    initSumtittedRunPanel([data]);
                    // then start the check interval..
                    startRunCheckInterval();
                }
            })
            /*
            $.get(Config.RERUN_URL + exports.detail.job_uid,
                function(data, textStatus, jqXhr){
                    // initialize the submitted run panel immediately
                    initSumtittedRunPanel([data]);
                    // then start the check interval..
                    startRunCheckInterval();
            });
            */
        });
        
        // handle clone event
        $('button#clone').bind('click', function(e){
            window.location.href = '/jobs/clone/' + exports.detail.job_uid;
        });
    }
    
    /**
      * Loads the completed run details.
      * 
      * Parameters:
      * expand_first {Object} - whether to expand the first completed run.
      */
    function loadCompletedRunDetails(expand_first){
        var job_uid = exports.detail.job_uid;
        var $runPanel = $('#completed_runs > .panel-group');
        $.getJSON(Config.RUNS_URL + '?status=COMPLETE&job_uid=' + job_uid, function(data){
            // clear the completed run panel
            $runPanel.empty();
            // hide the submitted run panel
            if (!exports.detail.timer) {
                $('#submitted_runs > .panel-group').empty();
                $('#submitted_runs').css('display', 'none');
            }
            
            $.each(data, function(index, run){
                var started = moment(run.started_at).format('h:mm:ss a, MMMM Do YYYY');
                var finished = moment(run.finished_at).format('h:mm:ss a, MMMM Do YYYY');
                var duration = moment.duration(run.duration).humanize();
                var status_class = run.status === 'COMPLETED' ? 'alert alert-success' : 'alert alert-warning';
                var expanded = !exports.detail.timer && index === 0 ? 'in' : '';
                var context = { 'run_uid': run.uid, 'status': run.status,
                                'started': started, 'finished': finished,
                                'duration': duration,'status_class': status_class,
                                'expanded': expanded};
                var template = getCompletedRunTemplate();
                var html = template(context);
                $runPanel.append(html);
                
                // add task info
                $taskDiv = $runPanel.find('div#' + run.uid).find('#tasks').find('table');
                var tasks = run.tasks;
                $.each(tasks, function(i, task){
                    var errors = task.errors;
                    var result = task.result;
                    var status = task.status;
                    var duration = numeral(task.duration).format("HH:mm:ss.SSS");
                    switch (task.name) {
                        case 'KML Export':
                            if (status === 'SUCCESS') {
                                $taskDiv.append('<tr><td><a href="' + result.url + '">' + gettext('Google Earth (KMZ) File') + '</a></td><td>' + duration + '</td><td>' +
                                    result.size + '</td></tr>');
                            }
                            break;
                        case 'OSM2PBF':
                            if (status === 'SUCCESS') {
                                $taskDiv.append('<tr><td><a href="' + result.url + '">' + gettext('OpenStreetMap (PBF) File') + '</a></td><td>' + duration + '</td><td>' +
                                    result.size + '</td></tr>');
                            }
                            break;
                        case 'Default Shapefile Export':
                            if (status === 'SUCCESS') {
                                $taskDiv.append('<tr><td><a href="' + result.url + '">' + gettext('ESRI Shapefile (SHP)') + '</a></td><td>' + duration + '</td><td>' +
                                    result.size + '</td></tr>');
                            }
                            break;
                        case 'OBF Export':
                            if (status === 'SUCCESS') {
                                $taskDiv.append('<tr><td><a href="' + result.url + '">' + gettext('OSMAnd (OBF) File') + '</a></td><td>' + duration + '</td><td>' +
                                    result.size + '</td></tr>');
                            }
                            break;
                        case 'Garmin Export':
                            if (status === 'SUCCESS') {
                                $taskDiv.append('<tr><td><a href="' + result.url + '">' + gettext('Garmin Map (IMG) File') + '</a></td><td>' + duration + '</td><td>' +
                                    result.size + '</td></tr>');
                            }
                            break;
                        case 'SQLITE Export':
                            if (status === 'SUCCESS') {
                                $taskDiv.append('<tr><td><a href="' + result.url + '">' + gettext('SQlite Database File') + '</a></td><td>' + duration + '</td><td>' +
                                    result.size + '</td></tr>');
                            }
                            break;
                        case 'Thematic Shapefile Export':
                            if (status === 'SUCCESS') {
                                $taskDiv.append('<tr><td><a href="' + result.url + '">Thematic ESRI Shapefile (SHP)</a></td><td>' + duration + '</td><td>' +
                                    result.size + '</td></tr>');
                            }
                            break;
                        case 'Generate Preset':
                            if (status === 'SUCCESS') {
                                $taskDiv.append('<tr><td><a href="' + result.url + '" target="_blank">' + gettext('Custom JOSM Preset (XML)') + '</a></td><td>' + duration + '</td><td>' +
                                    result.size + '</td></tr>');
                            }
                            break;
                    }
                    
                    if (errors.length > 0) {
                        $tr = $('tr#exceptions');
                        $tr.css('display', 'table-row');
                        $errorsDiv = $runPanel.find('div#' + run.uid).find('#errors').find('table');
                        $errorsDiv.append('<tr><td>' + task.name + '</td><td>' + task.errors[0].exception + '</td></tr>');
                    }
                });
            });
        }); 
      
    }
    
    /**
     * Gets a template for displaying completed run details.
     */
    function getCompletedRunTemplate(context) {
        var html = $('  <div class="panel panel-default"> \
                            <div class="panel-heading" role="tab"> \
                                <h4 class="panel-title"> \
                                    <a role="button" data-toggle="collapse" data-parent="#completed_runs" href="#{{ run_uid }}" \
                                        aria-expanded="true" aria-controls="{{ run_uid }}"> \
                                        {{ finished }} \
                                    </a> \
                                </h4> \
                            </div> \
                            <div id="{{ run_uid }}" class="panel-collapse collapse {{ expanded }}" role="tabpanel"> \
                                <div class="panel-body"> \
                                    <div class="row"> \
                                       <div class="col-md-12"> \
                                           <div class="table-responsive"> \
                                               <table class="table"> \
                                                   <tr><td><strong>Run Id:</strong></td><td><div id="runuid">{{ run_uid }}</div></td></tr> \
                                                   <tr><td><strong>Status:</strong></td><td><div id="status" class="{{ status_class }}" role="alert">{{ status }}</div></td></tr> \
                                                   <tr><td><strong>Started:</strong></td><td><div id="started">{{ started }}</div></td></tr> \
                                                   <tr><td><strong>Finished:</strong></td><td><div id="finished">{{ finished }}</div></td></tr> \
                                                   <tr><td><strong>Duration:</strong></td><td><div id="duration">{{ duration }}</div></td></tr> \
                                                   <tr><td><strong>Download:</strong></td><td> \
                                                        <div id="tasks"> \
                                                            <table class="table table-condensed" width="100%"> \
                                                            <thead><th>File</th><th>Duration</th><th>Size</th></thead> \
                                                            </table> \
                                                        </div> \
                                                    </td></tr> \
                                                    <tr id="exceptions"><td><strong>Errors:</strong></td><td> \
                                                        <div id="errors"> \
                                                            <table class="table table-condensed" width="100%"> \
                                                            <thead><th>Task</th><th>Error</th></thead> \
                                                            </table> \
                                                        </div> \
                                                    </td></tr> \
                                               </table> \
                                           </div> \
                                       </div> \
                                    </div> \
                                </div> \
                            </div> \
                        </div>').html();
        var template = Handlebars.compile(html);
        return template;
    }
    
    
    /**
      * Loads the job details.
      * This occurs initially on page load..
      */
    function loadSubmittedRunDetails(){
        var job_uid = exports.detail.job_uid;
        $.ajax({
            cache: false,
            url: Config.RUNS_URL + '?status=SUBMITTED&job_uid=' + job_uid,
            success: function(data){
                if (data.length > 0) {
                    initSumtittedRunPanel(data);
                    startRunCheckInterval();
                }
            }
        });
    }
    
    /**
     * Initializes the submitted run panel.
     */
    function initSumtittedRunPanel(data){
        var $runPanel = $('#submitted_runs > .panel-group');
        $runPanel.empty();
        if (data.length > 0) {
            // display the submitted run
            $('#submitted_runs').css('display', 'block');
            // disable the re-run button..
            $('button#rerun').prop('disabled', true);
            $('button#delete').prop('disabled', true);
        }
        else {
            // stop the interval timer..
            clearInterval(exports.detail.timer);
            // hide the submitted run div
            $('#submitted_runs').css('display', 'none');
            // reload the completed runs to show the latest run..
            loadCompletedRunDetails();
            // enable the re-run button..
            $('button#rerun').prop('disabled', false);
            $('button#delete').prop('disabled', false);
            return;
        }
        $.each(data, function(index, run){
            var started = moment(run.started_at).format('h:mm:ss a, MMMM Do YYYY');
            var duration = moment.duration(run.duration).humanize();
            var status_class = run.status === 'SUBMITTED' ? 'alert alert-info' : 'alert alert-warning';
            var expanded = index === 0 ? 'in' : ''; // collapse all for now..
            var context = { 'run_uid': run.uid, 'status': run.status,
                            'started': started, 'status_class': status_class,
                            'expanded': expanded};
            var template = getSubmittedRunTemplate();
            var html = template(context);
            $runPanel.append(html);
            // add task info
            $taskDiv = $('div#' + run.uid).find('#tasks').find('table');
            var tasks = run.tasks;
            $.each(tasks, function(i, task){
                var result = task.result;
                var status = task.status;
                var duration = task.duration ? numeral(task.duration).format("HH:mm:ss.SSS") : ' -- '; 
                switch (task.name) {
                    case 'OverpassQuery':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('Extract OpenStreetMap Data') + '</td><td>' + duration + '</td><td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('Extract OpenStreetMap Data') + '</td><td>' + duration + '</td><td>' + result.size + '</td><td>' + task.status + '</td></tr>');
                        }
                        break;
                    case 'KML Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('Google Earth (KMZ)') + '</td><td>' + duration + '</td><td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td><a href="' + result.url + '">' + gettext('Google Earth (KMZ) File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td></tr>');
                        }
                        break;
                    case 'OSM2PBF':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('OpenStreetMap (PBF) File') + '</td><td>' + duration + '</td><td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td><a href="' + result.url + '">' + gettext('OpenStreetMap (PBF) File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td></tr>');
                        }
                        break;
                    case 'Default Shapefile Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('ESRI Shapefile (SHP)') + '</td><td>' + duration + '</td><td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td><a href="' + result.url + '">' + gettext('ESRI Shapefile (SHP)') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td></tr>');
                        }
                        break;
                    case 'Thematic Shapefile Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('Thematic ESRI Shapefile (SHP)') + '</td><td>' + duration + '</td><td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td><a href="' + result.url + '">' + gettext('Thematic ESRI Shapefile (SHP)') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td></tr>');
                        }
                        break;
                    case 'OBF Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('OSMAnd (OBF) File') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td><a href="' + result.url + '">' + gettext('OSMAnd (OBF) File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td></tr>');
                        }
                        break;
                    case 'Garmin Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('Garamin Map (IMG) File') + '</td><td> -- <td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td><a href="' + result.url + '">' + gettext('Garmin Map (IMG) File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td></tr>');
                        }
                        break;
                    case 'SQLITE Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid + '"><td>' + gettext('SQlite Database File') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td><a href="' + result.url + '">' + gettext('SQlite Database File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td></tr>');
                        }
                        break;
                    case 'OSMSchema':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('Generate OpenStreetMap Schema') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>'+ gettext('Generate OpenStreetMap Schema') + '</td><td>' + duration + '</td><td></td><td>' + task.status + '</td></tr>');
                        }
                        break;
                    case 'Generate Preset':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('Genrerate JOSM Preset') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td></tr>');
                        }
                        else {
                            cls = status.toLowerCase();
                            $taskDiv.append('<tr class="' + cls + '" id="' + task.uid +'"><td>' + gettext('Generate JOSM Preset') + '</td><td>' + duration + '</td><td></td><td>' + task.status + '</td></tr>');
                        }
                        break;
                }
            });
        });
    }
    
    /**
     * Gets a template for displaying submitted run details.
     */
    function getSubmittedRunTemplate(context) {
        var html = $('  <div class="panel panel-default"> \
                            <!-- \
                            <div class="panel-heading" role="tab"> \
                                <h4 class="panel-title"> \
                                    <a role="button" data-toggle="collapse" data-parent="#submitted_runs" href="#{{ run_uid }}" \
                                        aria-expanded="true" aria-controls="{{ run_uid }}"> \
                                        {{ finished }} \
                                    </a> \
                                </h4> \
                            </div> \
                            --> \
                            <div id="{{ run_uid }}" class="panel-collapse collapse {{ expanded }}" role="tabpanel"> \
                                <div class="panel-body"> \
                                    <div class="row"> \
                                       <div class="col-md-12"> \
                                           <div class="table-responsive"> \
                                               <table class="table"> \
                                                   <tr><td><strong>Run Id:</strong></td><td><div id="runuid">{{ run_uid }}</div></td></tr> \
                                                   <tr><td><strong>Status:</strong></td><td><div id="status" class="{{ status_class }}" role="alert">{{ status }}</div></td></tr> \
                                                   <tr><td><strong>Started:</strong></td><td><div id="started">{{ started }}</div></td></tr> \
                                                   <tr><td><strong>Tasks:</strong></td><td> \
                                                        <div id="tasks"> \
                                                            <table class="table table-condensed" width="100%"> \
                                                            <thead><th>Name</th><th>Duration</th><th>Size</th><th>Status</th></thead> \
                                                            </table> \
                                                        </div> \
                                                    </td></tr> \
                                                    <tr><td></td></tr> \
                                               </table> \
                                           </div> \
                                       </div> \
                                   </div> \
                                </div> \
                            </div> \
                        </div>').html();
        var template = Handlebars.compile(html);
        return template;
    }
    
    /**
     * Updates the submitted run details to show task status.
     *
     * data: the data to update
     */
    function updateSubmittedRunDetails(data){
        if (data.length > 0) {
            var run = data[0];
            var run_uid = run.uid;
            var $runDiv = $('#' + run_uid);
            var tasks = run.tasks;
            $.each(tasks, function(i, task){
                var uid = task.uid;
                var result = task.result;
                var status = task.status;
                var duration = task.duration ? numeral(task.duration).format("HH:mm:ss.SSS") : ' -- ';
                var $tr = $runDiv.find('table').find('tr#' + uid);
                switch (task.name) {
                    case 'OverpassQuery':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('Extract OpenStreetMap Data') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('Extract OpenStreetMap Data') + '</td><td>' + duration + '</td><td>' + result.size + '</td><td>' + task.status + '</td>');
                        }
                        break;
                    case 'KML Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('Google Earth (KMZ)') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td><a href="' + result.url + '">' + gettext('Google Earth (KMZ) File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td>');
                        }
                        break;
                    case 'OSM2PBF':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('OpenStreetMap (PBF) File') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td><a href="' + result.url + '">' + gettext('OpenStreetMap (PBF) File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td>');
                        }
                        break;
                    case 'Default Shapefile Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('ESRI Shapefile (SHP)') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td><a href="' + result.url + '">' + gettext('ESRI Shapefile (SHP)') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td>');
                        }
                        break;
                    case 'Thematic Shapefile Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('Thematic ESRI Shapefile (SHP)') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td><a href="' + result.url + '">' + gettext('Thematic ESRI Shapefile (SHP)') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td>');
                        }
                        break;
                    case 'OBF Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('OSMAnd (OBF) File') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td><a href="' + result.url + '">' + gettext('OSMAnd (OBF) File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td>');
                        }
                        break;
                    case 'Garmin Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('Garamin Map (IMG) File') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td><a href="' + result.url + '">' + gettext('Garmin Map (IMG) File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td>');
                        }
                        break;
                    case 'SQLITE Export':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('SQlite Database File') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td><a href="' + result.url + '">' + gettext('SQlite Database File') + '</a></td><td>' + duration + '</td><td>' +
                            result.size + '</td><td>' + task.status + '</td>');
                        }
                        break;
                    case 'OSMSchema':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>Generate OpenStreetMap Schema</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('Generate OpenStreetMap Schema') + '</td><td>' + duration + '</td><td> -- </td><td>' + task.status + '</td>');
                        }
                        break;
                    case 'Generate Preset':
                        if (status === 'PENDING' || status === 'RUNNING' || status === 'FAILED') {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('Generate JOSM Preset') + '</td><td> -- </td><td> -- </td><td>' + task.status + '</td>');
                        }
                        else {
                            $tr.removeClass();
                            $tr.addClass(status.toLowerCase());
                            $tr.html('<td>' + gettext('Generate JOSM Preset') + '</td><td>' + duration + '</td><td> -- </td><td>' + task.status + '</td>');
                        }
                        break; 
                }
               
            });
        }
        else {
            // stop the interval timer..
            clearInterval(exports.detail.timer);
            exports.detail.timer = false;
            
            // reload the completed runs to show the latest run..
            loadCompletedRunDetails();
            
            // enable the re-run button..
            $('button#rerun').prop('disabled', false);
            $('button#delete').prop('disabled', false);
        }
    } 
    
    /*
     * Starts an interval timer to periodically
     * report the status of a currently running job.
     */
    function startRunCheckInterval(){
        var job_uid = exports.detail.job_uid;
        /*
         * Collapse the completed run panels before
         * updating the submitted run panel.
         * Only do this once before interval check kicks in.
         */
        if (!exports.detail.timer) {
            $('#completed_runs .panel-collapse').removeClass('in'); // fix this..
        }
        
        /*
         * Run a check on the submitted job
         * at an interval of 3 seconds.
         */
        exports.detail.timer = setInterval(function(){
            var job_uid = exports.detail.job_uid;
            var url = Config.RUNS_URL + '?job_uid=' +  job_uid + '&status=SUBMITTED&format=json';
            $.ajax({
                cache: false,
                url: url,
                dataType: 'json',
                cache: false,
                success: function(data, textStatus, jqXhr){
                    updateSubmittedRunDetails(data);
                }
            });
        }, 3000);
    }
    
    function buildDeleteDialog(){
        
        var that = this;
        var options = {
            url: Config.JOBS_URL + '/' + exports.detail.job_uid,
            dataType: 'json',
            beforeSubmit: function(arr, $form, options) {
            },
            success: function(data, status, xhr) {
                if (status == 'nocontent') {
                    $('#details-row').css('display', 'none');
                    // display delete info..
                    $('#delete-info').css('display', 'block');
                } 
            },
            error: function(xhr, status, error){
                var json = xhr.responseJSON
                console.log(error);
            },
        }
        
       var modalOpts = {
            keyboard: true,
            backdrop: 'static',
        }
        
        $("button#delete").bind('click', function(e){
            // stop form getting posted..
            e.preventDefault(); 
            $("#deleteExportModal").modal(modalOpts, 'show');
        });
        
        $("#deleteConfirm").click(function(){
            // post form..
            $('#deleteForm').ajaxSubmit(options);
            $("#deleteExportModal").modal('hide');
        });
    }
    
    function buildFeatureDialog(){
        var modalOpts = {
            keyboard: true,
            backdrop: 'static',
        }
        $("button#features").bind('click', function(e){
            $("#featuresModal").modal(modalOpts, 'show');
        });
    }
    
    function initPopovers(){
        $('button#rerun').popover({
            //title: 'Select Formats', 
            content: gettext("Run the export with the same geographic location and settings"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'top'
        });
        $('button#clone').popover({
            //title: 'Select Formats', 
            content: gettext("Clone this export while adjusting the settings"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'top'
        });
        
    }
    
    // ----- FEATURE SELECTION TREES ----- //
    
    /*
     * Initialises the HDM feature tree.
     */
    function initHDMFeatureTree(tags){
        
        $.get(Config.HDM_TAGS_URL, function(data){
            var level_idx = 0;
            var $tree = $('#hdm-feature-tree ul.nav-list');
            if (typeof data == 'object') {
                traverse(data, $tree, level_idx);
            }
            
            /*
             * Recursively builds the feature tree.
             */
            function traverse(data, $level, level_idx){
                $.each(data, function(k,v){
                    if ($(v).attr('displayName')){
                        var name = $(v).attr('displayName');
                        var tag = $(v).attr('tag');
                        var key = tag.split(':')[0];
                        var val = tag.split(':')[1];
                        var geom = $(v).attr('geom');
                        geom_str = geom.join([separator=',']);
                        var $entry = $('<li class="entry"><label><i class="fa fa-square-o fa-fw"></i>' + name + '</label>' +
                                           '<div class="checkbox tree-checkbox"><input class="entry" type="checkbox" data-model="HDM" data-geom="' +
                                            geom_str + '" data-key="' + key + '" data-val="' + val +'" data-name="' + name + '" disabled/></div>' +
                                        '</li>');
                        $level.append($entry);
                    }
                    else {
                        var collapse = level_idx > 0 ? 'collapse' : '';
                        var state = level_idx == 0 ? 'open' : 'closed';
                        var icon = level_idx == 0 ? 'fa-minus-square-o' : 'fa-plus-square-o';
                        var root = level_idx == 0 ? 'root' : '';
                        var $nextLevel = $('<li class="level nav-header ' + state + ' ' + root + '"><label><i class="level fa ' + icon + ' fa-fw"></i>' + k + '</label>' + 
                                            '<div class="checkbox tree-checkbox"><input class="level" type="checkbox" disabled/></div>');
                        var $nextUL = $('<ul class="nav nav-list sub-level ' + collapse + '">');
                        $nextLevel.append($nextUL);
                        $level.append($nextLevel);
                        level_idx += 1;
                        traverse(v, $nextUL, level_idx);
                    }
                });
            }
            
            $.each(tags, function(idx, tag){
                var key = tag.key;
                var val = tag.value;
                // check the corresponding input on the tree
                var $input = $('#hdm-feature-tree').find('input[data-key="' + key + '"][data-val="' + val + '"]');
                $input.prop('checked', true);
                $input.prop('disabled', false);
                // check the parent levels
                $.each($input.parentsUntil('#hdm-feature-tree', 'li.level'),
                       function(idx, level){
                    $(level).children('div.tree-checkbox').find('input.level').prop('checked', true);
                    $(level).children('div.tree-checkbox').find('input.level').prop('disabled', false);
                });
            });
                    
            // toggle level collapse
            $('#hdm-feature-tree li.level > label').bind('click', function(e){
                if ($(this).parent().hasClass('open')) {
                    $(this).parent().removeClass('open').addClass('closed');
                    $(this).find('i.level').removeClass('fa-plus-minus-o').addClass('fa-plus-square-o');
                }
                else {
                    $(this).parent().removeClass('closed').addClass('open');
                    $(this).find('i.level').removeClass('fa-plus-square-o').addClass('fa-minus-square-o');
                }
                $(this).parent().children('ul.sub-level').toggle(150);
            });
            
            // prevent checkboxes from being deselected
            $('#hdm-feature-tree input[type="checkbox"]').on('click', function(e){
                e.preventDefault();
            });
            
        });
    }
    
    /*
     * Initialises the OSM feature tree.
     */
    function initOSMFeatureTree(tags){
        $.get(Config.OSM_TAGS_URL, function(data){
            var v = {'OSM Data Model': data}
            var level_idx = 0;
            var $tree = $('#osm-feature-tree ul.nav-list');
            if (typeof data == 'object') {
                traverse(v, $tree, level_idx);
            }
            
            /*
             * Recursively builds the feature tree.
             */
            function traverse(data, $level, level_idx){
                $.each(data, function(k,v){
                    if ($(v).attr('displayName')){
                        var name = $(v).attr('displayName');
                        var tag = $(v).attr('tag');
                        var key = tag.split(':')[0];
                        var val = tag.split(':')[1];
                        var geom = $(v).attr('geom');
                        geom_str = geom.join([separator=',']);
                        var $entry = $('<li class="entry"><label><i class="fa fa-square-o fa-fw"></i>' + name + '</label>' +
                                           '<div class="checkbox tree-checkbox"><input class="entry" type="checkbox" data-model="OSM" data-geom="' +
                                            geom_str + '" data-key="' + key + '" data-val="' + val +'" data-name="' + name + '" disabled/></div>' +
                                        '</li>');
                        $level.append($entry);
                    }
                    else {
                        var collapse = level_idx > 0 ? 'collapse' : '';
                        var state = level_idx == 0 ? 'open' : 'closed';
                        var icon = level_idx == 0 ? 'fa-minus-square-o' : 'fa-plus-square-o';
                        var root = level_idx == 0 ? 'root' : '';
                        var $nextLevel = $('<li class="level nav-header ' + state + ' ' + root + '"><label><i class="level fa ' + icon + ' fa-fw"></i>' + k + '</label>' + 
                                            '<div class="checkbox tree-checkbox"><input class="level" type="checkbox" disabled /></div>');
                        var $nextUL = $('<ul class="nav nav-list sub-level ' + collapse + '">');
                        $nextLevel.append($nextUL);
                        $level.append($nextLevel);
                        level_idx += 1;
                        traverse(v, $nextUL, level_idx);
                    }
                });
            }
            
            // toggle level collapse
            $('#osm-feature-tree li.level > label').bind('click', function(e){
                if ($(this).parent().hasClass('open')) {
                    $(this).parent().removeClass('open').addClass('closed');
                    $(this).find('i.level').removeClass('fa-plus-minus-o').addClass('fa-plus-square-o');
                }
                else {
                    $(this).parent().removeClass('closed').addClass('open');
                    $(this).find('i.level').removeClass('fa-plus-square-o').addClass('fa-minus-square-o');
                }
                $(this).parent().children('ul.sub-level').toggle(150);
            });
            
            $.each(tags, function(idx, tag){
                var key = tag.key;
                var val = tag.value;
                // check the corresponding input on the tree
                var $input = $('#osm-feature-tree').find('input[data-key="' + key + '"][data-val="' + val + '"]');
                $input.prop('checked', true);
                $input.prop('disabled', false);
                // check the parent levels
                $.each($input.parentsUntil('#osm-feature-tree', 'li.level'),
                       function(idx, level){
                    $(level).children('div.tree-checkbox').find('input.level').prop('checked', true);
                    $(level).children('div.tree-checkbox').find('input.level').prop('disabled', false);
                });
            });
            
            // prevent checkboxes from being deselected
            $('#osm-feature-tree input[type="checkbox"]').on('click', function(e){
                e.preventDefault();
            });
        });
    }
    
    /*
     * Loads preset details on fetaures modal.
     */
    function initPresetList(configurations){
        var $filelist = $('#filelist');
        if (configurations.length > 0) {
            var config = configurations[0];
            var published = config.published ? 'Published' : 'Private';
            var $tr = $('<tr id="' + config.uid + '" data-filename="' + config.filename + '"' +
                        'data-type="' + config.config_type + '" data-published="' + config.published + '"' +
                        'class="config"><td><i class="fa fa-file"></i>&nbsp;&nbsp;<span>' + config.filename + '</span></td>' +
                        '<td>' + config.config_type + '</td><td>' + published + '</td></tr>');
            $filelist.append($tr);
        }
    }
  
})();


$(document).ready(function() {
    // initialize the app..
    exports.detail.init();
});

