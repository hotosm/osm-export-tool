configurations = {};
configurations.list = (function(){
    var map;
    var job_extents;
    var bbox;
    var filtering = false;
    var searchForm = $('form#search');
    var selections = [];

    return {
        main: function(){
            $('div#search-config').css('display','none');
            $('div#spinner').css('display','block');
            // initialize the results table
            initDataTable();
            // initialize the start / end date pickers
            initDatePickers();
            // initialize the selection handler
            initSelectionHandler();
            // listen for state changes on selected file list
            handleStateChanges();
            // initialize the search callback
            initSearch();
            // run the default search
            //runSearch();
        },
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

            // enable checkboxes on selections
            $(selections).each(function(idx, selection){
                $('input[id="' + selection.uid + '"]').prop('checked', true);
                toggleCheckboxes(selection, true);
            });

            // bind a listener to the selection checkboxes
            $('input[name="config"]').on('change', function(e){
                var isSelected = $(e.target).is(':checked');
                var uid = e.target.id;
                var type = e.target.getAttribute('data-type');
                var filename = e.target.getAttribute('data-filename');
                var published = e.target.getAttribute('data-published') === true ? 'Published' : 'Private';
                if (isSelected) {
                    var selection = {}
                    selection['uid'] = uid;
                    selection['config_type'] = type;
                    selection['filename'] = filename;
                    selection['published'] = published;
                    selections.push(selection);
                    toggleCheckboxes(selection, true);
                    if (type === 'PRESET') {
                        $(document).trigger({type: 'preset:selected', source: 'config-browser'});
                    }
                }
                else {
                    $(selections).each(function(idx, selection){
                        if (selection.uid === e.target.id) {
                            selections.splice(idx, 1);
                            toggleCheckboxes(selection, false);
                        }
                    });
                    if (type === 'PRESET') {
                        $(document).trigger({type: 'preset:deselected', source: 'config-browser'});
                    }
                }
            });
        });
    }

    /*
     * Toggles disabled state on configuration types
     * depending on what's currently selected.
     */
    function toggleCheckboxes(selection, disable){
        var type = selection.config_type;
        var uid = selection.uid;
        $('input[data-type="' + type + '"]')
            .each(function(i, input){
                if (disable) {
                    var inputUid = input.id;
                    if (inputUid != uid) {
                        $(input).prop('disabled', true);
                        $(input).closest('tr').css('opacity', .5);
                    }
                    else {
                        // leave the one currently selected enabled
                        $(input).prop('disabled', false);
                    }
                }
                else {
                    $(input).prop('disabled', false);
                    $(input).closest('tr').css('opacity', 1);
                }

        });
    }

    // handle user config selections
    function initSelectionHandler(){
        $('button#select').on('click', function(e){
            var $filelist = $('#filelist');
            // clear the list and add the new selections
            $filelist.find('tr[data-source="config-browser"]').each(function(idx, tr){
                var selection = getSelectionFromTR(tr);
                $filelist.trigger({type: 'config:removed', source: 'config-browser', selection: selection});
            });
            $(selections).each(function(idx, selection){
                $filelist.trigger({type: 'config:added', source: 'config-browser', selection: selection});
            });
            selections = [];
        });
    }

    // builds a selection object from an entry in the filelist.
    function getSelectionFromTR(tr){
        var selection = {};
        selection['uid'] = $(tr).attr('id');
        selection['filename'] = $(tr).attr('data-filename');
        selection['config_type'] = $(tr).attr('data-type');
        selection['published'] = $(tr).attr('data-published');
        return selection;
    }

    /*
     * Listens for state changes.
     * on selected file list.
     */
    function handleStateChanges(){

        /*
         * Handle events on dialog show.
         */
        $('#configSelectionModal').on('show.bs.modal', function(e){
            selections = [];
            $('table#filelist tr.config').each(function(idx, tr){
                var selection = getSelectionFromTR($(tr));
                selections.push(selection);
            });
            runSearch();
        });

        /*
         * Listen for remove events on the filelist and update
         * selections accordingly.
         */
        $('table#configurations').on('filelist:removed', function(e){
            $(selections).each(function(idx, selection){
                if (selection.uid === e.selection.uid) {
                    selections.splice(idx, 1);
                }
            });
            runSearch();
        });

        /*
         * Listen for configurations being added to the filelist
         * and update state on this.
         */
        $('table#configurations').on('config:added', function(e){
            selections.push(e.selection);
            toggleCheckboxes(e.selection, true);
        });

        $('table#configurations').on('config:removed', function(e){
            toggleCheckboxes(e.selection, false);
        });
    }

    /*
     * Creates the pagination links based on the Content-Range and Link headers.
     *
     * jqXHR: the ajax xhr
     */
    function paginate(jqXHR){

        // get the pagination ul
        var paginate = $('#pagination ul.pager');
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
            paginate.append('<li id="prev" data-url="' + url + '"><a href="#"><span class="glyphicon glyphicon-chevron-left"/> Prev</a></li>&nbsp;');
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
                paginate.append('<li id="prev" data-url="' + url + '"><a href="#"><span class="glyphicon glyphicon-chevron-left"/> Prev</a></li>');
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
                {data: 'owner'},
                {data: 'filename'},
                {
                    data: 'uid',
                    render: function(data, type, row){
                        var html = '<div class="checkbox">' +
                                        '<label>' +
                                            '<input id="' + row.uid + '" type="checkbox" ' +
                                                'data-type="' + row.config_type + '" ' +
                                                'data-filename="' + row.filename + '" ' +
                                                'data-published="' + row.published + '" ' +
                                                'name="config"/>' +
                                        '</label>' +
                                    '</div>';
                        return html
                    }
                }
            ]
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
        $('input#user-check').bind('click', function(e){
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

}());


$(document).ready(function() {
    // initialize the app..
    configurations.list.main();
});

