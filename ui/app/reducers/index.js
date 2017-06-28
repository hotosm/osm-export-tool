import { reducer as reduxFormReducer } from 'redux-form';
import {exportModeReducer, exportRunsReducer, exportListReducer, exportAoiInfoReducer, exportInfoReducer, overpassTimestampReducer } from './exportsReducer';
import {invalidDrawWarningReducer} from './aoi/drawToolBarReducer';
import {zoomToSelectionReducer, resetMapReducer} from './aoi/AoiInfobarReducer.js';
import {getGeonamesReducer} from './aoi/searchToolbarReducer.js';
import {toolbarIconsReducer, showImportModalReducer, importGeomReducer} from './aoi/mapToolReducer';
import {configurationsReducer} from './configurationsReducer';
import {getHdxReducer} from './hdxReducer';

export default {
  // short hand property names
  mode: exportModeReducer,
  aoiInfo: exportAoiInfoReducer,
  zoomToSelection: zoomToSelectionReducer,
  resetMap: resetMapReducer,
  geonames: getGeonamesReducer,
  invalidDrawWarning: invalidDrawWarningReducer,
  toolbarIcons: toolbarIconsReducer,
  showImportModal: showImportModalReducer,
  importGeom: importGeomReducer,
  form: reduxFormReducer,
  hdx: getHdxReducer,
  exportInfo: exportInfoReducer,
  exportRuns: exportRunsReducer,
  exportList: exportListReducer,
  configurations: configurationsReducer,
  overpassLastUpdated: overpassTimestampReducer
};
