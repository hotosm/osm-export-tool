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
     *
     * Parameters:
     * job_uid {String} - The uid of the job to load
     */
    function loadJobDetail(job_uid){
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
    }
  
    /**
      * Loads the job details.
      *
      * Parameters:
      * job_uid {String} - The uid of the job
      */
    function loadRunDetails(job_uid){
        $.getJSON(Config.RUNS_URL + '?job_uid=' + job_uid, function(data){
            for (i = 0; i < data.length; i++){
                var run = data[i];
                $('#ruid').html(run.uid);
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
        }); 
      
    }
    
    /**
      * Builds task html
      *
      * Parameters:
      * tasks {Object} - the tasks to build.
      */
    function buildTaskElements(tasks){
        for (j = 0; j < tasks; j++){
                    
        }
    }
  
    return {
        init: function(){
            parts = window.location.href.split('/');
            job_uid = parts[parts.length -2];
            initMap();
            loadJobDetail(job_uid);
            loadRunDetails(job_uid);
        },
    }
    
})();


$(document).ready(function() {
    // initialize the app..
    exports.detail.init();
});

