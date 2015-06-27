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

var vectors;

$(document).ready(function() {
        new JobApp();
});

var JobApp = OpenLayers.Class({
    
    initialize: function(){
        this.map = this.initMap();
        this.max_bounds_area = 100; // set this dynamically..
    },
    
    initMap: function() {
        var that = this;
        
        // set up the map
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
        
        // add base layers
        osm = Layers.OSM
        hotosm = Layers.HOT
        osm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        hotosm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayers([osm, hotosm]);
        
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
        var regions = new OpenLayers.Layer.Vector('regions', {
            displayInLayerSwitcher: false,
            style: {
                strokeWidth: 3.5,
                strokeColor: '#D73F3F',
                fillColor: 'transparent',
                fillOpacity: 0.8,
            }
        });
        
        var mask = new OpenLayers.Layer.Vector('mask', {
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
        
        /* add the regions and mask features */
        //this.buildJobList(jobs, selectControl);
        this.addRegionMask(mask);
        this.addRegions(regions);
        
        // add bounding box selection layer
        bbox = new OpenLayers.Layer.Vector("bbox", {
           displayInLayerSwitcher: false,
           styleMap: this.getTransformStyleMap(),
        });
        map.addLayers([bbox]);
        
        // add a draw feature control for bbox selection.
        box = new OpenLayers.Control.DrawFeature(bbox, OpenLayers.Handler.RegularPolygon, { 
           handlerOptions: {
              sides: 4,
              snapAngle: 90,
              irregular: true,
              persist: true
           }
        });
        map.addControl(box);
       
        transform = new OpenLayers.Control.TransformFeature(bbox, {
           rotate: false,
           irregular: true,
           renderIntent: "transform",
        });
        
        // listen for selection box being added to bbox layer..
        box.events.register('featureadded', this, function(e){
            // get selection bounds
            bounds = e.feature.geometry.bounds;
            
            // add feature based on selection
            bbox.removeAllFeatures(); 
            var feature = new OpenLayers.Feature.Vector(bounds.toGeometry());
            bbox.addFeatures(feature);
            transform.setFeature(feature);
            box.deactivate();
            
            // validate the selected extents.
            if (this.checkBounds(bounds)) {
                //all ok
                this.setBounds(bounds);
                $('#alert-area').css('visibility','hidden');
                $("#create-export-job :input").prop("disabled", false);
            }
            else {
                 $('#alert-area').css('visibility','visible');
                 $("#create-export-job :input").prop("disabled", true);
            }
        });
        
        // update the bounds when bbox is moved..
        transform.events.register("transformcomplete", this, function(e){
            var bounds = e.feature.geometry.bounds
            if (this.checkBounds(bounds)) {
                //all ok
                this.setBounds(bounds);
                $('#alert-area').css('visibility','hidden');
                $("#create-export-job :input").prop("disabled", false);
            }
            else {
                $('#alert-area').css('visibility','visible');
                $("#create-export-job :input").prop("disabled", true);
            }
            this.setBounds(bounds);
        });
        map.addControl(transform);
        
        // handles click on select area button
        $("#select-area").bind('click', function(e){
            /* clear existing features and activate draw control */
            bbox.removeAllFeatures();
            transform.unsetFeature();
            box.activate();
            $('#alert-area').css('visibility','hidden');
            $("#create-export-job :input").prop("disabled", false);
        });
        
        $('#clear-selection').bind('click', function(e){
            /*
             * remove features and transforms
             */
            bbox.removeAllFeatures();
            box.deactivate();
            transform.unsetFeature();
            $('#alert-area').css('visibility','hidden');
            $("#create-export-job :input").prop("disabled", false);
        });
        
        $('#reset-map').bind('click', function(e){
            /*
             * remove features and transforms
             * reset map to regions extent
             */
            bbox.removeAllFeatures();
            box.deactivate();
            transform.unsetFeature();
            map.zoomToExtent(regions.getDataExtent());
            $("#create-export-job :input").prop("disabled", false);
        });
        
        /* Add map controls */
        map.addControl(new OpenLayers.Control.ScaleLine());
        //map.addControl(new OpenLayers.Control.LayerSwitcher());
        
        // set inital zoom to regions extent
        map.zoomTo(regions.getDataExtent());
        
        return map;
    },
    
    buildJobList: function(jobs){
        var that = this;
        var selectControl = map.getControlsBy('id','selectControl')[0];
        $.getJSON(Config.JOBS_URL, function(data){
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
        $.getJSON(Config.REGIONS_URL, function(data){
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
        $.getJSON(Config.REGION_MASK_URL, function(data){
            var geojson = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
            });
            var features = geojson.read(data);
            mask.addFeatures(features);
        }); 
    },
    
    setBounds: function(bounds) {
     
        bounds.transform('EPSG:3857','EPSG:4326');
     
        z = 10000;
     
        var left    = Math.round(bounds.left   * z) / z;
        var bottom  = Math.round(bounds.bottom * z) / z;
        var right   = Math.round(bounds.right  * z) / z;
        var top     = Math.round(bounds.top    * z) / z;
     
        $("#job_lonmin").val(left);
        $("#job_latmin").val(bottom);
        $("#job_lonmax").val(right);
        $("#job_latmax").val(top);
        //$("form").resetClientSideValidations();
    },
    
    initValues2Box: function() {
    
       /*<% unless @job.id.nil? %>"
       xminlon = <%= @job.lonmin %>;
       xminlat = <%= @job.latmin %>;
       xmaxlon = <%= @job.lonmax %>;
       xmaxlat = <%= @job.latmax %>;*/
    
       bounds = new OpenLayers.Bounds(xminlon, xminlat, xmaxlon, xmaxlat);
       bounds.transform(proj4326,projmerc);
       draw_box(bounds);
       /*<% end %>*/
    },
    
    values2Box: function() {

        xminlon = $("#job_lonmin").val(); 
        xminlat = $("#job_latmin").val();
        xmaxlon = $("#job_lonmax").val();
        xmaxlat = $("#job_latmax").val();
     
        bounds = new OpenLayers.Bounds(xminlon, xminlat, xmaxlon, xmaxlat);
        bo//unds.transform(proj4326,projmerc);
        //this.drawBox(bounds);
        //$("form").resetClientSideValidations();
    },
    
    checkBounds: function(bounds) {
        var extent = bounds.toGeometry();
        var regions = map.getLayersByName('regions')[0].features
        var valid_region = false;
        for (i=0; i < regions.length; i++){
            region = regions[i].geometry;
            if (extent.intersects(region)){
                valid_region = true;
            }
        }
        // need a check here if user is_admin.. 
        //var max_bounds_area = "<%= @max_bounds_area.to_s %>";
        var area = bounds.transform('EPSG:3857', 'EPSG:4326').toGeometry().getArea();
        //bounds.transform(proj4326,projmerc);
     
        $("a.select_area").text("<%=t('jobs.area.select_different') %>");
        
        if (!valid_region) {
           //Area is out of the covered regions
           $('#alert-area').html('<strong>Error!</strong> Selected area is outside a valid HOT Export Region.')
           return false;
        } else if (area > this.max_bounds_area) {
           //Area is too large
           $('#alert-area').html('<strong>Error!</strong> Selected area is ' + area.toFixed(2) + '. Must be less than 100.');
           return false;
        } else {
           //All ok
           return true;
        }
    },
    
    updateMapMessage: function(msg) {
        mapMessage = msg
        $("#mapmessage").html(mapMessage);
    },
    
    /* returns the style map for the selection bounding box */
    getTransformStyleMap: function(){
        return new OpenLayers.StyleMap({
                    "default": new OpenLayers.Style({
                        fillColor: "blue",
                        fillOpacity: 0.05,
                        strokeColor: "blue"
                    }),
                    // a nice style for the transformation box
                    "transform": new OpenLayers.Style({
                        display: "${getDisplay}",
                        cursor: "${role}",
                        pointRadius: 6,
                        fillColor: "blue",
                        fillOpacity: 1,
                        strokeColor: "blue",
                        //strokeDashstyle: "dash",
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
    
    /*
    $("form#new_job").submit(function() {
        //Extra validation, in addition to the standard stuff from the
        //validation plugin.
        if (mapMessage!="" && mapMessage!="&nbsp;") {   		   
           alert( mapMessage );
           return false
        } else {
           return true;
        }
    });
    */
    
    
});
