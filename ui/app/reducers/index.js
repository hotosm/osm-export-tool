import { reducer as reduxFormReducer } from 'redux-form';
import {exportModeReducer, exportAoiInfoReducer, exportInfoReducer, overpassTimestampReducer } from './exportsReducer';
import {invalidDrawWarningReducer} from './aoi/drawToolBarReducer';
import {zoomToSelectionReducer, resetMapReducer} from './aoi/AoiInfobarReducer.js';
import {getGeonamesReducer} from './aoi/searchToolbarReducer.js';
import {toolbarIconsReducer, showImportModalReducer, importGeomReducer} from './aoi/mapToolReducer';
import {getHdxReducer} from './hdxReducer';

export default {
  // short hand property names
  mode: exportModeReducer,
  aoiInfo: exportAoiInfoReducer,
  zoomToSelection: zoomToSelectionReducer,
  resetMap: resetMapReducer,
  geonames: getGeonamesReducer,
  showInvalidDrawWarning: invalidDrawWarningReducer,
  toolbarIcons: toolbarIconsReducer,
  showImportModal: showImportModalReducer,
  importGeom: importGeomReducer,
  form: reduxFormReducer,
  hdx: getHdxReducer,
  exportInfo: exportInfoReducer,
  overpassTimestamp: overpassTimestampReducer
};
