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
            initHDMFeatureTree();
            initOSMFeatureTree();
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
        var xmin = numeral(bounds.left).format(fmt);
        var ymin = numeral(bounds.bottom).format(fmt);
        var xmax = numeral(bounds.right).format(fmt);
        var ymax = numeral(bounds.top).format(fmt);
        // fire input event here to make sure fields validate..
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
    
        // track the number of uploaded files.
        var numUploadedFiles = 0;
        
        /*
         * Initialize the bootstrap form wizard.
         */
        $('#create-job-wizard').bootstrapWizard({
            tabClass: 'nav nav-pills',
            onTabClick: function(tab, navigation, index){
                //return validateTab(index);
                if (index == 2 || index == 3){
                    $('ul.pager.wizard').find('li.next > a').html('Skip');
                }
                else{
                    $('ul.pager.wizard').find('li.next > a').html('Next');
                }
            },
            onNext: function(tab, navigation, index){
                if (index == 2 || index == 3){
                    $('ul.pager.wizard').find('li.next > a').html('Skip');
                }
                else{
                    $('ul.pager.wizard').find('li.next > a').html('Next');
                }
                // update summary if user navigates there..
                if (index == 4) {
                    updateExportSummaryTab();
                }
            },
            onPrevious: function(tab, navigation, index){
                if (index == 2 || index == 3){
                    $('ul.pager.wizard').find('li.next > a').html('Skip');
                }
                else{
                    $('ul.pager.wizard').find('li.next > a').html('Next');
                }
            }
        });
        
        // ----  FORM VALIDATION ---- //
        
        /*
         * Set up form validation.
         */
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
                },
                'filename': {
                    validators: {
                        notEmpty: {
                            message: 'The filename is required and cannot be empty.'
                        },
                    }
                },
                'config_type': {
                    validators: {
                        notEmpty: {
                            message: 'The configuration type is required and cannot be empty.'
                        },
                    }
                },
            }
        })
        .on('success.form.fv', function(e){
            e.preventDefault();
            /*
             * Enable the submit button, but prevent automatic form submission
             * on successful validation as this is done by ajax call
             * when the submit button is clicked.
             */
            $('#btn-submit-job').prop('disabled', 'false');
        })
        .on('success.field.fv', function(e) {
            // re-enable the file upload button when field is valid
            if (e.target.id === 'filename' || e.target.id === 'config_type') {
                $('button#upload').prop('disabled', false);
                $('button#select-file').prop('disabled', false);
            }
        }).on('err.field.fv', function(e) {
            // re-enable the file upload button when field is valid
            if (e.target.id === 'filename' || e.target.id === 'config_type') {
                $('button#upload').prop('disabled', true);
                $('button#select-file').prop('disabled', true);
            }
        });
        
        
        /*
         * Validates a wizard tab given the tab index.
         */
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
        
        /*
         * Validates the file upload tab.
         */
        function validateFileUploadTab() {
            var fv = $('#create-job-form').data('formValidation'), // FormValidation instance
                // The current tab
                $tab = $('#create-job-form').find('.tab-pane').eq(3);
            
            // validate the form panel contents
            fv.validateContainer($tab);
            var isValid = fv.isValidContainer($tab);
            if ((isValid === false || isValid === null)){
                // stay on this tab
                $('button#upload').prop('disabled', true);
                return false;
            }
            $('button#upload').prop('disabled', false);
            
            // reset validation on fields
            fv.resetField($('input#filename'));
            fv.resetField($('select#config_type'));
            
            return true;
        }
        
        // ----- UPLOAD TAB ----- //
        
        $('button#select-file').bind('click', function(e){
            if (!validateFileUploadTab()) {
                e.preventDefault();
                $(this).prop('disabled', true);
            }
        });
        
        /*
         * Listen for changes on file selection button.
         */
        $('.btn-file :file').on('change', function(){
                var $input = $(this),
                numFiles = $input.get(0).files ? $input.get(0).files.length : 1,
                label = $input.val().replace(/\\/g, '/').replace(/.*\//, '');
                $input.trigger('fileselect', [numFiles, label]);
        });
        
        /*
         * Handle file selection.
         */
        $('.btn-file :file').on('fileselect', function(event, numFiles, label) {
            /*
             * disable the input fields.
             * dont want these changed after this point.
             */
            $('input#filename').prop('disabled', true);
            $('select#config_type').prop('disabled', true);
            $('input#publish_config').prop('disabled', true);
            var $filelist = $('#filelist');
            var $select = $('.btn-file');
            var $upload = $('button#upload');
            $upload.prop('disabled', false);
            var type = $('option:selected').val();
            var published = $('input#publish_config').is(':checked') ? 'Published' : 'Private';
            
            var html = '<tr class="config"><td><i class="fa fa-file"></i>&nbsp;&nbsp;<span>' + label + '</span></td>' +
                       '<td>' + type + '</td><td>' + published + '</td>' +
                       '<td><button id="remove" type="button" class="btn btn-warning btn-sm pull-right">Remove&nbsp;&nbsp;<span class="glyphicon glyphicon-remove"></span></button></td></tr>';
            $filelist.append(html);
            $filelist.css('display', 'block');
            $select.css('visibility', 'hidden');
            $upload.css('visibility', 'visible');
            // handle events on the remove button if file selected
            $('button#remove').bind('click', function(e){
                $('input#filename').prop('disabled', false);
                $('select#config_type').prop('disabled', false);
                $('input#publish_config').prop('disabled', false);
                var $select = $('.btn-file');
                var $upload = $('button#upload');
                var $filelist = $('#filelist');
                var $fileupload = $('#fileupload');
                // clear the selected files list
                $fileupload.val('');
                // get number of selected files in the table
                var selected = $('#filelist tr').length  -1; // exclude th
                if (selected == 1) {
                    $(e.target).parent().parent().remove();
                    $('#filelist').css('display', 'none');
                }
                else {
                    // just remove this row..
                    $(e.target).parent().parent().remove();
                }
                // toggle file select and upload buttons
                $upload.css('visibility', 'hidden');
                $select.css('visibility', 'visible');
                // clear input fields
                $('input#filename').val('');
                $('option#select-message').prop('selected', true);
                $('input#publish_config').prop('checked', false);
                // reset the input field validation
                var fv = $('#create-job-form').data('formValidation');
                fv.resetField($('input#filename'));
                fv.resetField($('select#config_type'));
                $('#create-job-form').trigger('change');
            });
        });
        
        /*
         * Handle config file upload.
         */
        $('button#upload').bind('click', function(e){
            if (!validateFileUploadTab()){
                e.preventDefault();
                return;
            }
            // disable the upload button
            $('button#upload').prop('disabled', true);
            // show progress bar
            $('button#remove').css('display', 'none');
            $('.progress').css('display', 'block');
            var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
            var filename = $('input#filename').val();
            var config_type = $('select#config_type').val();
            switch (config_type) {
                case 'PRESET':
                    $('option#select-preset').prop('disabled', true);
                    break;
                case 'TRANSFORM':
                    $('option#select-transform').prop('disabled', true);
                    break;
                case 'TRANSLATION':
                    $('option#select-translate').prop('disabled', true);
                    break;
            }
            var published = $('input[name="publish_config"]').is(':checked');
            var data = new FormData();
            data.append('name', filename);
            data.append('config_type', config_type);
            data.append('published', published);
            var $filedata = $('#fileupload').get(0).files[0];
            data.append('upload', $filedata);
            $.ajax({
                // post to the config endpoint
                url: Config.CONFIGURATION_URL,
                type: 'POST',
                contentType: false,
                data: data,
                xhr: function() {
                    var xhr = $.ajaxSettings.xhr();
                    if(xhr.upload){ // Check if upload property exists
                        xhr.upload.addEventListener('progress', handleProgress, false); // For handling the progress of the upload
                    }
                    else {
                        console.log('File upload not supported in this browser');
                        // whats the fallback?
                        //TODO: alert user here..
                    }
                    return xhr;
                },
                processData: false, // send as multipart
                beforeSend: function(jqxhr){
                    // set the crsf token header for authentication
                    jqxhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(result, textStatus, jqxhr) {
                    // increment the number of uploaded files
                    numUploadedFiles += 1;
                    // add the delete button to the uploaded file
                    var $td = $('#filelist tr').last().find('td').last();
                    $td.empty();
                    var html = '<button id="' + result.uid + '" type="button" class="delete-file btn btn-danger btn-sm pull-right">' +
                                        'Delete&nbsp;&nbsp;<span class="glyphicon glyphicon-trash">' +
                                '</span></button>';
                    $td.html(html);
                    
                    // update the config inputs on the form
                    updateConfigInputs(result);
                    
                    // reset the form for more file uploads..
                    resetUploadConfigTab(textStatus);   
                    
                    // handle delete events
                    $('.delete-file').bind('click', function(e){
                        var that = $(this);
                        var data = new FormData();
                        data.append('_method', 'DELETE');
                        $.ajax({
                            url: Config.CONFIGURATION_URL + '/' + e.target.id,
                            type: 'POST',
                            data: data,
                            contentType: false,
                            processData: false,
                            beforeSend: function(jqxhr){
                                // set the crsf token header for authentication
                                var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
                                jqxhr.setRequestHeader("X-CSRFToken", csrftoken);
                            },
                            success: function(result, textStatus, jqxhr) {
                                // decrement the number of uploaded files
                                numUploadedFiles -= 1;
                                resetUploadConfigTab(textStatus);
                                // clear the selected files list
                                var $fileupload = $('#fileupload');
                                $fileupload.val('');
                                
                                // re-enable this config_type in the select combo
                                var config_type = that.parent().parent().find('td').eq(1).html();
                                var $option = $('option[value="' + config_type + '"]');
                                $option.prop('disabled', false);
                                
                                // remove the config form input value
                                var config_type_lwr = config_type.toLowerCase();
                                $('#' + config_type_lwr).val();
                                
                                // get number of selected files in the table
                                var selected = $('#filelist tr.config').length;
                                if (selected == 1) {
                                    // remove the row and hide the table
                                    that.parent().parent().fadeOut(300, function(){
                                        $(this).remove();
                                        $('#filelist').css('display', 'none');
                                        // trigger change event on form when config deleted
                                        $('#create-job-form').trigger('change');
                                    });  
                                }
                                else {
                                    // just remove the deleted row
                                    that.parent().parent().fadeOut(300, function(){
                                        $(this).remove();
                                        // trigger change event on form when config deleted
                                        $('#create-job-form').trigger('change');
                                    });
                                }
                                
                            }
                        });
                        
                    });
                },
                error: function(jqxhr, textStatus, errorThrown){
                    console.log(jqxhr);
                    resetUploadConfigTab(textStatus);
                    var modalOpts = {
                        keyboard: true,
                        backdrop: 'static',
                    }
                    var message = jqxhr.responseJSON.message[0];
                    $('p#message').html(message);
                    $("#uploadConfigError").modal(modalOpts, 'show');
                }
            });
        });
        
        /*
         * Updates the form with the uploaded config ids
         */
        function updateConfigInputs(result){
            var uid = result.uid;
            switch (result.config_type){
                case "PRESET":
                    $('input#preset').val(uid);
                    break;
                case "TRANSLATION":
                    $('input#translation').val(uid);
                    break;
                case "TRANSFORM":
                    $('input#transform').val(uid);
                    break;
            }
        }
        
        /*
         * Resets the upload config tab on success or failure.
         */
        function resetUploadConfigTab(textStatus){
            // hide the progress bar
            $('.progress').css('display', 'none');
            $('.progress-bar').css('width', '0%');
            
            // toggle file selection and upload buttons
            $('button#upload').css('visibility', 'hidden');
            $('.btn-file').css('visibility', 'visible');
            
            // reset the fields.
            $('input#filename').val('');
            $('option#select-message').prop('selected', true);
            $('input#publish_config').prop('checked', false);
            
            // check if max uploaded is reached
            if (numUploadedFiles == 3) {
                $('input#filename').prop('disabled', true);
                $('select#config_type').prop('disabled', true);
                $('input#publish_config').prop('disabled', true);
                $('button#select-file').prop('disabled', true);
            }
            else {
                // re-enable the fields
                $('input#filename').prop('disabled', false);
                $('select#config_type').prop('disabled', false);
                $('input#publish_config').prop('disabled', false);
                $('button#select-file').prop('disabled', false);
            }
            
            if (textStatus === 'error') {
                // clear the selected files list
                var $fileupload = $('#fileupload');
                $fileupload.val('');
                // get number of selected files in the table
                var selected = $('#filelist tr').length  -1; // exclude <th>
                if (selected == 1) {
                    // remove the last entry in the table
                    $('#filelist tr').last().remove();
                    $('#filelist').css('display', 'none');
                }
                else {
                    // just remove this row..
                    $('#filelist tr').last().remove();
                }
            }
        }
        
        /*
         * Updates progressbar on file upload.
         */
        function handleProgress(e){
            if(e.lengthComputable){
                var percent = e.loaded / e.total * 100;
                $('.progress-bar').attr({value:e.loaded,max:e.total});
                $('.progress-bar').css('width', percent + '%');
            }
        }
        
        
        // ----- SUMMARY TAB ----- //
        
        /*
         * Listen for changes to the form
         * and update the export summary tab.
         */
        $('#create-job-form').bind('change', function(e){
            var name = $(this).find('input[name="name"]').val();
            var description = $(this).find('textarea[name="description"]').val();
            var event = $(this).find('input[name="event"]').val();
            $('#summary-name').html(name);
            $('#summary-description').html(description);
            $('#summary-event').html(event);
            var formats = [];
            var $ul = $('<ul>');
            $.each($(this).find('input[name="formats"]:checked'), function(i, format){
                var val = $(this).val();
                switch (val){
                    case 'obf':
                        $ul.append($('<li>OSMAnd Format</li>'));
                        break;
                    case 'shp':
                        $ul.append($('<li>ESRI Shapefile Format</li>'));
                        break;
                    case 'kml':
                        $ul.append($('<li>KML Format</li>'));
                        break;
                    case 'garmin':
                        $ul.append($('<li>Garmin IMG Format</li>'));
                        break;
                    case 'sqlite':
                        $ul.append($('<li>SQlite Database Format</li>'));
                        break;
                }
            });
            $('#summary-formats').html($ul);
            var $tbl = $('<table class="table">');
            $tbl.append('<tr><th>Filename</th><th>Type</th><th>Status</th></tr>');
            $('#filelist tr.config').each(function(idx, config){
                 var filename = $(config).find('td').eq(0).find('span').html();
                 var config_type = $(config).find('td').eq(1).html();
                 var status = $(config).find('td').eq(2).html();
                 $tbl.append('<tr><td>' + filename + '</td><td>' + config_type + '</td><td>' + status + '</td></tr>');
            });
            $('#summary-configs').html($tbl);
        });
        
        // ----- FORM SUBMISSION ----- //
        
        /*
         * Submits the export job.
         */
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
            
            /*
             * Disable config form field validation
             * as validation of these fields is
             * only required on config upload.
             */
            fv.enableFieldValidators('filename', false);
            fv.enableFieldValidators('config_type', false);
            
            fv.validate(); // validate the form
            var fvIsValidForm = fv.isValid();
            if (!fvIsValidForm) {
                // alert user here..
                alert('invalid form');
                e.preventDefault();
            }
            else {
                // submit the form..
                var fields = $form.serializeArray();
                var form_data = {};
                var tags = [];
                var formats = [];
                $.each(fields, function(idx, field){
                    console.log(idx, field);
                    // ignore config upload related fields
                    switch (field.name){
                        case 'filename': break;
                        case 'config_type': break;
                        case 'publishconfig': break;
                        case 'published':
                            form_data['published'] = true;
                            break;
                        case 'formats':
                            formats.push(field.value);
                        default:
                            form_data[field.name] = field.value;
                    }
                });
                // get the selected tags
                var selected_tags = $('input.entry:checked');
                $.each(selected_tags, function(idx, entry){
                    var tag = {};
                    var key = entry.getAttribute('data-key');
                    var value = entry.getAttribute('data-val');
                    var geom_types = entry.getAttribute('data-geom');
                    var data_model = entry.getAttribute('data-model');
                    tag["key"] = key;
                    tag["value"] = value;
                    tag["geom_types"] = geom_types.split(',');
                    tag["data_model"] = data_model;
                    tags.push(tag)
                });
                // add tags and formats to the form data
                form_data["tags"] = tags;
                form_data["formats"] = formats;
                // convert to json string for submission.
                var json_data = JSON.stringify(form_data);
                $.ajax({
                    // post json to the api endpoint
                    url: Config.JOBS_URL,
                    type: 'POST',
                    dataType: 'json',
                    contentType: 'application/json',
                    data: json_data,
                    processData: false, // send as json
                    beforeSend: function(jqxhr){
                        // set the crsf token header for authentication
                        var csrftoken = form_data['csrfmiddlewaretoken'];
                        jqxhr.setRequestHeader("X-CSRFToken", csrftoken);
                    },
                    success: function(result) {
                        var uid = result.uid;
                        var url = '/jobs/' + uid;
                        window.location.href=url;
                    }
                });
            }
        });
    }
    
    // ----- FEATURE SELECTION TREES ----- //
    
    /*
     * Initialises the HDM feature tree.
     */
    function initHDMFeatureTree(){
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
                                           '<div class="checkbox tree-checkbox"><input class="entry" type="checkbox" data-model="HDM" data-geom="' + geom_str + '" data-key="' + key + '" data-val="' + val + '" checked/></div>' +
                                        '</li>');
                        $level.append($entry);
                    }
                    else {
                        var collapse = level_idx > 0 ? 'collapse' : '';
                        var state = level_idx == 0 ? 'open' : 'closed';
                        var icon = level_idx == 0 ? 'fa-minus-square-o' : 'fa-plus-square-o';
                        var root = level_idx == 0 ? 'root' : '';
                        var $nextLevel = $('<li class="level nav-header ' + state + ' ' + root + '"><label><i class="level fa ' + icon + ' fa-fw"></i>' + k + '</label>' + 
                                            '<div class="checkbox tree-checkbox"><input class="level" type="checkbox" checked/></div>');
                        var $nextUL = $('<ul class="nav nav-list sub-level ' + collapse + '">');
                        $nextLevel.append($nextUL);
                        $level.append($nextLevel);
                        level_idx += 1;
                        traverse(v, $nextUL, level_idx);
                    }
                });
            }
        
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
            
            // toggle level child nodes
            $('#hdm-feature-tree input.level').on('change', function(e){
                // toggle checkboxes on children when level checkbox is changed
                var checked = $(this).is(':checked');
                
                $(this).parent().parent().find('ul input').each(function(i, input){
                    $(input).prop('checked', checked);
                });
                
                $(this).parentsUntil('#hdm-feature-tree', 'li.level').slice(1).each(function(i, level){
                    $input = $(level).find('input.level:first');
                    var childrenChecked = $(level).find('ul input.level:checked').length > 0 ? true : false;
                    if (childrenChecked) {
                        $input.prop('checked', true);
                    }
                    else {
                        $input.prop('checked', false);
                    }
                });

            });
            
            /*
            * Handle events on entry checkboxes.
            */
            $('#hdm-feature-tree input.entry').on("change", function(e){
                // fire changed event on levels
                $('#hdm-feature-tree input.level').trigger("entry:changed", e);
            });
            
            /*
             * Listen for changes on entry level checkboxes
             * and update levels accordingly.
             */
            $('#hdm-feature-tree input.level').on("entry:changed", function(e){
                var $currentLevel = $(this).parent().parent();
                var hasCheckedChildren = $currentLevel.find('input.entry:checked').length > 0 ? true : false;
                //var hasChildLevelsChecked = $currentLevel.find('input.level:checked').length > 0 ? true : false;
                if (hasCheckedChildren) {
                    var $input = $currentLevel.find('input:first');
                    $input.prop('checked', true);
                }
                else {
                    var $input = $currentLevel.find('input:first');
                    $input.prop('checked', false);
                }
            });    
        });
    }
    
    /*
     * Initialises the OSM feature tree.
     */
    function initOSMFeatureTree(){
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
            function traverse(data, $level){
                $.each(data, function(k,v){
                    if ($(v).attr('displayName')){
                        var name = $(v).attr('displayName');
                        var tag = $(v).attr('tag');
                        var key = tag.split(':')[0];
                        var val = tag.split(':')[1];
                        var geom = $(v).attr('geom');
                        geom_str = geom.join([separator=',']);
                        var $entry = $('<li class="entry"><label><i class="fa fa-square-o fa-fw"></i>' + name + '</label>' +
                                           '<div class="checkbox tree-checkbox"><input class="entry" type="checkbox" data-model="OSM" data-geom="' + geom_str + '" data-key="' + key + '" data-val="' + val + '"/></div>' +
                                        '</li>');
                        $level.append($entry);
                    }
                    else {
                        var collapse = level_idx > 0 ? 'collapse' : '';
                        var $nextLevel = $('<li class="level nav-header closed"><label><i class="level fa fa-plus-square-o fa-fw"></i>' + k + '</label>' + 
                                            '<div class="checkbox tree-checkbox"><input class="level" type="checkbox" disabled/></div>');
                        var $nextUL = $('<ul class="nav nav-list sub-level ' + collapse + '">');
                        $nextLevel.append($nextUL);
                        $level.append($nextLevel);
                        level_idx += 1;
                        traverse(v, $nextUL, level_idx);
                    }
                });
            } 
            
            /*
             * Handle click events on tree levels
             */
            $('#osm-feature-tree li.level > label').bind('click', function(e){
                if ($(this).parent().hasClass('open')) {
                    $(this).parent().removeClass('open').addClass('closed');
                    $(this).parent().find('i.level').removeClass('fa-plus-minus-o').addClass('fa-plus-square-o');
                }
                else {
                    $(this).parent().removeClass('closed').addClass('open');
                    $(this).parent().find('i.level').removeClass('fa-plus-square-o').addClass('fa-minus-square-o');
                }
                //$(this).parent().children('ul.sub-level').toggle(150);
                
            });
            
            /*
             * Handle events on sub-levels
             */
            /*
            $('li.level > .tree-checkbox').bind('click', function(e){
                var checked = $(this).find('input').is(':checked');
                $(this).parent().find('.tree-checkbox').each(function(i, value){
                    var $input = $(value).find('input');
                    $input.prop('checked', checked);
                })
            });
            */
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
                        }, 200); // timeout before initiating search..
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
                // test for empty or invalid coords
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
