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
    
    var job_uid;
    
    return {
        init: function(){
            parts = window.location.href.split('/');
            job_uid = parts[parts.length -2];
            exports.detail.job_uid = job_uid;
            initMap();
            loadJobDetail();
            loadCompletedRunDetails();
            loadSubmittedRunDetails();
            //startRunCheckInterval();
            
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
                fillColor: 'transparent',
                fillOpacity: 0.8,
            }
        });
        
        map.addLayer(job_extents);
        return map;
    }
  
    /**
     * Loads the job details.
     */
    function loadJobDetail(){
        var job_uid = exports.detail.job_uid;
        $.getJSON(Config.JOBS_URL + '/' + job_uid, function(data){
            $('#uid').html(data.uid);
            $('#name').html(data.name);
            $('#description').html(data.description);
            var created = moment(data.created_at).format('h:mm:ss a, MMMM Do YYYY');
            $('#created').html(created);
            var formats = data.exports;
            for (i = 0; i < formats.length; i++){
                $('#formats').append(formats[i].name + '<br/>');
            }
            var extent = data.extent;
            var geojson = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
            });
            var feature = geojson.read(extent);
            job_extents.addFeatures(feature);
            map.zoomToExtent(job_extents.getDataExtent());
        });
        
        // handle re-run click events..
        $('button#rerun').bind('click', function(e){
           $.get(Config.RERUN_URL + exports.detail.job_uid,
                function(data, textStatus, jqXhr){
                    // initialize the submitted run panel immediately
                    initSumtittedRunPanel([data]);
                    // then start the check interval..
                    startRunCheckInterval();
                });
        });
    }
    
    /**
      * Loads the job details.
      * This occurs initially on page load..
      */
    function loadSubmittedRunDetails(){
        var job_uid = exports.detail.job_uid;
        $.getJSON(Config.RUNS_URL + '?status=SUBMITTED&job_uid=' + job_uid, function(data){
            if (data.length > 0) {
                initSumtittedRunPanel(data);
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
                $('button#rerun').prop('disabled', 'true');
                startRunCheckInterval();
        }
        else {
            // stop the interval timer..
            clearInterval(exports.detail.timer);
            // hide the submitted run div
            $('#submitted_runs').css('display', 'none');
            // reload the complted runs to show the latest run..
            loadCompletedRunDetails();
            // enable the re-run button..
            $('button#rerun').prop('disabled', '');
        }
        $.each(data, function(index, run){
            var started = moment(run.started_at).format('h:mm:ss a, MMMM Do YYYY');
            var finished = moment(run.finished_at).format('h:mm:ss a, MMMM Do YYYY');
            var duration = moment.duration(run.duration).humanize();
            var status_class = '';
            if (run.status === 'SUBMITTED') {
                status_class = 'alert alert-info';
            }
            else {
                status_class = 'alert alert-warning'
            }
            var expanded = index == 0 ? 'in' : ''; // collapse all for now..
            var context = { 'run_uid': run.uid, 'status': run.status,
                            'started': started, 'finished': finished,
                            'duration': duration,'status_class': status_class,
                            'expanded': expanded};
            var template = getRunTemplate();
            var html = template(context);
            $runPanel.append(html);
        });
    }
    
    /**
     * Updates the submitted run details
     */
    function updateSubmittedRunDetails(){
        var job_uid = exports.detail.job_uid;
        $.getJSON(Config.RUNS_URL + '?status=SUBMITTED&job_uid=' + job_uid,
                  function(data){
            if (data.length > 0) {
                console.log('update submitted panel..');
            }
            else {
                // stop the interval timer..
                clearInterval(exports.detail.timer);
                // hide the submitted run div
                $('#submitted_runs').css('display', 'none');
                // reload the complted runs to show the latest run..
                loadCompletedRunDetails();
                // enable the re-run button..
                $('button#rerun').prop('disabled', '');
            }
        }); 
    }
  
    /**
      * Loads the completed run details.
      *
      */
    function loadCompletedRunDetails(){
        var job_uid = exports.detail.job_uid;
        var $runPanel = $('#completed_runs > .panel-group');
        $runPanel.empty();
        $.getJSON(Config.RUNS_URL + '?status=COMPLETED&job_uid=' + job_uid, function(data){
            $.each(data, function(index, run){
                var started = moment(run.started_at).format('h:mm:ss a, MMMM Do YYYY');
                var finished = moment(run.finished_at).format('h:mm:ss a, MMMM Do YYYY');
                var duration = moment.duration(run.duration).humanize();
                var status_class = '';
                if (run.status === 'COMPLETED') {
                    status_class = 'alert alert-success';
                }
                else {
                    status_class = 'alert alert-info'
                }
                var expanded = index == 0 ? '' : ''; // collapse all for now..
                var context = { 'run_uid': run.uid, 'status': run.status,
                                'started': started, 'finished': finished,
                                'duration': duration,'status_class': status_class,
                                'expanded': expanded};
                var template = getRunTemplate();
                var html = template(context);
                $runPanel.append(html);
            });
            /*
            for (i = 0; i < data.length; i++){
                if (run.status == 'COMPLETED') {
                    $('#status').html('<div class="alert alert-success" role="alert">'+run.status+'</div>');
                }
                if (run.status == 'SUBMITTED') {
                    $('#status').html('<div class="alert alert-info" role="alert">'+run.status+'</div>');
                }
                var started = moment(run.started_at).format('h:mm:ss a, MMMM Do YYYY');
                var finished = moment(run.finished_at).format('h:mm:ss a, MMMM Do YYYY');
                var duration = moment.duration(run.duration).humanize();
                $('#started').html(started);
                $('#finished').html(finished);
                $('#duration').html(duration);
                //buildTaskElements(run.tasks);
                var tasks = run.tasks;
                for (j = 0; j < tasks.length; j++){
                    var result = tasks[j].result;
                    var status = tasks[j].status;
                    if (status == 'SUCCESS') {
                        $('#downloads').append('<a href="' + result.url + '">' + result.filename +'</a> (' + result.size + ')<br/>');//code
                    }
                    else if (status == 'RUNNING') {
                        $('#downloads').append('<span>' + tasks[j].name + ' is running...</span><br/>');
                    }
                }
            }
            */
        }); 
      
    }
    
    /**
     * Gets a template for displaying run details.
     */
    function getRunTemplate(context) {
        var html = $('  <div class="panel panel-default"> \
                            <div class="panel-heading" role="tab"> \
                                <h4 class="panel-title"> \
                                    <a role="button" data-toggle="collapse" data-parent="#runs" href="#{{ run_uid }}" \
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
      * Builds task html
      *
      * Parameters:
      * tasks {Object} - the tasks to buil
      */
    function buildTaskElements(tasks){
        for (j = 0; j < tasks; j++){
                    
        }
    }
    
    function startRunCheckInterval(){
        var job_uid = exports.detail.job_uid;
        timer = setInterval(function(){
            updateSubmittedRunDetails();
        }, 3000);
        exports.detail.timer = timer;
    }
  
    
})();


$(document).ready(function() {
    // initialize the app..
    exports.detail.init();
});

