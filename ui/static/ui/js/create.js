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
        // construct the UI app
        new JobApp();
});

/*
 * Application to handle Export Job Creation.
 */
var JobApp = OpenLayers.Class({
    
    initialize: function(){
        // initialize the map and set the max extent.
        this.map = this.initMap();
        this.max_bounds_area = 2500000; // sq km // set this dynamically..
    },
    
    /*
     * Initialize the map
     * and the UI controls.
     */
    initMap: function() {
        var that = this;
        
        // set up the map and add the required layers
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
        
        // add the regions layer
        var regions = new OpenLayers.Layer.Vector('regions', {
            displayInLayerSwitcher: false,
            style: {
                strokeWidth: 3.5,
                strokeColor: '#D73F3F',
                fillColor: 'transparent',
                fillOpacity: 0.8,
            }
        });
        
        // add the region mask layer
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
        map.addLayers([regions, mask]);
        
        // add region and mask features
        this.addRegionMask(mask);
        this.addRegions(regions);
        
        // add export format checkboxes
        this.buildExportFormats();
        
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
       
       
        // add a transform control to enable modifications to bounding box (drag, resize)
        transform = new OpenLayers.Control.TransformFeature(bbox, {
           rotate: false,
           irregular: true,
           renderIntent: "transform",
        });
        
        // listen for selection box being added to bbox layer
        box.events.register('featureadded', this, function(e){
            // get selection bounds
            bounds = e.feature.geometry.bounds;
            
            // clear existing features
            bbox.removeAllFeatures();
            box.deactivate();
            
            // add a bbox feature based on user selection
            var feature = new OpenLayers.Feature.Vector(bounds.toGeometry());
            bbox.addFeatures(feature);
            
            // enable bbox modification
            transform.setFeature(feature);
            
            // validate the selected extents
            if (this.validateBounds(bounds)) {
                this.setBounds(bounds);
            }
            else {
                this.unsetBounds();
            }
        });
        
        // update the bounds when bbox is moved / modified
        transform.events.register("transformcomplete", this, function(e){
            var bounds = e.feature.geometry.bounds.clone();
            if (this.validateBounds(bounds)) {
                this.setBounds(bounds);
            }
            else {
                this.unsetBounds();
            }
        });
        
        // update bounds during bbox modification
        transform.events.register("transform", this, function(e){
            var bounds = e.object.feature.geometry.bounds.clone();
            if (this.validateBounds(bounds)) {
                this.setBounds(bounds);
            }
            else {
                this.unsetBounds();
            }
        });
        // add the transform control
        map.addControl(transform);
        
        // handles click on select area button
        $("#select-area").bind('click', function(e){
            /*
             * unset bounds on form,
             * clear transform control
             * activate the draw bbox control
             */
            that.unsetBounds();
            bbox.removeAllFeatures();
            transform.unsetFeature();
            box.activate();
            that.validateBounds();
        });
        
        $('#zoom-selection').bind('click', function(e){
            // zoom to the selected extent
            if (bbox.features.length > 0) {
                map.zoomToExtent(bbox.getDataExtent(), false);
            }
        });
        
        $('#clear-selection').bind('click', function(e){
            /*
             * Unsets the bounds on the form and
             * remove features and transforms
             */
            bbox.removeAllFeatures();
            box.deactivate();
            transform.unsetFeature();
            that.unsetBounds();
            that.validateBounds();
        });
        
        $('#reset-map').bind('click', function(e){
            /*
             * Unsets the bounds on the form
             * remove features and transforms
             * reset map to regions extent
             */
            that.unsetBounds();
            bbox.removeAllFeatures();
            box.deactivate();
            transform.unsetFeature();
            map.zoomToExtent(regions.getDataExtent());
            that.validateBounds();
        });
        
        /* Add map controls */
        map.addControl(new OpenLayers.Control.ScaleLine());
        //map.addControl(new OpenLayers.Control.LayerSwitcher());
        
        // set inital zoom to regions extent
        map.zoomTo(regions.getDataExtent());
        
        return map;
    },
    
    /*
     * Initialize the form validation.
     */
    initForm: function(){
        
        $('#create-job-form').formValidation({
            framework: 'bootstrap',
            // Feedback icons
            icon: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            live: 'enabled',
    
            // List of fields and their validation rules
            fields: {
                'name': {
                    validators: {
                        notEmpty: {
                            message: 'The export job name is required and cannot be empty.'
                        },
                    }
                },
                'description': {
                    validators: {
                        notEmpty: {
                            message: 'The description is required and cannot be empty.'
                        }
                    }
                },
                'formats': {
                    validators: {
                        choice: {
                            min: 1,
                            max: 5,
                            message: 'At least one export format must be selected.'
                        }
                    }
                },
                'xmin':{
                    validators: {
                        notEmpty: {
                            message: 'not empty'
                        }
                    }
                },
                'ymin':{
                    validators: {
                        notEmpty: {
                            message: 'not empty'
                        }
                    }
                },
                'xmax':{
                    validators: {
                        notEmpty: {
                            message: 'not empty'
                        }
                    }
                },
                'ymax':{
                    validators: {
                        notEmpty: {
                            message: 'not empty'
                        }
                    }
                }
            }
        })/*
        .on('err.field.fv', function(e, data) {
            // handle validation on bounding box fields
            if (data.field == 'xmin' || data.field == 'ymin'
                || data.field == 'xmax' || data.field == 'ymax') {
                $('#alert-extents').css('visibility','visible');
                $('#alert-extents').html('<strong>Invalid Extent!</strong><br/>You must select an area to export.')
            }
        })
        */
        .on('success.form.fv', function(e) {
            e.preventDefault(); // prevent form submission
            $('#alert-extents').css('visibility','hidden');
        });
    },
    
    /*
     * Add the regions to the map.
     */
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
    
    /*
     * Add the region mask to the map.
     */
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
    
    /*
     * build the export format checkboxes.
     */
    buildExportFormats: function(){
        var that = this;
        var formatsDiv = $('#supported-formats');
        $.getJSON(Config.EXPORT_FORMATS_URL, function(data){
            for (i = 0; i < data.length; i++){
                format = data[i];
                formatsDiv.append('<div class="checkbox"><label>'
                                 + '<input type="checkbox"'
                                 + 'name="formats"'
                                 + 'value="' + format.slug + '"/>'
                                 + format.description
                                 + '</label></div>');
            }
            /*
             * only initialize form validation when
             * all form elements have been loaded.
             */
            that.initForm();
        }); 
    },
    
    /*
     * update the bbox extents on the form.
     */
    setBounds: function(bounds) {
        fmt = '0.0000000000' // format to 10 decimal places
        // fire input event here to make sure fields validate..
        var xmin = numeral(bounds.left).format(fmt);
        var ymin = numeral(bounds.bottom).format(fmt);
        var xmax = numeral(bounds.right).format(fmt);
        var ymax = numeral(bounds.top).format(fmt);
        $('#xmin').val(xmin).trigger('input');
        $('#ymin').val(ymin).trigger('input');
        $('#xmax').val(xmax).trigger('input');
        $('#ymax').val(ymax).trigger('input');
    },
    
    /*
     * clear extents from the form.
     */
    unsetBounds: function(){
        // fire input event here to make sure fields validate..
        $('#xmin').val('').trigger('input');
        $('#ymin').val('').trigger('input');
        $('#xmax').val('').trigger('input');
        $('#ymax').val('').trigger('input');
    },
    
    /*
     * triggers validation of the extents.
     */
    validateBBox: function(){
        $('#create-job-form').data('formValidation').validateContainer('#form-group-bbox');
    },
    
    /*
     * Validate the selected export extent.
     */
    validateBounds: function(bounds) {
        var that = this;
        if (!bounds) {
            that.validateBBox();
            $('#valid-extents').css('visibility','hidden');
            $('#alert-extents').css('visibility','visible');
            $('#alert-extents').html('<strong>Invalid Exent.</strong><br/>Select and area to export.');
            return false;
        }
        var extent = bounds.toGeometry();
        var regions = map.getLayersByName('regions')[0].features
        var valid_region = false;
        // check that we're within a HOT region.
        for (i = 0; i < regions.length; i++){
            region = regions[i].geometry;
            if (extent.intersects(region)){
                valid_region = true;
            }
        }
         
        var area = bounds.transform('EPSG:3857', 'EPSG:4326').toGeometry().getGeodesicArea() / 1000000; // sq km
        
        var area_str = numeral(area).format('0,0');
        var max_bounds_str = numeral(this.max_bounds_area).format('0,0');
        
        if (!valid_region) {
           // invalid region
           that.validateBBox(); // trigger validation on extents
           $('#valid-extents').css('visibility','hidden');
           $('#alert-extents').css('visibility','visible');
           $('#alert-extents').html('<strong>Invalid Extent!</strong><br/>Selected area is outside a valid HOT Export Region.')
           return false;
        } else if (area > this.max_bounds_area) {
           // are too large
           that.validateBBox(); // trigger validation on extents
           $('#valid-extents').css('visibility','hidden');
           $('#alert-extents').css('visibility','visible');
           $('#alert-extents').html('<strong>Invalid Exent!</strong><br/>Selected area is ' + area_str
                                 + ' sq km.<br/> Must be less than ' + max_bounds_str + ' sq km.');
           return false;
        } else {
            $('#alert-extents').css('visibility','hidden');
            $('#valid-extents').css('visibility','visible');
            $('#valid-extents').html('<span>Extents are valid.&nbsp;&nbsp;</span><span class="glyphicon glyphicon-ok">&nbsp;</span>');
            return true;
        }
    },

    /*
     * get the style map for the selection bounding box.
     */
    getTransformStyleMap: function(){
        return new OpenLayers.StyleMap({
                    "default": new OpenLayers.Style({
                        fillColor: "blue",
                        fillOpacity: 0.05,
                        strokeColor: "blue"
                    }),
                    // style for the transformation box
                    "transform": new OpenLayers.Style({
                        display: "${getDisplay}",
                        cursor: "${role}",
                        pointRadius: 6,
                        fillColor: "blue",
                        fillOpacity: 1,
                        strokeColor: "blue",
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
    
});
