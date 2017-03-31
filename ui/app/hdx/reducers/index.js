import { reducer as reduxFormReducer } from 'redux-form';
import {exportModeReducer, exportAoiInfoReducer, exportInfoReducer, stepperReducer} from './exportsReducer';
import {invalidDrawWarningReducer} from './drawToolBarReducer';
import {zoomToSelectionReducer, resetMapReducer} from './AoiInfobarReducer.js';
import {getGeonamesReducer} from './searchToolbarReducer.js';
import {toolbarIconsReducer, showImportModalReducer, importGeomReducer} from './mapToolReducer';
import {getHdxReducer} from './hdxReducer';

export default {
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
};
