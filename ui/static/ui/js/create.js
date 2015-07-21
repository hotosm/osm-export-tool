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


create = {};
create.job = (function(){
    var map;
    var regions;
    var mask;
    var transform;
    var max_bounds_area = 2500000; // sq km // set this dynamically..
    
    return {
        init: function(){
            initCreateMap();
            initSelectFeaturesTree();
            initNominatim();
        }
    }
    
    /*
     * Initialize the map
     * and the UI controls.
     */
    function initCreateMap() {
        // set up the map and add the required layers
        var maxExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");
        var mapOptions = {
                displayProjection: new OpenLayers.Projection("EPSG:4326"),
                controls: [new OpenLayers.Control.Attribution(),
                           new OpenLayers.Control.ScaleLine()],
                maxExtent: maxExtent,          
                scales:[500000,350000,250000,100000,25000,20000,15000,10000,5000,2500,1250],   
                units: 'm',
                sphericalMercator: true,
                noWrap: true, // don't wrap world extents  
        }
        map = new OpenLayers.Map('create-export-map', {options: mapOptions});
        
        // restrict extent to world bounds to prevent panning..
        map.restrictedExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");
        
        // add base layers
        var osm = new OpenLayers.Layer.OSM("OpenStreetMap");
        var hotosm = Layers.HOT
        osm.options = {
            //layers: "basic",
            isBaseLayer: true,
            visibility: true,
            displayInLayerSwitcher: true,
        };
        osm.attribution = "&copy; <a href='//www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors<br/>Nominatim Search Courtesy of <a href='http://www.mapquest.com/' target='_blank'>MapQuest</a> <img src='http://developer.mapquest.com/content/osm/mq_logo.png'>";
        hotosm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayers([osm]);
        
        // add the regions layer
        regions = new OpenLayers.Layer.Vector('regions', {
            displayInLayerSwitcher: false,
            style: {
                strokeWidth: 3.5,
                strokeColor: '#D73F3F',
                fillColor: 'transparent',
                fillOpacity: 0.8,
            }
        });
        
        // add the region mask layer
        mask = new OpenLayers.Layer.Vector('mask', {
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
        addRegionMask();
        addRegions();
        
        // add export format checkboxes
        buildExportFormats();
        
        // add bounding box selection layer
        bbox = new OpenLayers.Layer.Vector("bbox", {
           displayInLayerSwitcher: false,
           styleMap: getTransformStyleMap(),
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
            if (validateBounds(bounds)) {
                setBounds(bounds);
            }
            else {
                unsetBounds();
            }
        });
        
        // update the bounds after bbox is moved / modified
        transform.events.register("transformcomplete", this, function(e){
            var bounds = e.feature.geometry.bounds.clone();
            if (validateBounds(bounds)) {
                setBounds(bounds);
            }
            else {
                unsetBounds();
            }
        });
        
        // update bounds during bbox modification
        transform.events.register("transform", this, function(e){
            var bounds = e.object.feature.geometry.bounds.clone();
            if (validateBounds(bounds)) {
                setBounds(bounds);
            }
            else {
                unsetBounds();
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
            $('#nominatim').val('');
            unsetBounds();
            bbox.removeAllFeatures();
            map.zoomToExtent(regions.getDataExtent());
            transform.unsetFeature();
            box.activate();
            validateBounds();
        });
        
        $('#zoom-selection').bind('click', function(e){
            // zoom to the bounding box extent
            if (bbox.features.length > 0) {
                map.zoomToExtent(bbox.getDataExtent(), false);
            }
        });
        
        $('#reset-map').bind('click', function(e){
            /*
             * Unsets the bounds on the form
             * remove features and transforms
             * reset map to regions extent
             */
            $('#nominatim').val('');
            unsetBounds();
            bbox.removeAllFeatures();
            box.deactivate();
            transform.unsetFeature();
            map.zoomToExtent(regions.getDataExtent());
            validateBounds();
        });
        
        /* Add map controls */
        map.addControl(new OpenLayers.Control.ScaleLine());
        //map.addControl(new OpenLayers.Control.LayerSwitcher());
        
        // set inital zoom to regions extent
        map.zoomTo(regions.getDataExtent());
    }
    
    /*
     * Add the regions to the map.
     * Calls into region api.
     */
    function addRegions(){
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
    }
    
    /*
     * Add the region mask to the map.
     * Calls into region mask api.
     */
    function addRegionMask(){
        // get the regions from the regions api
        $.getJSON(Config.REGION_MASK_URL, function(data){
            var geojson = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
            });
            var features = geojson.read(data);
            mask.addFeatures(features);
        }); 
    }
    
    /*
     * build the export format checkboxes.
     */
    function buildExportFormats(){
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
            initForm();
        }); 
    }
    
    /*
     * update the bbox extents on the form.
     */
    function setBounds(bounds) {
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
    }
    
    /*
     * clear extents from the form.
     */
    function unsetBounds(){
        // fire input event here to make sure fields validate..
        $('#xmin').val('').trigger('input');
        $('#ymin').val('').trigger('input');
        $('#xmax').val('').trigger('input');
        $('#ymax').val('').trigger('input');
    }
    
    /*
     * triggers validation of the extents on the form.
     */
    function validateBBox(){
        $('#create-job-form').data('formValidation').validateContainer('#form-group-bbox');
    }
    
    /*
     * Validate the export extent.
     * Display error message in case of validation error.
     * Display success message when extents are valid. 
     */
    function validateBounds(bounds) {
        if (!bounds) {
            // no extents selected..
            validateBBox(); // trigger form validation.
            $('#valid-extents').css('visibility','hidden');
            $('#alert-extents').css('visibility','visible');
            $('#alert-extents').html('<span>Select area to export.&nbsp;&nbsp;</span><span class="glyphicon glyphicon-remove">&nbsp;</span>');
            return false;
        }
        var extent = bounds.toGeometry();
        var regions = map.getLayersByName('regions')[0].features;
        var valid_region = false;
        // check that we're within a HOT region.
        for (i = 0; i < regions.length; i++){
            region = regions[i].geometry;
            if (extent.intersects(region)){
                valid_region = true;
            }
        }
        /*
         * calculate the extent area and convert to sq kilometers
         * converts to lat long which will be proj set on form if extents are valid.
         */
        var area = bounds.transform('EPSG:3857', 'EPSG:4326').toGeometry().getGeodesicArea() / 1000000; // sq km
        // format the area and max bounds for display..
        var area_str = numeral(area).format('0,0');
        var max_bounds_str = numeral(max_bounds_area).format('0,0');
        
        if (!valid_region) {
           // invalid region
           validateBBox(); // trigger validation on extents
           $('#valid-extents').css('visibility','hidden');
           $('#alert-extents').css('visibility','visible');
           $('#alert-extents').html('<strong>Invalid Extent.</strong><br/>Selected area is outside <br/>a valid HOT Export Region.')
           return false;
        } else if (area > max_bounds_area) {
           // area too large
           validateBBox(); // trigger validation on extents
           $('#valid-extents').css('visibility','hidden');
           $('#alert-extents').css('visibility','visible');
           $('#alert-extents').html('<strong>Invalid Exent.</strong><br/>Selected area is ' + area_str
                                 + ' sq km.<br/> Must be less than ' + max_bounds_str + ' sq km.');
           return false;
        } else {
            // extents are valid so display success message..
            $('#alert-extents').css('visibility','hidden');
            $('#valid-extents').css('visibility','visible');
            $('#valid-extents').html('<span class="glyphicon glyphicon-ok"></span>');
            return true;
        }
    }
    
    /*
     * get the style map for the selection bounding box.
     */
    function getTransformStyleMap(){
        return new OpenLayers.StyleMap({
                    "default": new OpenLayers.Style({
                        fillColor: "blue",
                        fillOpacity: 0.05,
                        strokeColor: "blue"
                    }),
                    // style for the select extents box
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
    
    /*
     * Initialize the form validation.
     */
    function initForm(){
        $('#create-job-form').formValidation({
            framework: 'bootstrap',
            // Feedback icons
            icon: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            excluded: ':disabled',
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
                'event': {
                    validators: {
                        notEmpty: {
                            message: 'The event is required and cannot be empty.'
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
        })
        .on('success.form.fv', function(e){
            e.preventDefault();
            console.log(e);
            /*
             * Enable the submit button, but prevent automatic form submission
             * on successful validation as this is done by ajax call
             * when the submit button is clicked.
             */
            $('#btn-submit-job').prop('disabled', 'false');
        })
        .on('success.field.fv', function(e) {
            //$('#btn-submit-job').prop('disabled', 'true');
        });
        
        
        $('#create-job-wizard').bootstrapWizard({
            tabClass: 'nav nav-pills',
            onTabClick: function(tab, navigation, index){
                //return validateTab(index); temp
            }
        });
        
        function validateTab(index) {
            var fv = $('#create-job-form').data('formValidation'), // FormValidation instance
                // The current tab
                $tab = $('#create-job-form').find('.tab-pane').eq(index),
                $bbox = $('#bbox');
                
            // validate the form first
            fv.validate();
            var isFormValid = fv.isValid();
            if (!isFormValid) {
                // disable submit button unless form is valid
                $('#btn-submit-job').prop('disabled', 'true');
            }
    
            // validate the bounding box extents
            fv.validateContainer($bbox);
            var isValidBBox = fv.isValidContainer($bbox);
            if (isValidBBox === false || isValidBBox === null) {
                validateBounds(bbox.getDataExtent());
            }
            
            // validate the form panel contents
            fv.validateContainer($tab);
            var isValidStep = fv.isValidContainer($tab);
            if ((isValidStep === false || isValidStep === null) ||
                (isValidBBox === false || isValidBBox === null)) {
                // stay on this tab
                return false;
            }
            return true;
        }
        
         // handle form submission
        $('#create-job-form').submit(function(e){
            // check that the form is valid..
            var $form = $('#create-job-form'),
                fv = $($form).data('formValidation'),
                $bbox = $('#bbox');
            // validate the bounding box
            fv.validateContainer($bbox);
            var isValidBBox = fv.isValidContainer($bbox);
            if (isValidBBox === false || isValidBBox === null) {
                validateBounds(bbox.getDataExtent());
            }
            fv.validate();
            var fvIsValidForm = fv.isValid();
            if (!fvIsValidForm) {
                e.preventDefault();
            }
            /*
            if (fv.$invalidFields.length > 0) {
                e.preventDefault();
            }
            */
            else {
                $.ajax({
                    url: Config.JOBS_URL,
                    type: 'POST',
                    data: $form.serialize(),
                    success: function(result) {
                        var uid = result.uid;
                        var url = '/jobs/' + uid;
                        window.location.href=url;
                    }
            });
            }
        });
    }
    
    
    /**
     * Initializes the feature selection tree.
     */
    function initSelectFeaturesTree(){
        // initialize the feature selection tree
        $.get(Config.HDM_TAGS_URL, function(data){
            var tree = [];
            $.map(data, function(idx, node){
                // top level of tree..
                var leaf = {
                    selectable: false,
                    state: {
                        checked: true,
                    }
                };
                leaf.text = node;
                addNodes(idx, leaf);
                tree.push(leaf);
            });
            
            function addNodes(idx, leaf){
                var nodes = [];
                $.map(idx, function(i, n){
                    if ($.isArray(i)) {
                        var l = {};
                        l.text = n;
                        l.selectable = true;
                        nodes.push(l)
                        leaf.nodes = nodes;
                        addNodes(i, l);
                    }
                    else {
                        var l = {};
                        l.text = idx[n];
                        nodes.push(l);
                        leaf.nodes = nodes;
                    }
                });
            }
            
            
            $('#feature-tree').treeview({
                data: tree,
                levels: 1,
                multiSelect: true,
                showBorder: false,
                showCheckbox: true,
            });
            
            // make sure all checked to begin with
            $('#feature-tree').treeview('checkAll');
        });
        
        
    }
    
    /*
     * Handles placename lookups using nominatim.
     * Only interested relations.
     */
    function initNominatim(){
        window.query_cache = {};
        $('#nominatim').typeahead({
            source: function (query, process) {
                        // check if user is entering bbox coordinates manually
                        if (checkQueryRegex(query)) {
                            return;
                        }
                        else {
                            // clear any existing features and reset the map extents
                            bbox.removeAllFeatures();
                            transform.unsetFeature();
                            unsetBounds();
                            map.zoomToExtent(regions.getDataExtent());
                            
                        }
                        // if in cache use cached value
                        if(query_cache[query]){
                            process(query_cache[query]);
                            return;
                        }
                        if( typeof searching != "undefined") {
                            clearTimeout(searching);
                            process([]);
                        }
                        searching = setTimeout(function() {
                            return $.getJSON(
                                Config.MAPQUEST_SEARCH_URL,
                                {
                                    q: query,
                                    format: 'json',
                                    limit: 10,
                                },
                                function(data){
                                    // build list of suggestions
                                    var suggestions = [];
                                    $.each(data, function(i, place){
                                        // only interested in relations
                                        if (place.osm_type === 'relation') {
                                            suggestions.push(place);
                                        }
                                    });
                                    // save result to cache
                                    query_cache[query] = suggestions;
                                    return process(suggestions);
                                }
                            );
                        }, 100); // ms
            },
            
            displayText: function(item){
                return item.display_name;
            },
            afterSelect: function(item){
                var boundingbox = item.boundingbox;
                var bottom = boundingbox[0], top = boundingbox[1],
                    left = boundingbox[2], right = boundingbox[3];
                var bounds = new OpenLayers.Bounds(left, bottom, right, top);
                // add the bounds to the map..
                var feature = buildBBoxFeature(bounds);
                // allow bbox to be modified
                if (feature){
                    transform.setFeature(feature);
                }
            }
        });
        
        /**
        * Tests if the query is a float
        */
        function checkQueryRegex(query){
            var reg = new RegExp('[-+]?([0-9]*.[0-9]+|[0-9]+)');
            if (reg.test(query)){
                return true;
            }
        }
        
        /**
         * Construct the feature from the bounds.
         */
        function buildBBoxFeature(bounds){
            // convert to web mercator
            var merc_bounds = bounds.clone().transform('EPSG:4326', 'EPSG:3857');
            var geom = merc_bounds.toGeometry();
            var feature = new OpenLayers.Feature.Vector(geom);
            // add the bbox to the map
            bbox.addFeatures([feature]);
            map.zoomToExtent(bbox.getDataExtent());
            // validate the selected extents
            if (validateBounds(merc_bounds)) {
                setBounds(merc_bounds);
                return feature;
            }
            else {
                unsetBounds();
            }
        }
        
        /**
         * Validate manually entered bounding box.
         */
        $('#nominatim').bind('input', function(e){
            var val = $(this).val();
            // if search field is empty, reset map
            if (val === '') {
                unsetBounds();
                bbox.removeAllFeatures();
                box.deactivate();
                transform.unsetFeature();
                map.zoomToExtent(regions.getDataExtent());
                validateBounds();
                return;
            }
            // if entering coordinates manually..
            var isEnterBBox = checkQueryRegex(val);
            if (isEnterBBox) {
                // remove existing features
                bbox.removeAllFeatures();
                var coords = val.split(',');
                // check for correct number of coords
                if (coords.length != 4) {
                     bbox.removeAllFeatures();
                     validateBounds();
                     return;
                }
                // test for empty invalid coords
                for (i = 0; i < coords.length; i++){
                     if (coords[i] === '' || !checkQueryRegex(coords[i])) {
                         bbox.removeAllFeatures();
                         validateBounds();
                         return;
                     }
                }
                var left = coords[0], bottom = coords[1],
                    right = coords[2], top = coords[3];
                // check for valid lat long extents 
                if ((parseFloat(left) < -180 || parseFloat(left) > 180) ||
                    (parseFloat(right) < -180 || parseFloat(right) > 180) ||
                    (parseFloat(bottom) < -90 || parseFloat(bottom) > 90) ||
                    (parseFloat(top) < -90 || parseFloat(top) > 90)){
                    bbox.removeAllFeatures();
                    validateBounds();
                    return;
                }
                // add feature
                var bounds = new OpenLayers.Bounds(left, bottom, right, top);
                buildBBoxFeature(bounds); 
            }
        });
    }
    
    
    
}());


$(document).ready(function() {
        // construct the UI app
        $('li#create-tab').bind('click', function(e){
            $('#create-export-map').css('visibility', 'visible');
            $('#create-controls').css('display','block');
            $('#list-export-map').css('visibility', 'hidden');
            $('#list-controls').css('display','none');
        });
        create.job.init();
});
