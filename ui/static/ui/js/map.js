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

$(document).ready(function() {
        new JobApp();
});

var JobApp = OpenLayers.Class({
    
    initialize: function(){
        this.map = this.initMap();
    },
    
    initMap: function() {
        
        maxExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");
        var mapOptions = {
                displayProjection: new OpenLayers.Projection("EPSG:4326"),
                controls: [new OpenLayers.Control.Attribution(),
                           new OpenLayers.Control.ScaleLine()],
                maxExtent: maxExtent,          
                scales:[500000,350000,250000,100000,25000,20000,15000,10000,5000,2500,1250],   
                units: 'm',
                sphericalMercator: true,
                noWrap: true
        }

        map = new OpenLayers.Map('map', {options: mapOptions});
        map.restrictedExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");
        
        osm = Layers.OSM
        hotosm = Layers.HOT
        osm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        hotosm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayers([osm, hotosm]);
        
        /* Styles */
        var defaultStyle = new OpenLayers.Style({
            strokeColor: "#db337b",
            strokeWidth: 2.5,
            strokeDashstyle: "dash"
        });
        
        var selectStyle = new OpenLayers.Style({
            strokeColor: "#6B9430",
            strokeWidth: 3.5,
            strokeDashstyle: "dash",
            label: '${name}',
            labelAlign: "lm",
            labelXOffset: "20",
            labelOutlineColor: "white",
            labelOutlineWidth: 3,
            fontSize: 16,
            graphicZIndex: 10,
        });
        
        var lineStyles = new OpenLayers.StyleMap(
        {
                "default": defaultStyle,
                "select": selectStyle
        });
        
        var regionStyle = new OpenLayers.Style({
            strokeColor: "#D73F3F",
            strokeWidth: 3.5,
            strokeDashstyle: "dash",
            fill: false
        });
        
        /* Add the Jobs */
        var jobs = new OpenLayers.Layer.Vector('Export Jobs', {
             style: {
                strokeWidth: .5,
                strokeColor: 'blue',
                fillColor: 'blue',
                fillOpacity: 0.4,
            }
        });
        /* Add the Regions */
        var regions = new OpenLayers.Layer.Vector('HOT Export Regions', {
            style: {
                strokeWidth: 3.5,
                strokeColor: '#D73F3F',
                fillColor: 'transparent',
                fillOpacity: 0.8,
            }
        });
        
        var mask = new OpenLayers.Layer.Vector('Mask', {
            displayInLayerSwitcher: false,
            styleMap: new OpenLayers.StyleMap({
                "default": new OpenLayers.Style({
                fillColor: "#fff",
                fillOpacity: 0.7,
                strokeColor: "#fff",
                strokeWidth: .1,
                strokeOpacity: 0.2,
                })
            }),
        });
        map.addLayers([mask, jobs, regions]);
        
        /* required to fire selection events on jobs layer */
        
        var selectControl = new OpenLayers.Control.SelectFeature(jobs,{
            id: 'selectControl'
        });
        map.addControl(selectControl);
        selectControl.activate();
        
        
        //this.buildJobList(jobs, selectControl);
        this.addRegionMask(mask);
        this.addRegions(regions);
        
        /* feature selection event handling */
        jobs.events.register("featureselected", this, function(e) {
                var feature = e.feature;
                var uid = feature.uid;
                var feat = feature.clone();
                var attrs = feat.attributes;
                var geom = feat.geometry.transform('EPSG:3857','EPSG:4326');
                map.zoomToExtent(feature.geometry.bounds, false);
                
        });
        
        /* feature unselection event handling */
        jobs.events.register("featureunselected", this, function(e){
            
        });
        
        $('#reset-map').bind('click', function(e){
             map.zoomToExtent(routes.getDataExtent());
        });
        
        /* Add map controls */
        map.addControl(new OpenLayers.Control.ScaleLine());
        map.addControl(new OpenLayers.Control.LayerSwitcher());
        
        map.zoomTo(2);
        
        return map;
    },
    
    buildJobList: function(jobs){
        var that = this;
        var selectControl = map.getControlsBy('id','selectControl')[0];
        // get the routes from the tracks api and build the page..
        $.getJSON('http://hot.geoweb.io/api/jobs.json', function(data){
            var geojson = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
            });
            $.each(data, function(i, job){
                var bbox = geojson.read(data[i].bbox);
                jobs.addFeatures(bbox);
                // add jobs info to dom here..
            });
        });
    },
    
    addRegions: function(regions){
       var that = this;
        // get the regions from the regions api
        $.getJSON('http://hot.geoweb.io/api/regions.json', function(data){
            var geojson = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
            });
            var features = geojson.read(data);
            regions.addFeatures(features);
            map.zoomToExtent(regions.getDataExtent());
        }); 
    },
    
    addRegionMask: function(mask){
        // get the regions from the regions api
        $.getJSON('http://hot.geoweb.io/api/maskregions.json', function(data){
            var geojson = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
            });
            var features = geojson.read(data);
            mask.addFeatures(features);
        }); 
    },
    
    
    buildDeleteDialog: function(){
        var that = this;
        var options = {
            dataType: 'json',
            beforeSubmit: function(arr, $form, options) {
                console.log('in before submit..');
            },
            success: function(data, status, xhr) {
                console.log(status);
                if (status == 'nocontent') {
                    routes = map.getLayersByName('Routes')[0]
                    routes.destroyFeatures();
                    that.buildRouteList(routes);
                } 
            },
            error: function(xhr, status, error){
                var json = xhr.responseJSON
                errors = json.errors;
                console.log(errors);
            },
        }
        
        var modalOpts = {
            keyboard: true,
            backdrop: 'static',
        }
        
        $("#btnDelete").click(function(){
            $("#deleteRouteModal").modal(modalOpts, 'show');
        });
        
        $("#deleteConfirm").click(function(){
            $('#deleteForm').ajaxSubmit(options);
            $("#deleteRouteModal").modal('hide');
        });
        
    }
    
});
