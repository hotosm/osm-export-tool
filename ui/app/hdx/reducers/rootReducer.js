import {combineReducers} from 'redux'
import { reducer as reduxFormReducer } from 'redux-form'
import {exportJobsReducer, exportModeReducer, exportBboxReducer, exportAoiInfoReducer, exportInfoReducer, stepperReducer} from './exportsReducer';
import {invalidDrawWarningReducer} from './drawToolBarReducer';
import {zoomToSelectionReducer, resetMapReducer} from './AoiInfobarReducer.js';
import {getGeonamesReducer} from './searchToolbarReducer.js';
import {toolbarIconsReducer, showImportModalReducer, importGeomReducer} from './mapToolReducer';
import {getHdxReducer} from './hdxReducer';


const rootReducer = combineReducers({
    // short hand property names
    mode: exportModeReducer,
    aoiInfo: exportAoiInfoReducer,
    exportInfo: exportInfoReducer,
    zoomToSelection: zoomToSelectionReducer,
    resetMap: resetMapReducer,
    geonames: getGeonamesReducer,
    showInvalidDrawWarning: invalidDrawWarningReducer,
    toolbarIcons: toolbarIconsReducer,
    showImportModal: showImportModalReducer,
    importGeom: importGeomReducer,
    stepperNextEnabled: stepperReducer,
    form: reduxFormReducer,
    hdx: getHdxReducer
});

export default rootReducer;
