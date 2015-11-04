configurations = {};
configurations.list = (function(){
    var map;
    var job_extents;
    var bbox;
    var filtering = false;
    var searchForm = $('form#search');

    return {
        main: function(){

            initUploadForm();
            initPopovers();
            initDataTable();
            initDatePickers();
            initSearch();
            runSearch();
        },
    }

    /*
     * Initialize the configuration upload form.
     */
    function initUploadForm(){

        // track the number of uploaded files.
        var numUploadedFiles = 0;

        /*
         * Set up form validation.
         */
        $('#create-configuration-form').formValidation({
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
                'filename': {
                    validators: {
                        notEmpty: {
                            message: gettext('The preset name is required and cannot be empty.')
                        },
                    }
                },
                /*
                'config_type': {
                    validators: {
                        notEmpty: {
                            message: 'The configuration type is required and cannot be empty.'
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
            $('#btn-submit-config').prop('disabled', 'false');
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

        // ----- CONFIGURATION UPLOAD ----- //

        /*
         * Validates the file upload tab.
         */
        function validateFileUploadForm() {
            var fv = $('#create-configuration-form').data('formValidation');// FormValidation instance

            // validate the form panel contents
            fv.validate();
            var isValid = fv.isValid();
            if ((isValid === false || isValid === null)){
                // stay on this tab
                $('button#upload').prop('disabled', true);
                return false;
            }
            $('button#upload').prop('disabled', false);

            // reset validation on fields
            fv.resetField($('input#filename'));
            //fv.resetField($('select#config_type'));

            return true;
        }

        $('#select-file').on('click', function(e){
            if (!validateFileUploadForm()) {
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
            //$('select#config_type').prop('disabled', true);
            $('input#publish_config').prop('disabled', true);
            var $filelist = $('#filelist');
            var $select = $('.btn-file');
            var $upload = $('button#upload');
            $upload.prop('disabled', false);
            //var type = $('option:selected').val();
            var type = $('input#config_type').val();
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
                //$('select#config_type').prop('disabled', false);
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
                //$('option#select-message').prop('selected', true);
                $('input#publish_config').prop('checked', false);
                // reset the input field validation
                var fv = $('#create-configuration-form').data('formValidation');
                fv.resetField($('input#filename'));
                fv.resetField($('select#config_type'));
                $('#create-configuration-form').trigger('change');
            });
        });

        /*
         * Handle config file upload.
         */
        $('button#upload').bind('click', function(e){
            if (!validateFileUploadForm()){
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
            //var config_type = $('select#config_type').val();
            var config_type = $('input#config_type').val();
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
                    // get number of selected files in the table
                    var uploaded = $('#filelist tr').length  -1; // exclude <th>
                    if (uploaded == 1) {
                        // remove the last entry in the table
                        $('#filelist tr').last().remove();
                        $('#filelist').css('display', 'none');
                    }
                    else {
                        // just remove this row..
                        $('#filelist tr').last().remove();
                    }
                    // reset the form for more file uploads..
                    resetUploadConfigTab(textStatus);

                    // add the new configuration to the table
                    var $table = $('table#configurations').DataTable();
                    var rowNode = $table
                            .row.add(result)
                            .draw()
                            .node();
                    $(rowNode).css('background-color','#dff0d8');
                    $(rowNode).animate({'background-color': 'white'}, 2000);
                    runSearch();
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


            // re-enable the fields
            $('input#filename').prop('disabled', false);
            $('select#config_type').prop('disabled', false);
            $('input#publish_config').prop('disabled', false);
            $('#select-file').prop('disabled', false);

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

    }


    /**
     * Lists the configurations.
     *
     * url: the search endpoint.
     *
     */
    function listConfigurations(url){
        if (!url) {
            // default search endpoint
            url = Config.CONFIGURATION_URL;
        }
        $.ajax({
            url: url,
            cache: false,
        })
        .done(function(data, textStatus, jqXHR){
            // generate pagination on UI
            paginate(jqXHR);

            // clear the existing data on results table and add new page
            var tbody = $('table#configurations tbody');
            var table = $('table#configurations').DataTable();
            table.clear();
            table.rows.add(data).draw();
            $('div#spinner').css('display', 'none');
            $('div#search-config').css('display', 'block').fadeIn(1500);
            // set message if no results returned from this url..
            $('td.dataTables_empty').html('No configuration files found.');

            // handle delete events on table rows..
            $('.delete-file').bind('click', function(e){
                var that = $(this);
                var data = new FormData();
                data.append('_method', 'DELETE');
                var uid = e.target.id;
                console.log(uid);
                $.ajax({
                    url: Config.CONFIGURATION_URL + '/' + uid,
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
                        // handle deletion on the table..
                        var row = table.row('#' + uid);
                        $(row.node()).css('background-color', '#f2dede');
                        $(row.node()).fadeOut(400, function(){
                            runSearch();
                        });
                        row.remove();
                    }
                });
            });
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
            paginate.append('<li id="prev" data-url="' + url + '"><a href="#"><span class="glyphicon glyphicon-chevron-left"/>' + gettext(' Prev') + '</a></li>&nbsp;');
            $('li#prev').on('click', function(){
                var u = this.getAttribute('data-url');
                u == 'undefined' ? listConfigurations() : listConfigurations(u);
            });
        }

        if (a) {
            var url = a.split(';')[0].trim();
            url = url.slice(1, url.length -1);
            var rel = a.split(';')[1].split('=')[1];
            rel = rel.slice(1, rel.length -1);
            if (rel == 'prev') {
                paginate.append('<li id="prev" data-url="' + url + '"><a href="#"><span class="glyphicon glyphicon-chevron-left"/>' + gettext('Prev') + '</a></li>');
                $('li#prev').on('click', function(){
                    var u = this.getAttribute('data-url');
                    u == 'undefined' ? listConfigurations() : listConfigurations(u);
                });
            }
            else {
                paginate.append('<li id="next" data-url="' + url + '"><a href="#">Next <span class="glyphicon glyphicon-chevron-right"/></a></li>');
                $('li#next').on('click', function(){
                    var u = this.getAttribute('data-url');
                    u == 'undefined' ? listConfigurations() : listConfigurations(u);
                });
            }
        }
    }

    /*
     * Initialize the configuration list data table.
     */
    function initDataTable(){
        $('table#configurations').DataTable({
            paging: false,
            info: false,
            filter: false,
            searching: false,
            ordering: true,
            rowId: 'uid',
            "order": [[ 2, "desc" ]],
            columns: [
                {data: 'name'},
                {data: 'config_type'},
                {
                    data: 'created',
                    render: function(data, type, row){
                        return moment(data).format('YYYY-MM-DD');
                    }
                },
                {
                    data: 'filename',
                    render: function(data, type, row){
                        return '<a href="' + row.upload + '" target="_blank">' + data + '</a>';
                    }
                },
                { data: 'owner'},
                {
                    data: 'published',
                    orderable:false,
                    render: function(data, type, row){
                        var published = row.published;
                        var owner = $('span#user').text();
                        var $div = $('<div>');
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
                            $pubSpan.addClass('glyphicon-minus-sign');
                        }
                        // return the html
                        return $div[0].outerHTML;
                    }
                },
                {
                    data: 'uid',
                    orderable:false,
                    render: function(data, type, row){
                        var user = $('span#user').text();
                        if (row.owner === user) {
                            return '<button title="Delete this configuration file" id="' + data + '" type="button" class="delete-file btn btn-danger btn-sm pull-right">' +
                                'Delete</button>';
                        }
                        else {
                            return '';
                        }
                    }
                }
            ],
            rowCallback: function(row, data, index){
                var user = $('span#user').text();
                var owner = user === data.owner ? 'me' : data.owner;
                var $pubSpan = $(row).find('.glyphicon-globe');
                var $unpubSpan = $(row).find('.glyphicon-minus-sign');
                var $users = $(row).find('.fa-users');
                var $user = $(row).find('.glyphicon-user');
                if (data.published) {
                    $pubSpan.tooltip({
                        'html': true,
                        'title': gettext('Published preset')
                    });
                }
                else {
                    $unpubSpan.tooltip({
                        'html': true,
                        'title': gettext('Private preset')
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
            }
           });
        // clear the empty results message on initial draw..
        $('td.dataTables_empty').html('');
    }

    /**
     * Initialize the start / end date pickers.
     */
    function initDatePickers(){
        $('#start-date').datetimepicker({
            showTodayButton: true,
            // show one month of configurations by default
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

    /*
     * Search configurations.
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
            runSearch();
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
                $('input#published').val('');
                runSearch();
            } else {
                $('input#user').val('');
                //$('input#published').val('True');
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
        var url = Config.CONFIGURATION_URL + '?';
        url += searchForm.serialize();
        listConfigurations(url); // update results table
    }

    /*
     * Initialise UI popovers.
     */
    function initPopovers(){
        $('a#filter-toggle').popover({
            //title: 'Select Formats',
            content: gettext("Filter through all the preset files based on keywords in the search box and/or between a start and end date"),
            trigger: 'hover',
            delay: {show: 0, hide: 0},
            placement: 'right'
        });
        $('label[for="publish_config"]').popover({
            //title: 'Select Formats',
            content: gettext("Publish the preset file to the global store for everyone to access"),
            trigger: 'hover',
            delay: {show: 0, hide: 100},
            placement: 'top'
        });
        $('input#filename').popover({
            //title: 'Select Formats',
            content: gettext("Give the selected Preset file a name"),
            trigger: 'hover',
            delay: {show: 0, hide: 100},
            placement: 'top'
        });
    }

}());


$(document).ready(function() {
    // initialize the app..
    configurations.list.main();
});

