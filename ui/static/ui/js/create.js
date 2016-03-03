create = {};
create.job = (function(){
    var map;
    var regions;
    var mask;
    var transform;
    var max_bounds_area = $('#user-max-extent').text();

    return {
        init: function(){
            initMap();
            initPopovers();
            initHDMFeatureTree();
            initOSMFeatureTree();
            initNominatim();
            initPresetSelectionHandler();
            initConfigSelectionHandler();
        }
    }

    /*
     * Initialize the map
     * and the UI controls.
     */
    function initMap() {
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
        osm.attribution = "&copy; <a href='//www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors.";
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
            transform.unsetFeature();
            box.activate();
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
                                 + 'value="' + format.slug + '"'
                                 + 'data-description="' + format.description + '"/>'
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
        fmt = '0.000000' // format to 6 decimal places .11 metre precision
        var xmin = numeral(bounds.left).format(fmt);
        var ymin = numeral(bounds.bottom).format(fmt);
        var xmax = numeral(bounds.right).format(fmt);
        var ymax = numeral(bounds.top).format(fmt);
        // fire input event here to make sure fields validate..
        $('#xmin').val(xmin).trigger('input');
        $('#ymin').val(ymin).trigger('input');
        $('#xmax').val(xmax).trigger('input');
        $('#ymax').val(ymax).trigger('input');
        // update coordinate display
        var coords = gettext('(West, South, East, North): ') + xmin + ', ' + ymin + ', ' + xmax + ', ' + ymax;
        $('span#coordinates').html(coords);
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
        $('span#coordinates').empty();
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
            //$('#alert-extents').html('<span>Select area to export.&nbsp;&nbsp;</span><span class="glyphicon glyphicon-remove">&nbsp;</span>');
            $('#alert-extents').html('<span>' + gettext('Select area to export') + '&nbsp;&nbsp;</span>');
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
        bounds.transform('EPSG:3857', 'EPSG:4326')
        // trim bounds to 6 decimal places before calculating geodesic area
        var left = bounds.left.toFixed(6);
        var bottom = bounds.bottom.toFixed(6);
        var right = bounds.right.toFixed(6);
        var top = bounds.top.toFixed(6);
        
        bounds_trunc = new OpenLayers.Bounds(left, bottom, right, top);
        var area = bounds_trunc.toGeometry().getGeodesicArea() / 1000000; // sq km
        
        // format the area and max bounds for display..
        var area_str = numeral(area).format('0 0');
        var max_bounds_str = numeral(max_bounds_area).format('0 0');

        if (!valid_region) {
           // invalid region
           validateBBox(); // trigger validation on extents
           $('#valid-extents').css('visibility','hidden');
           $('#alert-extents').css('visibility','visible');
           $('#alert-extents').html('<strong>' + gettext('Invalid Extent') + '</strong><br/>' + gettext('Selected area is outside') + '<br/>' + gettext('a valid HOT Export Region'))
           return false;
        } else if (area > max_bounds_area) {
           // area too large
           validateBBox(); // trigger validation on extents
           $('#valid-extents').css('visibility','hidden');
           $('#alert-extents').css('visibility','visible');
           $('#alert-extents').html('<strong>' + gettext('Invalid Extent') + '</strong><br/>' + gettext('Selected area is ') + area_str
                                 + gettext(' sq km.') + '<br/>' + gettext('Must be less than ') + max_bounds_str + gettext(' sq km.'));
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
                        pointRadius: 4,
                        fillColor: "blue",
                        fillOpacity: 1,
                        strokeColor: "blue",
                    },
                    {
                        context: {
                            getDisplay: function(feature) {
                                // hide the resize handles except at the se & nw corners
                                return  feature.attributes.role === "n-resize"  ||
                                        feature.attributes.role === "ne-resize" ||
                                        feature.attributes.role === "e-resize"  ||
                                        feature.attributes.role === "s-resize"  ||
                                        feature.attributes.role === "sw-resize" ||
                                        feature.attributes.role === "w-resize"  ? "none" : ""
                            }
                        }
                    })
                });
    }

    /*
     * Initialize the form validation.
     */
    function initForm(){

        /*
         * Initialize the bootstrap form wizard.
         */
        $('#create-job-wizard').bootstrapWizard({
            tabClass: 'nav nav-pills',
            onTabClick: function(tab, navigation, index){
                return validateTab(index);
            },
            onTabShow: function(tab, navigation, index){
                if (index == 1) {
                    $('#create-job-wizard').bootstrapWizard('enable', 2);
                    $('#create-job-wizard').bootstrapWizard('enable', 3);
                    $('#create-job-wizard').bootstrapWizard('enable', 4);
                }
                if (index == 2 || index == 3) {
                    $('li.next').css('display', 'block');
                }
                else {
                    $('li.next').css('display', 'none');
                }
            },
            onNext: function(tab, navigation, index){
                return validateTab(index);
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
                //invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            excluded: ':disabled',
            // List of fields and their validation rules
            fields: {
                'name': {
                    validators: {
                        notEmpty: {
                            message: gettext('The export job name is required and cannot be empty')
                        },
                    }
                },
                'description': {
                    validators: {
                        notEmpty: {
                            message: gettext('The description is required and cannot be empty')
                        }
                    }
                },
                'formats': {
                    validators: {
                        choice: {
                            min: 1,
                            max: 7,
                            message: gettext('At least one export format must be selected')
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
                            message: gettext('The preset name is required and cannot be empty')
                        },
                    }
                },
                /*
                'config_type': {
                    validators: {
                        notEmpty: {
                            message: 'The configuration type is required and cannot be empty'
                        },
                    }
                },
                */
            }
        })
        .on('success.form.fv', function(e){
            e.preventDefault();
            /*
             * Enable the submit button, but prevent automatic form submission
             * on successful validation as this is done by ajax call
             * when the submit button is clicked.
             */
            $('#btn-submit-job').prop('disabled', false);
            $('#btn-submit-job').removeClass('disabled');
        })
        .on('err.form.fv', function(e){
            /*
             * Disable submit button when form is invalid.
             */
            $('#btn-submit-job').prop('disabled', true);
            $('#btn-submit-job').addClass('disabled');
        })
        .on('success.field.fv', function(e) {
            // re-enable the file upload button when field is valid
            if (e.target.id === 'filename' || e.target.id === 'config_type') {
                $('button#upload').prop('disabled', false);
                $('#select-file').prop('disabled', false);
            }
        }).on('err.field.fv', function(e) {
            // re-enable the file upload button when field is valid
            if (e.target.id === 'filename' || e.target.id === 'config_type') {
                $('button#upload').prop('disabled', true);
                $('#select-file').prop('disabled', true);
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
                $('#btn-submit-job').prop('disabled', true);
                $('#btn-submit-job').addClass('disabled');
            }
            else {
                $('#btn-submit-job').prop('disabled', false);
                $('#btn-submit-job').removeClass('disabled');
            }

            // ignore upload tab as we apply custom validation there..
            /*
            var id = $tab.attr('id');
            if (id === 'features' || id === 'summary' || id === 'upload'){
                fv.resetField('filename');
                $('#select-file').prop('disabled', false);
                return true;
            }
            */

            /*
             * Disable config form field validation
             * as validation of these fields is
             * only required on config upload.
             */
            fv.enableFieldValidators('filename', false);

            // validate the bounding box extents
            fv.validateContainer($bbox);
            var isValidBBox = fv.isValidContainer($bbox);
            if (isValidBBox === false || isValidBBox === null) {
                validateBounds(bbox.getDataExtent());
            }

            // validate the form panel contents
            fv.validateContainer($tab);
            var isValidStep = fv.isValidContainer($tab);
            if ((isValidStep === false) ||
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

        $('#select-file').on('click', function(e){
            var fv = $('#create-job-form').data('formValidation');
            fv.enableFieldValidators('filename', true);
            $(this).popover('hide');
            if (!validateFileUploadTab()) {
                e.preventDefault();
                $(this).prop('disabled', true);
            }
        });

        /*
         * Listen for changes on file selection button.
         */
        $('#select-file :file').on('change', function(){
                var $input = $(this),
                    filename = $input.val().replace(/\\/g, '/').replace(/.*\//, ''),
                    $filelist = $('#filelist'),
                    selection = {},
                    //type = $('option:selected').val(),
                    type = $('input#config_type').val(),
                    published = $('input#publish_config').is(':checked') ? 'Published' : 'Private';
                selection['filename'] = filename;
                selection['config_type'] = type;
                selection['published'] = published;

                // disable form fields
                $('input#filename').prop('disabled', true);
                $('select#config_type').prop('disabled', true);
                $('input#publish_config').prop('disabled', true);

                // toggle select and upload button visibility
                $('.btn-file').css('visibility', 'hidden');
                $('button#upload').prop('disabled', false).css('visibility', 'visible');

                // disable config-browser
                $('button#select-config').prop('disabled', true);

                // trigger the selection event
                $filelist.trigger({type: 'config:fileselected', source: 'config-upload', selection: selection});
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
            $('button#remove-upload').prop('disabled', true);

            // disable the config-select button
            $('button#select-config').prop('disabled', true);

            // disable selected config remove buttons until file uploaded
            $(this).find('tr.config').find('button').each(function(idx, btn){
                $(btn).prop('disabled', true);
            });

            // show progress bar
            $('button#remove').css('display', 'none');
            $('.progress').css('display', 'block');
            var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
            var filename = $('input#filename').val();
            var config_type = $('input#config_type').val();

            /*
             * Put this back later if we implement translation or transforms
             *
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
            */

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
                        window.location.href = Config.UPDATE_BROWSER_URL
                    }
                    return xhr;
                },
                processData: false, // send as multipart
                beforeSend: function(jqxhr){
                    // set the crsf token header for authentication
                    jqxhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(result, textStatus, jqxhr) {

                    // trigger preset:selected event
                    if (result.config_type === 'PRESET') {
                        $(document).trigger({type: 'preset:selected', source: 'config-upload'});
                    }
                    var selection = {};
                    selection['uid'] = result.uid;
                    selection['filename'] = result.filename;
                    selection['config_type'] = result.config_type;
                    selection['published'] = result.published;
                    // notify the file list
                    $('#filelist').trigger({type: 'config:uploaded', source: 'config-upload', selection: selection});

                },
                error: function(jqxhr, textStatus, errorThrown){
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
         * Handle click on select config button (config-browser)
         */
        $('button#select-config').on('click', function(e){
            $(this).popover('hide');
            var modalOpts = {
                    keyboard: true,
                    backdrop: 'static',
            }
            // reset the input field validation
            var fv = $('#create-job-form').data('formValidation');
            fv.resetField($('input#filename'));
            $('#select-file').prop('disabled', false);
            $("#configSelectionModal").modal(modalOpts, 'show');
        });


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
                var description = format.getAttribute('data-description');
                $ul.append($('<li>' + description + '</li>'));
            });
            $('#summary-formats').html($ul);
        });

         /*
         * Listen for configurations being added to the filelist
         * and update state on this.
         */
        $('table#summary-configs').on('config:added', function(e){
            $('div#summary-configs').css('visibility', 'visible');
            var selection = e.selection;
            $('#filelist tr.config').each(function(idx, config){
                 var filename = $(config).find('td').eq(0).find('span').html();
                 var config_type = $(config).find('td').eq(1).html();
                 var status = $(config).find('td').eq(2).html();
                 $('table#summary-configs').append('<tr id="' + selection.uid + '" class="config"><td>' + filename + '</td><td>' + config_type + '</td><td>' + status + '</td></tr>');
            });
        });

        $('table#summary-configs').on('config:removed', function(e){
            var selection = e.selection;
            // remove the selected config from the table
            var configs = $('table#summary-configs tr.config').length;
            var $tr = $(this).find('tr#' + selection.uid);
            if (configs == 1) {
                // remove the config from the table
                $tr.remove();
                // hide the file list
                $('div#summary-configs').css('visibility', 'hidden');
            }
            else {
                // just remove this row..
                $tr.remove();
            }
        });

        /*
         * Handle selection events on config publish options.
         * Only one can be selected at at time.
         */
        $('input#feature_save').on('change', function(e){
            var checked = $(this).is(':checked');
            $featPub =  $('input#feature_pub');
            if (checked) {
                $featPub.prop('checked', false);
                $featPub.prop('disabled', true);
            }
            else {
                $featPub.prop('checked', false);
                $featPub.prop('disabled', false);
            }
        });

        $('input#feature_pub').on('change', function(e){
            var checked = $(this).is(':checked');
            $featSave =  $('input#feature_save');
            if (checked) {
                $featSave.prop('checked', false);
                $featSave.prop('disabled', true);
            }
            else {
                $featSave.prop('checked', false);
                $featSave.prop('disabled', false);
            }
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
            //fv.enableFieldValidators('config_type', false);

            fv.validate(); // validate the form
            var fvIsValidForm = fv.isValid();
            if (!fvIsValidForm) {
                // alert user here..
                e.preventDefault();
                var modalOpts = {
                    keyboard: true,
                    backdrop: 'static',
                }
                var message = ''
                var fields = fv.getInvalidFields();
                var field = $(fields[0]).attr('name');
                if (field === 'formats') {
                    message = 'Please select an export format.';
                }
                else {
                    message = 'The <strong>' + field + '</strong> field is required'
                }
                $('p#validation-message').html(gettext(message));
                $("#validationErrorModal").modal(modalOpts, 'show');
            }
            else {
                // submit the form..
                $('div#submit-spinner').css('display', 'block');
                $('#create-job-wizard').css('opacity', .5);
                $('#map-column').css('opacity', .5);
                var fields = $form.serializeArray();
                var form_data = {};
                var tags = [];
                var formats = [];
                $.each(fields, function(idx, field){
                    // ignore config upload related fields
                    switch (field.name){
                        case 'filename': break;
                        case 'config_type': break;
                        case 'publishconfig': break;
                        case 'published':
                            form_data['published'] = true;
                            break;
                        case 'feature_pub':
                            form_data['feature_pub'] = true;
                            break;
                        case 'feature_save':
                            form_data['feature_save'] = true;
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
                    var data_model = entry.getAttribute('data-model');
                    var levels = $(entry).parentsUntil('#' + data_model.toLowerCase() + '-feature-tree', 'li.level');
                    var groups = [];
                    var labels = $(levels).find('label:first');
                    $.each(labels, function(idx, label){
                        var group = $(label).text();
                        groups.push(group);
                    });
                    var tag = {};
                    var name = entry.getAttribute('data-name');
                    var key = entry.getAttribute('data-key');
                    var value = entry.getAttribute('data-val');
                    var geom_types = entry.getAttribute('data-geom');
                    tag['name'] = name;
                    tag["key"] = key;
                    tag["value"] = value;
                    tag["geom_types"] = geom_types.split(',');
                    tag["data_model"] = data_model;
                    tag["groups"] = groups;
                    tags.push(tag);
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
                        var url = '/exports/' + uid;
                        window.location.href=url;
                    },
                    error: function(jqXHR, textStatus, errorThrown){
                        if (jqXHR.status == 500 || jqXHR.status == 400) {
                            window.location.href = Config.CREATE_ERROR_URL;
                        }
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
        // turn off preset selection on config upload
        //$('option#select-preset').prop('disabled', true);
        /*
         * Fire preset selection on hdm-tree
         * to set the state of preset related controls.
         */
        $(document).trigger({type: 'preset:selected', source: 'hdm-feature-tree'});

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
                        var key = tag.split('=')[0];
                        var val = tag.split('=')[1];
                        var geom = $(v).attr('geom');
                        geom_str = geom.join([separator=',']);
                        var $entry = $('<li class="entry" data-toggle="tooltip" data-placement="right" title="' + key + '=' + val + '"><label><i class="fa fa-square-o fa-fw"></i>' + name + '</label>' +
                                           '<div class="checkbox tree-checkbox"><input class="entry" type="checkbox" data-model="HDM" data-geom="' +
                                            geom_str + '" data-key="' + key + '" data-val="' + val +'" data-name="' + name + '" checked/></div>' +
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

            /*
             * Handle events on sub-level checkboxes.
             */
            $('#hdm-feature-tree input.level').on('change', function(e){
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
                if (hasCheckedChildren) {
                    var $input = $currentLevel.find('input:first');
                    $input.prop('checked', true);
                }
                else {
                    var $input = $currentLevel.find('input:first');
                    $input.prop('checked', false);
                }
            });

            /*
             * Listen for changes to the HDM root node.
             * Trigger preset selection / deselection events.
             */
            $('#hdm-feature-tree li.root').on('change', function(e){
                var checked = $(this).find('input.level:first').is(':checked');
                $('#osm-feature-tree').find('input').each(function(idx, input){
                    $(input).prop('disabled', checked);
                });
                if (checked) {
                    $(document).trigger({type: 'preset:selected', source: 'feature-tree'});
                }
                else {
                    $(document).trigger({type: 'preset:deselected', source: 'feature-tree'});
                }
            });
        });
    }

    /*
     * Initialises the OSM feature tree.
     */
    function initOSMFeatureTree(){
        $.get(Config.OSM_TAGS_URL, function(data){
            var level_idx = 0;
            var $tree = $('#osm-feature-tree ul.nav-list');
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
                        var key = tag.split('=')[0];
                        var val = tag.split('=')[1];
                        var geom = $(v).attr('geom');
                        geom_str = geom.join([separator=',']);
                        var $entry = $('<li class="entry" data-toggle="tooltip" data-placement="right" title="' + key + '=' + val + '"><label><i class="fa fa-square-o fa-fw"></i>' + name + '</label>' +
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

            /*
             * Handle events on sub-level checkboxes.
             */
            $('#osm-feature-tree input.level').on('change', function(e){
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
            $('#osm-feature-tree input.entry').on("change", function(e){
                // fire changed event on levels
                $('#osm-feature-tree input.level').trigger("entry:changed", e);
            });

            /*
             * Listen for changes on entry level checkboxes
             * and update levels accordingly.
             */
            $('#osm-feature-tree input.level').on("entry:changed", function(e){
                var $currentLevel = $(this).parent().parent();
                var hasCheckedChildren = $currentLevel.find('input.entry:checked').length > 0 ? true : false;
                if (hasCheckedChildren) {
                    var $input = $currentLevel.find('input:first');
                    $input.prop('checked', true);
                }
                else {
                    var $input = $currentLevel.find('input:first');
                    $input.prop('checked', false);
                }
            });

            /*
             * Listen for changes to the OSM root node.
             */
            $('#osm-feature-tree li.root').on('change', function(e){
                var checked = $(this).find('input.level:first').is(':checked');
                $('#hdm-feature-tree').find('input').each(function(idx, input){
                    $(input).prop('disabled', checked);
                });
                if (checked) {
                    $(document).trigger({type: 'preset:selected', source: 'feature-tree'});
                }
                else {
                    $(document).trigger({type: 'preset:deselected', source: 'feature-tree'});
                }
            });
        });
    }

    /*
     * Handles placename lookups using nominatim.
     * Only interested in relations.
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
                                Config.GEONAMES_SEARCH_URL,
                                {
                                    q: query,
                                    maxRows: 20,
                                    username: 'hotexports',
                                    style: 'full'
                                },
                                function(data){
                                    // build list of suggestions
                                    var suggestions = [];
                                    var geonames = data.geonames;
                                    $.each(geonames, function(i, place){
                                        // only interested in features with a bounding box
                                        if (place.bbox) {
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
                //return item.display_name;
                names = [];
                item.name.trim() != "" ? names.push(item.name) : null;
                item.adminName1.trim() != "" ? names.push(item.adminName1) : null;
                item.adminName2.trim() != "" ? names.push(item.adminName2) : null;
                item.countryName.trim() != "" ? names.push(item.countryName) : null;
                return names.join(separator=', ');
            },
            afterSelect: function(item){
                var boundingbox = item.bbox;
                var bottom = boundingbox.south, top = boundingbox.north,
                    left = boundingbox.west, right = boundingbox.east;
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
                return feature;
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

    /*
     * Listens for preset selection events
     * and updates state on preset related
     * ui controls.
     *
     * Preset selection events can be triggered by:
     *  - hdm and osm feature-tree
     *  - config-upload
     *  - config-browser
     */
    function initPresetSelectionHandler(){
        // handle preset selections
        $(document).on('preset:selected', function(e){
            switch (e.source){
                case 'feature-tree':
                    // enable feature save and publish inputs
                    $('input#feature_save').prop('disabled', false);
                    $('input#feature_pub').prop('disabled', false);
                    break;
                case 'config-upload':
                    // disable the selection trees
                    $('#hdm-feature-tree, #osm-feature-tree').find('input').each(function(idx, input){
                        $(input).prop('checked', false);
                        $(input).prop('disabled', true);
                    });
                    // disable preset config types in the config browser
                    $('input[data-type="PRESET"]')
                        .each(function(i, input){
                            $(input).prop('disabled', true);
                            $(input).closest('tr').css('opacity', .5);
                    });
                    $('input#feature_save').prop('disabled', true);
                    $('input#feature_pub').prop('disabled', true);
                    break;
                case 'config-browser':
                    // disable the preset option on the config type selection control
                    $('option#select-preset').prop('disabled', true);
                    // clear and disable the feature selection trees
                    $('#hdm-feature-tree, #osm-feature-tree').find('input').each(function(idx, input){
                        $(input).prop('checked', false);
                        $(input).prop('disabled', true);
                    });
                    $('input#feature_save').prop('disabled', true);
                    $('input#feature_pub').prop('disabled', true);
                    break;
            }

        });

        // handle deselections
        $(document).on('preset:deselected', function(e){
            switch (e.source){
                case 'feature-tree':
                    // disable and uncheck feature save and publish inputs
                    $('input#feature_save').prop('disabled', true);
                    $('input#feature_save').prop('checked', false);

                    $('input#feature_pub').prop('disabled', true);
                    $('input#feature_pub').prop('checked', false);
                    // enable the preset option on the config type selection control
                    //$('option#select-preset').prop('disabled', false);
                    // enable preset config types in the config browser
                    $('input[data-type="PRESET"]')
                        .each(function(i, input){
                            $(input).prop('disabled', false);
                            $(input).closest('tr').css('opacity', 1);
                    });
                    break;
                case 'config-upload':
                    // re-enable the hdm-feature-tree and select all by default
                    $('#hdm-feature-tree').find('input').each(function(idx, input){
                        $(input).prop('disabled', false);
                        $(input).prop('checked', true);

                    });
                    // enable preset config types in the config browser
                    $('input[data-type="PRESET"]')
                        .each(function(i, input){
                            $(input).prop('disabled', false);
                            $(input).closest('tr').css('opacity', 1);
                    });
                    // enable the config_type selection option
                    $('option#select-preset').prop('disabled', false);
                    break;
                case 'config-browser':
                    // enable the preset option on the config type selection control
                    $('option#select-preset').prop('disabled', false);
                    // enable the hdm feature selection tree
                    $('#hdm-feature-tree').find('input').each(function(idx, input){
                        $(input).prop('disabled', false);
                        $(input).prop('checked', true);
                    });
                    break;
            }

        });
    }

    /*
     * Handles configuration selection events
     * when configurations are added or removed
     * to or from the filelist table.
     *
     * These events are triggered by:
     *  -   file selections on the upload config form  = config:fileselected
     *  -   a file successfully uploaded = config:uploaded
     *  -   config selections added by the config browser = config:added
     *  -   a pending file upload removed = config:remove-upload
     *  -   a configuration removed = config:removed
     *  -   an uploaded configuration deleted = config:upload-deleted
     *
     *  Other events fired:
     *  -   notification to the config-browser that a file is removed = filelist:removed
     *
     */
    function initConfigSelectionHandler(){

        var filesSelected = 0;

        $('#filelist').on('config:added config:uploaded', function(e){
            var selection = e.selection;
            var source = e.source;
            var uid = selection.uid;

            if (source == 'config-upload') {
                // add the uploaded uid to the table row
                $tr = $('#filelist').find('tr#upload');
                $tr.attr('id', selection.uid);

                // re-enable any remove buttons on the filelist
                $(this).find('tr.config').find('button').each(function(idx, btn){
                    $(btn).prop('disabled', false);
                });

                // add the delete button to the uploaded file
                var $td = $tr.find('td').last();
                $td.empty();
                var html = '<button id="' + selection.uid + '" type="button" class="delete-file btn btn-danger btn-sm pull-right">' +
                                    gettext('Delete') + '&nbsp;&nbsp;<span class="glyphicon glyphicon-trash">' +
                            '</span></button>';
                $td.html(html);

                // reset the form for more file uploads..
                resetUploadConfigTab('success');

                // notify the config-browser
                $('table#configurations').trigger({type: 'config:added', selection:selection});

                // handle delete events
                $tr.on('click', 'button#' + selection.uid, function(e){
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
                            // notify the config-browser
                            $('table#configurations').trigger({type: 'config:removed', selection: selection});
                            $('#filelist').trigger({type: 'config:delete-upload', selection: selection});
                        },
                        error: function(jqxhr, textStatus, errorThrown){
                            var status = jqxhr.status;
                            resetUploadConfigTab(textStatus);
                            var modalOpts = {
                                keyboard: true,
                                backdrop: 'static',
                            }
                            var message = '';
                            if (status === 404) {
                                message = gettext('Requested file not found')
                            }
                            else {
                                message = jqxhr.responseJSON.message[0];
                            }
                            $('p#message').html(message);
                            $("#uploadConfigError").modal(modalOpts, 'show');
                        }
                    });

                });
            }
            else {
                /*
                 * check that a file with the same id is not already on the list,
                 * e.g. from a user upload.
                 */
                $(this).find('tr[data-source="config-upload"]').each(function(idx, upload){
                    var uid = $(upload).attr('id');
                    if (uid == selection.uid) {
                        $(upload).remove();
                        filesSelected -= 1;
                    }
                })

                // add the selected config from config-browser to the table
                var $tr = $('<tr id="' + selection.uid + '" data-filename="' + selection.filename + '" data-source="' + source + '"' +
                                'data-type="' + selection.config_type + '" data-published="' + selection.published + '"' +
                                'class="config"><td><i class="fa fa-file"></i>&nbsp;&nbsp;<span>' + selection.filename + '</span></td>' +
                                '<td>' + selection.config_type + '</td><td>' + selection.published + '</td>' +
                                '<td><button id="' + selection.uid + '" type="button" class="btn btn-warning btn-sm pull-right">Remove&nbsp;&nbsp;<span class="glyphicon glyphicon-remove"></span></button></td></tr>');
                $(this).append($tr);
                $tr.on('click', 'button#' + selection.uid, function(e){
                    // notify the config-browser of removal
                    $('table#configurations').trigger({type: 'filelist:removed', selection: selection});
                    // remove from filelist
                    $('#filelist').trigger({type: 'config:removed', selection: selection});
                });

                // notify the config-browser
                $('table#configurations').trigger({type: 'config:added', selection:selection});
            }

            $(this).css('display', 'block');
            filesSelected += 1;
            updateConfigInputs(selection);

            // notify the summary config table on the summary tab
            $('table#summary-configs').trigger({type: 'config:added', selection:selection});

            // trigger max files check
            $(document).trigger({type: 'config:checkmaxfiles', filesSelected: filesSelected});

        });

        // a configuration file is selected for upload
        $('#filelist').on('config:fileselected', function(e){
            var selection = e.selection;
            var source = e.source;
            var html = '<tr id="upload" data-filename="' + selection.filename + '" data-source="' + source + '"' +
                        'data-type="' + selection.config_type + '" data-published="' + selection.published + '" ' +
                        'class="config"><td><i class="fa fa-file"></i>&nbsp;&nbsp;<span>' + selection.filename + '</span></td>' +
                       '<td>' + selection.config_type + '</td><td>' + selection.published + '</td>' +
                       '<td><button id="remove-upload" type="button" class="btn btn-warning btn-sm pull-right">Remove&nbsp;&nbsp;<span class="glyphicon glyphicon-remove"></span></button></td></tr>';
            $(this).append(html);
            $(this).css('display', 'block');

            // handle events on the remove button
            $('button#remove-upload').bind('click', function(e){
                $('#filelist').trigger({type: 'config:remove-upload'});
            });
        });

        // handle config selection removal from file list
        $('#filelist').on('config:removed', function(e){
            filesSelected -= 1;
            var selection = e.selection;

            // get the row being removed
            var $tr = $(this).find('tr#' + selection.uid);
            var config_type = $tr.find('td').eq(1).html();

            // re-enable that config type in the dropdown
            var $option = $('option[value="' + config_type + '"]');
            $option.prop('disabled', false);

            /*
             * If preset is being removed trigger deselected event
             * to notify other preset related ui controls.
             */
            if (config_type === 'PRESET') {
                $(document).trigger({type: 'preset:deselected', source: 'config-upload'});
            }

            // remove the config form input value
            var config_type_lwr = config_type.toLowerCase();
            $('input#' + config_type_lwr).val('');

            // remove the selected config from the table
            var configs = $('#filelist tr.config').length;
            var $tr = $(this).find('tr#' + selection.uid);
            if (configs == 1) {
               $tr.fadeOut(300, function(){
                    // remove the upload from the table
                    $(this).remove();
                    // hide the file list
                    $('#filelist').css('display', 'none');
                });
            }
            else {
                // just remove this row..
                $tr.fadeOut(300, function(){
                    // remove the upload from the table
                    $(this).remove();
                });
            }

            // trigger change event on form to update summary tab
            $('#create-job-form').trigger('change');

            $('table#summary-configs').trigger({type: 'config:removed', selection: selection});

            // trigger max files check
            $(document).trigger({type: 'config:checkmaxfiles', filesSelected: filesSelected});
        });

        // handle pending upload selection removal
        $('#filelist').on('config:remove-upload', function(e){
            // re-enable the upload input fields to allow another upload
            $('input#filename').prop('disabled', false);
            $('select#config_type').prop('disabled', false);
            $('input#publish_config').prop('disabled', false);
            $('input#filename').val('');
            $('option#select-message').prop('selected', true);
            $('input#publish_config').prop('checked', false);

            // reenable the select config button
            $('button#select-config').prop('disabled', false);

            // reset the input field validation
            var fv = $('#create-job-form').data('formValidation');
            fv.resetField($('input#filename'));
            //fv.resetField($('select#config_type'));

            // toggle file select and upload buttons
            $('#select-file').css('visibility', 'visible');
            $('button#upload').css('visibility', 'hidden');

            // clear the selected files list on the file input
            var $fileupload = $('#fileupload');
            $fileupload.val('');

            // clear configuration hidden inputs
            $('input#preset').val('');

            // remove the pending upload from the table
            var configs = $('#filelist tr.config').length;
            var $tr = $(this).find('tr#upload');
            if (configs == 1) {
               $tr.fadeOut(300, function(){
                    // remove the upload from the table
                    $(this).remove();
                    // hide the file list
                    $('#filelist').css('display', 'none');
                });
            }
            else {
                // just remove this row..
                $tr.fadeOut(300, function(){
                    // remove the upload from the table
                    $(this).remove();
                });
            }

            // trigger change event on form to update summary tab
            $('#create-job-form').trigger('change');
        });

        // an uploaded file is deleted
        $('#filelist').on('config:delete-upload', function(e){
            var selection = e.selection;

            // get the row being deleted.
            var $tr = $(this).find('tr#' + selection.uid);
            // decrement the number of uploaded files
            filesSelected -= 1;

            // reset the upload ui
            resetUploadConfigTab('success');

            // clear the selected files list
            var $fileupload = $('#fileupload');
            $fileupload.val('');

            // clear configuration hidden inputs
            $('input#preset').val('');

            // re-enable this config_type in the select combo
            var config_type = $tr.find('td').eq(1).html();
            var $option = $('option[value="' + config_type + '"]');
            $option.prop('disabled', false);

            /*
             * Re-enable the HDM feature selection tree.
             */
            if (config_type === 'PRESET') {
                $(document).trigger({type: 'preset:deselected', source: 'config-upload'});
            }

            // remove the config form input value
            var config_type_lwr = config_type.toLowerCase();
            $('input#' + config_type_lwr).val();

            // get number of configuration files in the table
            var configs = $('#filelist tr.config').length;
            if (configs == 1) {
                // remove the row and hide the table
                $tr.fadeOut(300, function(){
                    // remove the upload from the table
                    $(this).remove();
                    // hide the file list
                    $('#filelist').css('display', 'none');
                    // trigger change event on form when config deleted
                    $('#create-job-form').trigger('change');
                });
            }
            else {
                // just remove the deleted row
                $tr.fadeOut(300, function(){
                    $(this).remove();
                    // trigger change event on form when config deleted
                    $('#create-job-form').trigger('change');
                });
            }

            // update the summary tab
            $('table#summary-configs').trigger({type: 'config:removed', selection: selection});

            // trigger max files check
            $(document).trigger({type: 'config:checkmaxfiles', filesSelected: filesSelected});
        });


        $(document).on('config:checkmaxfiles', function(e){
            var maxFiles = 1;
            var filesSelected = e.filesSelected;
            if (filesSelected >= maxFiles) {
                $('input#filename').prop('disabled', true);
                $('select#config_type').prop('disabled', true);
                $('input#publish_config').prop('disabled', true);
                $('#select-file').addClass('disabled');
                $('button#select-config').prop('disabled', true);
            }
            else {
                // re-enable the fields
                $('input#filename').prop('disabled', false);
                $('select#config_type').prop('disabled', false);
                $('input#publish_config').prop('disabled', false);
                $('#select-file').removeClass('disabled');
                $('button#select-config').prop('disabled', false);
                $('input#feature_save').prop('disabled', false);
                $('input#feature_pub').prop('disabled', false);
            }
        });
    }

    /*
     * Updates the form with the uploaded config ids
     */
    function updateConfigInputs(selection){
        var uid = selection.uid;
        switch (selection.config_type){
            case "PRESET":
                $('option#select-preset').prop('disabled', true);
                $('input#preset').val(uid);
                break;
            case "TRANSLATION":
                $('option#select-translate').prop('disabled', true);
                $('input#translation').val(uid);
                break;
            case "TRANSFORM":
                $('option#select-transform').prop('disabled', true);
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

        // re-enabled config browser button
        $('button#select-config').prop('disabled', false);

        // reset the fields.
        $('input#filename').val('');
        $('input#filename').prop('disabled', false);
        $('option#select-message').prop('selected', true);
        $('input#publish_config').prop('disabled', false);
        $('input#publish_config').prop('checked', false);

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
     * Initialize the UI popovers.
     */
    function initPopovers() {
        $('#create-tab').popover({
            content: gettext("Select the area on the Map for export and enter the Name, Description and Event"),
            trigger: 'hover',
            delay: {show: 0, hide: 100},
            placement: 'top'
        });
        $('#formats-tab').popover({
            //title: 'Select Formats',
            content: gettext("Select one or more file formats for export"),
            trigger: 'hover',
            delay: {show: 0, hide: 100},
            placement: 'top'
        });
        $('#features-tab').popover({
            //title: 'Select Formats',
            content: gettext("Expand and select feature tags from the HDM or OSM tree list for export"),
            trigger: 'hover',
            delay: {show: 0, hide: 100},
            placement: 'top'
        });
        $('#upload-tab').popover({
            //title: 'Select Formats',
            content: gettext("Upload or select a preset file. Save and/or publish"),
            trigger: 'hover',
            delay: {show: 0, hide: 100},
            placement: 'top'
        });
        $('#summary-tab').popover({
            //title: 'Select Formats',
            content: gettext("Summary of the export settings. Select “Create Export” to start the export"),
            trigger: 'hover',
            delay: {show: 0, hide: 100},
            placement: 'top'
        });
        $('input#filename').popover({
            //title: 'Select Formats',
            content: "Give the selected Preset file a name",
            trigger: 'hover',
            delay: {show: 0, hide: 100},
            placement: 'top'
        });
        $('label[for="publish_config"]').popover({
            //title: 'Select Formats',
            content: gettext("Publish the preset file to the global storage for everyone to access"),
            trigger: 'hover',
            delay: {show: 0, hide: 100},
            placement: 'top'
        });
        $('#select-file').popover({
            //title: 'Select Formats',
            content: gettext("Find and upload a preset file from desktop"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'top'
        });
        $('button#select-config').popover({
            //title: 'Select Formats',
            content: gettext("Find and select preset file from the store"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'top'
        });
        $('label[for="feature_save"]').popover({
            //title: 'Select Formats',
            content: gettext("Save the feature tag selection to your personal preset storage"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'top'
        });
        $('label[for="feature_pub"]').popover({
            //title: 'Select Formats',
            content: gettext("Publish the feature tag selection to the global preset storage for everyone to access"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'top'
        });
        $('label[for="published"]').popover({
            //title: 'Select Formats',
            content: gettext("Publish the export to the global exports for everyone to access"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'top'
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
