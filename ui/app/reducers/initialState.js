export default {
    aoiInfo: {
        geojson: {},
        geomType: null,
        title: null,
        description: null,
    },
    mode: 'DRAW_NORMAL',
    showInvalidDrawWarning: false,
    showImportModal: false,
    zoomToSelection: {
        click: false
    },
    resetMap: {
        click: false
    },
    geonames: {
        fetching: false,
        fetched: false,
        geonames: [],
        error: null,
    },
    hdx: {
      fetching: false,
      fetched: false,
      exportRegions: {},
      error: null,
    },
    exportInfo:null,
    exportRuns:[],
    exportList:[],
    importGeom: {
        processing: false,
        processed: false,
        geojson: {},
        error: null,
    },
    toolbarIcons: {
        box: "DEFAULT",
        free: "DEFAULT",
        mapView: "DEFAULT",
        import: "DEFAULT",
        search: "DEFAULT",
    },
    runsList: {
        fetching: false,
        fetched: false,
        runs: [],
        error: null,
    },
    jobSubmit: {
        fetching: false,
        fetched: false,
        jobuid: '',
        error: null,
    },
    configurations: [],
    overpassLastUpdated: null
}
