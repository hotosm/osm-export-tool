jobs = {};
jobs.list = (function(){
    var map;
    var job_extents;
    var job_extents_source;
    var scaleLine;
    var attribution;
    var bbox;
    var filtering = false;
    var searchForm = $('form#search');

    // SHOULD NOT NEED THIS IN OL3
    /*
     * Override unselect so hidden features don't get reset
     * with the 'default' style on unselect.
     */
    // OpenLayers.Control.SelectFeature.prototype.unselect = function(feature){
    //     var layer = feature.layer;
    //     if (feature.renderIntent == 'hidden') {
    //         OpenLayers.Util.removeItem(layer.selectedFeatures, feature);
    //         layer.events.triggerEvent("featureunselected", {feature: feature});
    //         this.onUnselect.call(this.scope, feature);
    //     }
    //     else {
    //         // Store feature style for restoration later
    //         this.unhighlight(feature); // resets the renderIntent to 'default'
    //         OpenLayers.Util.removeItem(layer.selectedFeatures, feature);
    //         layer.events.triggerEvent("featureunselected", {feature: feature});
    //         this.onUnselect.call(this.scope, feature);
    //     }
    // }


    /*
     * Handle stickiness of map on window scroll
     */
    var stickyTop = $('#map-column').offset().top;
    $(window).scroll(function(){
        var windowTop = $(window).scrollTop();
        // only make sticky on larger screens
        if (stickyTop < windowTop && $(window).width() > 992) {
            $('#map-column').css({
                position: 'fixed',
                top: 0,
                right: 0
            });
        }
        else {
            $('#map-column').css({
                position: 'relative',
            });
        }

    });

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


        //***** OPENLAYERS 2 CODE COMMENTED OUT THROUGHOUT FILE ************
        //var maxExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");
        //var mapOptions = {
                //displayProjection: new OpenLayers.Projection("EPSG:4326"),
                //controls: [new OpenLayers.Control.Attribution(),
                //          new OpenLayers.Control.ScaleLine()],

                //maxExtent is no longer in OL3, just extent
                //maxExtent: maxExtent,
                //cant find scales to set in OL3
                //scales:[500000,350000,250000,100000,25000,20000,15000,10000,5000,2500,1250],
                //units: 'm',
                //sphericalMercator: true,
                //noWrap: true // don't wrap world extents
        //}
        //map = new OpenLayers.Map('list-export-map', {
        //    options: mapOptions
        //});

        // restrict extent to world bounds to prevent panning..
        //map.restrictedExtent = new OpenLayers.Bounds(-180,-90,180,90).transform("EPSG:4326", "EPSG:3857");

        // add base layers
        // var osm = new OpenLayers.Layer.OSM("OpenStreetMap");
        // osm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        // map.addLayer(osm);
        // map.zoomToMaxExtent();

        //var zoomLevels = [500000,350000,250000,100000,25000,20000,15000,10000,5000,2500,1250];

        //add base layers
        var osm = new ol.layer.Tile({
            source: new ol.source.OSM()
        });

        map = new ol.Map({
            target: 'list-export-map',
            layers: [osm],
            view: new ol.View({
                projection: 'EPSG:3857',
                extent: [-20037508.34,-20037508.34, 20037508.34, 20037508.34],
                center: [0, 0],
                zoom: 2,
                maxZoom: 18,
            })
        });

        scaleLine = new ol.control.ScaleLine();
        map.addControl(scaleLine);

        attribution = new ol.control.Attribution();
        map.addControl(attribution);
        
        var defaultStyle = new ol.style.Style({
            fill: new ol.style.Fill({
                color: '#D73F3F',
                opacity: 0.1,
            }),
            stroke: new ol.style.Stroke({
                color: '#D73F3F',
                width: 3.5,
            })
        });

        var selectStyle = new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'blue',
                opacity: 0.1,
            }),
            stroke: new ol.style.Stroke({
                color: 'blue',
                width: 3.5,
            })
        });

        var hiddenStyle = new ol.style.Style({
            display: 'none',
            zIndex: -1
        });

        job_extents_source = new ol.source.Vector();

        job_extents = new ol.layer.Vector({
            name: 'Job Extents',
            source: job_extents_source,
            style: defaultStyle,
        });
        map.addLayer(job_extents);

        // job_extents = new OpenLayers.Layer.Vector('extents', {
        //     displayInLayerSwitcher: false,
        //     styleMap: getExtentStyles()
        // });
        // add export extents to map

        //map.addLayer(job_extents);

        /* required to fire selection events on bounding boxes */
        // var selectControl = new OpenLayers.Control.SelectFeature(job_extents,{
        //     id: 'selectControl'
        // });
        // map.addControl(selectControl);
        // selectControl.activate();



        var selectControl = new ol.interaction.Select({
            style: selectStyle
        });
        map.addInteraction(selectControl);

        var features = selectControl.getFeatures();
        job_extents_source.addFeatures(features);

        //openlayers 3 doesn't have onclick for vectors.
        //Need to add an onclick to the map and check for vectors around the pixel that was clicked.
        map.on("click", function(e) {
            map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
                //check for feature close by, then fire off selected event to change style and list as shown below in old OL2 code
                if (layer == job_extents) {
                    var uid = feature.data.uid;
                    if ($('tr#' + uid).css('background-color') == '#FFF'){
                        $('tr#' + uid).css('background-color', '#E8E8E8');
                    }
                    else {
                        $('tr#' + uid).css('background-color', '#FFF');
                    }
                }
            });
        })

        //featureover event needs to be like this.  Might take care of featureout as well.
        $(map.getViewport()).on('mousemove', function(e) {
            if ($('#feature-popup').css('display') == 'block') {
                $('#feature-popup').css('display', 'none');
            }
            var pixel = map.getEventPixel(e.originalEvent);
            var hit = map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                if (layer == job_extents) {
                    return true;
                }
                else {
                    return false;
                }
            });
            if (hit) {
                $popup = $('#feature-popup');
                $popup.css('display', 'block');
            } 
        });

        //OL3 double click handler:
        map.on('dblclick', function(evt) {
            var feature = map.forEachFeatureAtPixel(evt.pixel,
                function(feature, layer) {
                    if(layer == job_extents) {
                        var uid = feature.attributes.uid;
                        window.location.href = '/exports/' + uid;
                    }
                });
        });


        /*
         * OLD OL2 code...Feature selection and hover events
         */
        // job_extents.events.register("featureselected", this, function(e){
        //     var uid = e.feature.data.uid;
        //     $('tr#' + uid).css('background-color', '#E8E8E8');
        // });

        // job_extents.events.register("featureunselected", this, function(e){
        //     var uid = e.feature.data.uid;
        //     $('tr#' + uid).css('background-color', '#FFF');
        // });

        // job_extents.events.register('featureover', this, function(e){
        //     $popup = $('#feature-popup');
        //     $popup.css('display', 'block');
        // });

        // job_extents.events.register('featureout', this, function(e){
        //     $('#feature-popup').css('display', 'none');
        // });


        /*
         * OL2 Double-click handler.
         * Does redirection to export detail page on feature double click.
         */
        // var dblClickHandler = new OpenLayers.Handler.Click(selectControl,
        //         {
        //             dblclick: function(e){
        //                 var feature = this.layer.selectedFeatures[0];
        //                 var uid = feature.attributes.uid;
        //                 window.location.href = '/exports/' + uid;
        //             }
        //         },
        //         {
        //             single: false,
        //             double: true,
        //             stopDouble: true,
        //             stopSingle: false
        //         }
        // )
        // dblClickHandler.activate();

        // add filter selection layer
        bboxSource = new ol.source.Vector()
        bbox = new ol.layer.Vector({
            name: 'Filter',
            source: bboxSource,
            style: new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: [0, 0, 255, 1]
                })
            })
        });
        map.addLayer(bbox);


        // add a draw feature control for bbox selection.
        // var box = new OpenLayers.Control.DrawFeature(bbox, OpenLayers.Handler.RegularPolygon, {
        //    handlerOptions: {
        //       sides: 4,
        //       snapAngle: 90,
        //       irregular: true,
        //       persist: true
        //    }
        // });
        // map.addControl(box);

        var dragBox = new ol.interaction.DragBox({
            condition: ol.events.condition.primaryAction,
        });

        var translate;

        dragBox.on('boxend', function(e){
            var dragFeature = new ol.Feature({
                geometry: dragBox.getGeometry()
            });
            bboxSource.addFeature(dragFeature);
            map.removeInteraction(dragBox);
            translate = new ol.interaction.Translate({
                features: new ol.Collection([dragFeature])
            });

            var bounds = dragFeature.getGeometry().getExtent();
            filtering = true;
            setBounds(bounds);
            map.getView().fit(bounds, map.getSize());

            map.addInteraction(translate);
            translate.on('translateend', function(e){
                var bounds = dragFeature.getGeometry().getExtent();
                filtering = true;
                setBounds(bounds);
                map.getView().fit(bounds, map.getSize());
            });
        });
        

        // // add a transform control to enable modifications to bounding box (drag, resize)
        // var transform = new OpenLayers.Control.TransformFeature(bbox, {
        //    rotate: false,
        //    irregular: true,
        //    renderIntent: "transform",
        // });

        // // listen for selection box being added to bbox layer
        // box.events.register('featureadded', this, function(e){
        //     // get selection bounds
        //     bounds = e.feature.geometry.bounds.clone();

        //     // clear existing selection features
        //     bbox.removeAllFeatures();
        //     box.deactivate();

        //     // add a bbox feature based on user selection
        //     var feature = new OpenLayers.Feature.Vector(bounds.toGeometry());
        //     bbox.addFeatures(feature);

        //     // enable bbox modification
        //     transform.setFeature(feature);

        //     // filter the results by bbox
        //     filtering = true;
        //     setBounds(bounds);
        //     map.zoomToExtent(bbox.getDataExtent());

        // });

        // // filter results after bbox is moved / modified
        // transform.events.register("transformcomplete", this, function(e){
        //     var bounds = e.feature.geometry.bounds.clone();
        //     // filter the results by bbox
        //     filtering = true;
        //     setBounds(bounds);
        // });

        // // add the transform control
        // map.addControl(transform);

        // handles click on filter area button
        $("#filter-area").bind('click', function(e){
            /*
             * activate the draw box control
             */
            //bbox.removeAllFeatures();
            //transform.unsetFeature();
            //box.activate();
            map.removeInteraction(translate);
            bboxSource.clear();
            map.addInteraction(dragBox);
        });

        // map.setLayerIndex(bbox, 0);
        // map.setLayerIndex(job_extents, 100);

        // // clears the search selection area
        $('#clear-filter').bind('click', function(e){
            /*
             * Unsets the bounds on the form and
             * remove features and transforms
             */
            if (filtering) {
                // clear the filter extents
                filtering = false;
                map.removeInteraction(translate);
                //bbox.removeAllFeatures();
                bboxSource.clear();
                //box.deactivate();
                //transform.unsetFeature();
                // reset the bounds and reload default search results.
                $('input#bbox').val('-180,-90,180,90');
                runSearch();
            }
        });

        /*
         * Reset the map to the job extents.
         */
        $('#reset-map').bind('click', function(e){
            if(job_extents_source.getFeatures().length > 0) {
                map.getView().fit(job_extents.getExtent(), map.getSize());
            }
            else {
                zoomtoextent()
            }
        });

    }

    function zoomtoextent() {
        var extent = [-20037508.34,-20037508.34, 20037508.34, 20037508.34];
        map.getView().fit(extent, map.getSize());
    }

    /*
     * get the style map for the filter bounding box.
     */

    // function getTransformStyleMap(){
    //     return new OpenLayers.StyleMap({
    //                 "default": new OpenLayers.Style({
    //                     fillColor: "blue",
    //                     fillOpacity: 0.05,
    //                     strokeColor: "blue",
    //                     graphicZIndex : 1,
    //                 }),
    //                 // style for the select extents box
    //                 "transform": new OpenLayers.Style({
    //                     display: "${getDisplay}",
    //                     cursor: "${role}",
    //                     pointRadius: 4,
    //                     fillColor: "blue",
    //                     fillOpacity: 1,
    //                     strokeColor: "blue",
    //                     graphicZIndex : -1,
    //                 },
    //                 {
    //                     context: {
    //                         getDisplay: function(feature) {
    //                             // hide the resize handles except at the south-east corner
    //                             return  feature.attributes.role === "n-resize"  ||
    //                                     feature.attributes.role === "ne-resize" ||
    //                                     feature.attributes.role === "e-resize"  ||
    //                                     feature.attributes.role === "s-resize"  ||
    //                                     feature.attributes.role === "sw-resize" ||
    //                                     feature.attributes.role === "w-resize"  ? "none" : ""
    //                         }
    //                     }
    //                 })
    //             });
    // }


    /**
     * Returns the styles for job extent display.
     */
    function getExtentStyles(){
        var defaultStyle = new ol.style.Style({
            fill: new ol.style.Fill({
                color: '#D73F3F',
                opacity: 0.1,
            }),
            stroke: new ol.style.Stroke({
                color: '#D73F3F',
                width: 3.5,
            })
        });

        var selectStyle = new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'blue',
                opacity: 0.1,
            }),
            stroke: new ol.style.Stroke({
                color: 'blue',
                width: 3.5,
            })
        });

        var hiddenStyle = new ol.style.Style({
            display: 'none',
            zIndex: -1
        });

        // default style for export extents
        // var defaultStyle = new OpenLayers.Style({
        //     strokeWidth: 3.5,
        //     strokeColor: '#D73F3F',
        //     fillColor: '#D73F3F',
        //     fillOpacity: 0.1,
        //     //graphicZIndex : 50,
        // });
        // // export extent selection style
        // var selectStyle = new OpenLayers.Style({
        //     strokeWidth: 3.5,
        //     strokeColor: 'blue',
        //     fillColor: 'blue',
        //     fillOpacity: 0.1,
        //     //graphicZIndex : 40,
        // });
        
        
        // var hiddenStyle = new OpenLayers.Style({
        //     display: 'none'
        // });


        // TODO: There is not a style map in OL3.  Need to figure out how to account for this...
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
        $.ajax({
            url: url,
            cache: false,
        })
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
                // var selectControl = map.getControlsBy('id','selectControl')[0];
                var selectControl;
                map.getInteractions().forEach(function(interaction) {
                    if(interaction instanceof ol.interaction.Select) {
                        selectControl = interaction;
                    }
                })
                if (selectControl) {
                    var uid = $(e.target).attr('id');
                    for(var f=0; f < job_extents_source.getFeatures().length; f++){
                        var feature = job_extents_source.getFeatures()[f];
                        if(feature.getProperties().uid === uid){;
                            var visible = feature.getStyle().getZIndex();
                            if (visible === -1) {
                                // feature.renderIntent = 'hidden';
                                // selectControl.unselect(feature);
                                selectControl.getFeatures().remove(feature);
                                feature.setStyle(getExtentStyles.hidden);
                                //job_extents.redraw();
                                $('tr#' + uid).addClass('warning');
                            }
                            else {
                                //feature.renderIntent = 'default';
                                feature.setStyle(getExtentStyles.default);
                                $('tr#' + uid).removeClass('warning');
                                //job_extents.redraw();
                            }
                       }
                    }
                }
                $(this).toggleClass('glyphicon-eye-open glyphicon-eye-close');
            });
            $('span.zoom-feature').on('click', function(e){
                var uid = $(e.target).attr('data-zoom');
                for(var f=0; f < job_extents_source.getFeatures().length; f++){
                    var feature = job_extents_source.getFeatures()[f];
                    if(feature.getProperties().uid === uid){;
                        var bounds = feature.getGeometry().getExtent();
                        map.getView().fit(bounds, map.getSize());

                   }
                }
            });

            // clear the existing export extent features and add the new ones..
            job_extents_source.clear();
            $.each(data, function(idx, job){
                 var extent = job.extent;
                 var geojson = new ol.format.GeoJSON();
                 var feature = geojson.readFeatures(extent, {
                    'featureProjection': "EPSG:3857",
                    'dataProjection': "EPSG:4326"
                 });
                 job_extents_source.addFeatures(feature);
             });
            /*
             * Zoom to extents depending on whether
             * bbox filtering is applied or not..
             */
            if (filtering) {
                map.getView().fit(bboxSource.getExtent(), map.getSize());
            }
            else {
                var bounds = job_extents.getExtent();
                if (bounds) {
                    map.getView().fit(job_extents.getExtent(), map.getSize());
                }
                else {
                    // zoom to max if no results
                    zoomtoextent()
                }
            }
            // select bbox features based on row hovering
            $('table#jobs tbody tr').hover(
                // mouse in
                function(e){
                    // var selectControl = map.getControlsBy('id','selectControl')[0];
                    var selectControl;
                    map.getInteractions().forEach(function(interaction) {
                        if(interaction instanceof ol.interaction.Select) {
                            selectControl = interaction;
                        }
                    });
                    if (selectControl) {
                        var uid = $(this).attr('id');
                        for(var f=0; f < job_extents_source.getFeatures().length; f++){
                            var feature = job_extents_source.getFeatures()[f];
                            if(feature.getProperties().uid === uid && feature.getStyle().getZIndex != -1){
                                //selectControl.select(feature);
                                selectControl.getFeatures().push(feature);
                            }
                            else {
                                //selectControl.unselect(feature);
                                selectControl.getFeatures().remove(feature);
                            }
                        }
                    }
                },
                // mouse out
                function(e){
                    // var selectControl = map.getControlsBy('id','selectControl')[0];
                    var selectControl;
                    map.getInteractions().forEach(function(interaction) {
                        if(interaction instanceof ol.interaction.Select) {
                            selectControl = interaction;
                        }
                    });
                    if(selectControl) {
                        // selectControl.unselectAll();
                        selectControl.getFeatures().clear();
                    }
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
                        return '<a id="' + row.uid + '" href="/exports/' + row.uid + '">' + data + '</a>';
                    }
                },
                {data: 'description'},
                {data: 'event'},
                {
                    data: 'created_at',
                    render: function(data, type, row){
                        return moment(data).format('YYYY-MM-DD');
                    }
                },
                /*{data: 'region.name'},*/
                {
                    data: 'region',
                    render: function(data, type, row){
                        return row.region == undefined ? '' : row.region.name;
                    }
                },
                {data: 'owner'},
                {
                    data: 'published',
                    orderable:false,
                    render: function(data, type, row){
                        var published = row.published;
                        var owner = $('span#user').text();
                        var $div = $('<div>');
                        var $toggleSpan = $('<span id="' + row.uid + '" class="toggle-feature glyphicon glyphicon-eye-open" data-toggle="tooltip"></span>');
                        var $pubSpan = $('<span class="glyphicon"></span>');
                        $div.append($pubSpan);
                        if (owner === row.owner) {
                            var $userSpan = $('<span class="glyphicon glyphicon-user"></span>');
                            $div.append($userSpan);
                        }
                        else {
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
                        var $zoomSpan = $('<span class="fa fa-search-plus zoom-feature" data-zoom="' + row.uid + '"></span>');
                        $div.append($zoomSpan);

                        // return the html
                        return $div[0].outerHTML;
                    }
                }
            ],
            rowCallback: function(row, data, index){
                var user = $('span#user').text();
                var owner = user === data.owner ? 'me' : data.owner;
                var $pubSpan = $(row).find('.glyphicon-globe');
                var $unpubSpan = $(row).find('.glyphicon-time');
                var $featToggle = $(row).find('.toggle-feature');
                var $users = $(row).find('.fa-users');
                var $user = $(row).find('.glyphicon-user');
                var $zoomSpan = $(row).find('.fa-search-plus');
                if (data.published) {
                    $pubSpan.tooltip({
                        'html': true,
                        'title': gettext('Published export.')
                    });
                }
                else {
                    var expires = moment(data.created_at).add(2, 'days').format('hh a YYYY-MM-DD');
                    $unpubSpan.tooltip({
                        'html': true,
                        'title': gettext('Unpublished export') + '<br/>' + gettext('Expires: ') + expires
                    });
                }
                $users.tooltip({
                    'html': true,
                    'title': gettext('Created by ') + owner
                });
                $user.tooltip({
                    'html': true,
                    'title': gettext('Created by ') + owner
                });
                $featToggle.tooltip({
                    'html': true,
                    'title': gettext('click to toggle feature visibility')
                });
                $zoomSpan.tooltip({
                    'html': true,
                    'title': gettext('click to zoom')
                });
                $(row).find('td').eq(5).addClass('owner');
            }
           });
        // clear the empty results message on initial draw..
        $('td.dataTables_empty').html('');
    }

    /**
     * Initialize the start / end date pickers.
     */
    function initDatePickers(){
        moment.utc();
        $('#start-date').datetimepicker({
            showTodayButton: true,
            // show one month of exports by default
            defaultDate: moment().subtract(1, 'month').startOf('d'),
            format: 'YYYY-MM-DD HH:mm'
        });
        $('#end-date').datetimepicker({
            showTodayButton: true,
            // default end-date to now.
            defaultDate: moment().endOf('d'),
            format: 'YYYY-MM-DD HH:mm'
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
     *  -- NOT IMPLEMENTED YET --
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
        //bounds.transform('EPSG:3857', 'EPSG:4326');
        bounds = ol.proj.transformExtent(bounds, 'EPSG:3857', 'EPSG:4326');
        var xmin = numeral(bounds[0]).format(fmt);
        var ymin = numeral(bounds[1]).format(fmt);
        var xmax = numeral(bounds[2]).format(fmt);
        var ymax = numeral(bounds[3]).format(fmt);
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
            setTimeout(function(){
                runSearch();
            }, 450);
        });

        // run search on selection changes
        $('select').bind('change', function(e){
           runSearch();
        });

        // run search on user filtering state change
        $('input#user-check').bind('change', function(e){
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

        $('button#reset-form').on('click', function(e){
            $('input#search').val('');
            $('input#user-check').prop('checked', false).trigger('change');
            $('#start-date').data('DateTimePicker').date(moment().subtract(1, 'month').startOf('d'));
            $('#end-date').data('DateTimePicker').date(moment().endOf('d'));
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

