import React, { Component } from 'react';

import axios from 'axios';
import isEqual from 'lodash/isEqual';
import prettyBytes from 'pretty-bytes';
import { FormGroup, ControlLabel, FormControl, HelpBlock, Row, Col, Checkbox, Panel, Button, Table } from 'react-bootstrap';
import { Field, SubmissionError, formValueSelector, propTypes, reduxForm } from 'redux-form';
import { FormattedDate, FormattedRelative, FormattedTime, IntlMixin } from 'react-intl';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { push } from 'react-router-redux';
import Select from 'react-select';
import 'react-select/dist/react-select.css';
import yaml from 'js-yaml';

import { clickResetMap } from '../actions/AoiInfobarActions';
import { clearAoiInfo, updateAoiInfo } from '../actions/exportsActions';
import { createExportRegion as _createExportRegion, deleteExportRegion, getExportRegion, runExport, updateExportRegion as _updateExportRegion } from '../actions/hdxActions';
import styles from '../styles/HDXExportRegionForm.css';

const AVAILABLE_EXPORT_FORMATS = {
  shp: 'ESRI Shapefiles',
  geopackage: 'GeoPackage',
  garmin_img: 'Garmin .IMG',
  kml: '.KMZ'
};

const FORM_NAME = 'HDXExportRegionForm';

const createExportRegion = _createExportRegion(FORM_NAME);
const updateExportRegion = _updateExportRegion(FORM_NAME);

const form = reduxForm({
  form: FORM_NAME,
  onSubmit: (values, dispatch, props) => {
    console.log('Submitting form. Values:', values);

    if (props.aoiInfo.geomType == null) {
      throw new SubmissionError({
        _error: 'Please select an area of interest →'
      });
    }

    const exportFormats = Object.keys(AVAILABLE_EXPORT_FORMATS).filter(x => values[x]);

    if (exportFormats.length === 0) {
      throw new SubmissionError({
        export_formats: 'At least one data format is required.'
      });
    }

    let geom = props.aoiInfo.geojson;

    if (props.aoiInfo.geojson.geometry) {
      geom = props.aoiInfo.geojson.geometry;
    }

    if (props.aoiInfo.geojson.features) {
      geom = props.aoiInfo.geojson.features[0].geometry;
    }

    const formData = {
      ...values,
      export_formats: exportFormats,
      locations: (values.locations || []).map(x => x.value || x),
      the_geom: geom
    };

    if (values.id != null) {
      dispatch(updateExportRegion(values.id, formData));
    } else {
      dispatch(createExportRegion(formData));
    }
  },
  validate: values => {
    const errors = {};

    try {
      yaml.safeLoad(values.feature_selection);
    } catch (err) {
      errors.feature_selection = <pre>{err.message}</pre>;
      errors._error = errors._error || [];
      errors._error.push('Feature selection is invalid.');
    }

    return errors;
  }
});

const renderInput = ({ id, input, label, help, meta: { error }, ...props }) =>
  <FormGroup controlId={id || props.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{error && <p className={styles.error}>{error}</p>}{help}</HelpBlock>
  </FormGroup>;

const renderMultiSelect = ({ id, input, label, help, meta: { error }, ...props }) =>
  <FormGroup controlId={id || props.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <Select
      {...input}
      {...props}
      onBlur={() => input.onBlur(input.value)}
    />
    <FormControl.Feedback />
    <HelpBlock>{error && <p className={styles.error}>{error}</p>}{help}</HelpBlock>
  </FormGroup>;

const renderTextArea = ({id, label, input, data, meta: { error }, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl componentClass='textarea' {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

const renderSelect = ({id, label, input, data, meta: { error }, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl componentClass='select' {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

const renderCheckboxes = ({id, label, input, data, meta: { error }, description, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    {props.children}
    <FormControl.Feedback />
    <HelpBlock>{error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

const renderCheckbox = ({input, data, description, meta, ...props}) =>
  <Checkbox {...input} {...props}>{description}</Checkbox>;

const getTimeOptions = () => {
  const options = [];

  for (let i = 0; i < 24; i++) {
    options.push(<option key={i} value={i}>{i}:00 UTC</option>);
  }

  return options;
};

const getFormatCheckboxes = () =>
  Object.keys(AVAILABLE_EXPORT_FORMATS).map((k, i) =>
    <Field
      key={i}
      name={k}
      description={AVAILABLE_EXPORT_FORMATS[k]}
      component={renderCheckbox}
      type='checkbox'
    />);

const PendingDatasetsPanel = ({ datasetPrefix, error, featureSelection, handleSubmit, status, styles, submitting }) =>
  <Panel>
    This will immediately create {Object.keys(featureSelection).length} dataset{Object.keys(featureSelection).length === 1 ? '' : 's'} on HDX:
    <ul>
      {
        Object.keys(featureSelection).map((x, i) => (
          <li key={i}>
            <code>{datasetPrefix}_{x}</code>
          </li>
        ))
      }
    </ul>
    <Button bsStyle='primary' bsSize='large' type='submit' disabled={submitting} onClick={handleSubmit} block>
      {submitting ? 'Creating...' : 'Create Datasets + Schedule Export'}
    </Button>
    {error && <p className={styles.error}><strong>{error}</strong></p>}
    {status && <p className={styles.status}><strong>{status}</strong></p>}
  </Panel>;

const ExistingDatasetsPanel = ({ error, datasets, handleSubmit, status, styles, submitting }) =>
  <Panel>
    This will immediately update {datasets.length} dataset{datasets.length === 1 ? '' : 's'} on HDX.
    <Button bsStyle='primary' bsSize='large' type='submit' disabled={submitting} onClick={handleSubmit} block>
      {submitting ? 'Saving...' : 'Save + Sync to HDX'}
    </Button>
    {error && <p className={styles.error}><strong>{error}</strong></p>}
    {status && <p className={styles.status}><strong>{status}</strong></p>}
  </Panel>;

export class HDXExportRegionForm extends Component {
  static propTypes = {
    ...propTypes
  }

  mixins = [IntlMixin];

  state = {
    deleting: false,
    editing: false,
    featureSelection: {},
    running: false
  };

  getLastRun () {
    const exportRegion = this.exportRegion;

    if (exportRegion.last_run == null) {
      return 'Never';
    }

    return <FormattedRelative value={exportRegion.last_run} />;
  }

  getNextRun () {
    const exportRegion = this.exportRegion;

    if (exportRegion.next_run == null) {
      return 'Never';
    }

    return <FormattedRelative value={exportRegion.next_run} />;
  }

  loadLocationOptions () {
    return axios('https://data.humdata.org/api/3/action/group_list?all_fields=true')
      .then(rsp => this.setState({
        locationOptions: rsp.data.result
          .filter(x => x.state === 'active')
          .map(x => ({
            value: x.name,
            label: x.title
          }))
      }));
  }

  didReceiveRegion (exportRegion) {
    if (exportRegion == null) {
      return;
    }

    const { anyTouched, change, getExportRegion, updateAOI } = this.props;

    // NOTE: this also sets some form properties that we don't care about (but that show up in the onSubmit handler)
    if (!anyTouched) {
      // only update properties if they haven't been touched
      Object.entries(exportRegion).forEach(([k, v]) => change(k, v));

      exportRegion.export_formats.forEach(x => change(x, true));

      updateAOI(exportRegion.the_geom);
    }

    if (exportRegion.runs[0] != null && exportRegion.runs[0].status === 'RUNNING') {
      this.setState({
        running: true
      });

      if (this.runPoller == null) {
        this.runPoller = setInterval(() => getExportRegion(exportRegion.id), 15e3);
      }
    } else {
      this.setState({
        running: false
      });

      clearInterval(this.runPoller);
      this.runPoller = null;
    }

    console.log('Export region:', exportRegion);
  }

  componentDidMount () {
    const { clearAOI, getExportRegion, hdx: { exportRegions }, match: { params: { id } } } = this.props;

    if (id == null) {
      clearAOI();
    } else {
      // we're editing
      getExportRegion(id);

      this.setState({
        editing: true
      });
    }

    this.loadLocationOptions();

    this.didReceiveRegion(exportRegions[id]);
  }

  componentWillReceiveProps (props) {
    const { hdx: { exportRegions, statusCode }, match: { params: { id } }, showAllExportRegions } = props;

    if (this.props.hdx.statusCode !== statusCode) {
      switch (statusCode) {
        case 403:
          // TODO display a modal instead with a link to log in via OSM
          // window.location = '/';
          break;

        case 404:
          // TODO consider displaying a 404 page instead
          // showAllExportRegions();
          break;
      }
    }

    if (!isEqual(this.props.hdx.exportRegions[id], exportRegions[id])) {
      this.didReceiveRegion(exportRegions[id]);
    }

    if (this.props.hdx.exportRegions[id] != null && exportRegions[id] == null) {
      showAllExportRegions();
    }

    // TODO this would be cleaner if using reselect
    if (props.featureSelection !== this.props.featureSelection) {
      try {
        this.setState({
          featureSelection: yaml.safeLoad(props.featureSelection) || {}
        });
      } catch (err) {
        // noop; feature selection may be in the process of being edited
        console.warn(err);
      }
    }
  }

  get exportRegion () {
    const { hdx: { exportRegions }, match: { params: { id } } } = this.props;
    return exportRegions[id];
  }

  getRunRows () {
    return this.exportRegion.runs.slice(0, 10).map((run, i) => (
      <tr key={i}>
        <td>
          <a href={`/exports/${this.exportRegion.job.uid}#${run.uid}`}><FormattedDate value={run.run_at} /> <FormattedTime value={run.run_at} /></a>
        </td>
        <td>
          {run.status}
        </td>
        <td>
          {`00${Math.floor(run.elapsed_time / 60)}`.slice(-2)}:{`00${Math.round(run.elapsed_time % 60)}`.slice(-2)}
        </td>
        <td>
          {prettyBytes(run.size)}
        </td>
      </tr>
    ));
  }

  handleDelete = () => {
    this.setState({
      deleting: true
    });

    this.props.handleDelete(this.exportRegion.id);
  };

  handleRun = () => {
    this.setState({
      running: true
    });

    this.props.handleRun(this.exportRegion.id, this.exportRegion.job.uid);
  };

  render () {
    const { deleting, editing, featureSelection, locationOptions, running } = this.state;
    const { error, handleSubmit, hdx: { status }, submitting } = this.props;
    const exportRegion = this.exportRegion;
    const datasetPrefix = this.props.datasetPrefix || '<prefix>';
    const name = this.props.name || 'Untitled';

    return (
      <div className={styles.hdxForm}>
        <ol className='breadcrumb'>
          <li><Link to='/'>Export Regions</Link></li>
          <li className='active'>{name}</li>
        </ol>
        <form onSubmit={handleSubmit}>
          <h2>{editing ? 'Edit' : 'Create'} Export Region</h2>
          {this.props.hdx.error && <p><strong className={styles.error}>{this.props.hdx.status}</strong></p>}
          <Field
            name='name'
            type='text'
            label='Dataset Name'
            placeholder='Senegal'
            component={renderInput}
          />
          <hr />
          <Field
            name='dataset_prefix'
            type='text'
            label='Dataset Prefix'
            placeholder='hotosm_senegal'
            help={<div>Example: prefix <code>hotosm_senegal</code> results in datasets <code>hotosm_senegal_roads</code>, <code>hotosm_senegal_buildings</code>, etc.</div>}
            component={renderInput}
          />
          <hr />
          <Field
            id='formControlsTextarea'
            label='Feature Selection'
            rows='10'
            name='feature_selection'
            component={renderTextArea}
            className={styles.featureSelection}
          />
          <Field
            id='formControlExtraNotes'
            name='extra_notes'
            rows='4'
            label='Extra Notes (prepended to notes section)'
            component={renderTextArea}
          />
          <Row>
            <Col xs={6}>
              <Field
                name='is_private'
                description='Private'
                component={renderCheckbox}
                type='checkbox'
              />
            </Col>
            <Col xs={6}>
              <Field
                name='subnational'
                description='Dataset contains sub-national data'
                component={renderCheckbox}
                type='checkbox'
              />
            </Col>
          </Row>
          <Row>
            <Col xs={12}>
              <Field
                name='buffer_aoi'
                description='AOI is an administrative boundary (and should be buffered)'
                component={renderCheckbox}
                type='checkbox'
              />
            </Col>
          </Row>
          <Field
            name='locations'
            multi
            label='Location'
            component={renderMultiSelect}
            options={locationOptions}
            isLoading={locationOptions == null}
          />
          <Field
            name='license_human_readable'
            type='text'
            label='License'
            disabled
            component={renderInput}
          />
          <Field
            name='license'
            label='License'
            disabled
            component='input'
            type='hidden'
          />
          <hr />
          <Row>
            <Col xs={6}>
              <Field
                name='schedule_period'
                label='Run this export on an automated schedule:'
                component={renderSelect}
              >
                <option value='daily'>Daily</option>
                <option value='weekly'>Weekly (Sunday)</option>
                <option value='monthly'>Monthly (1st of month)</option>
                <option value='6hrs'>Every 6 hours</option>
                <option value='disabled'>Don't automatically schedule</option>
              </Field>
            </Col>
            <Col xs={5} xsOffset={1}>
              <Field
                name='schedule_hour'
                label='At time:'
                component={renderSelect}
              >
                { getTimeOptions() }
              </Field>
            </Col>
          </Row>
          <Row>
            <Col xs={5}>
              <Field
                name='export_formats'
                label='File Formats'
                component={renderCheckboxes}
              >
                {getFormatCheckboxes()}
              </Field>
            </Col>
            <Col xs={7}>
              { editing && exportRegion
              ? <ExistingDatasetsPanel
                datasets={exportRegion.datasets}
                error={error}
                handleSubmit={handleSubmit}
                status={status}
                styles={styles}
                submitting={submitting}
              />
              : <PendingDatasetsPanel
                datasetPrefix={datasetPrefix}
                error={error}
                featureSelection={featureSelection}
                handleSubmit={handleSubmit}
                status={status}
                styles={styles}
                submitting={submitting}
              />
              }
            </Col>
          </Row>
        </form>
        {editing && exportRegion &&
          <div>
            <Row>
              <Col xs={7}>
                <h4>HDX Datasets</h4>
                <ul>
                  {
                    exportRegion.datasets.map((x, i) => (
                      <li key={i}>
                        <code><a href={x.url}>{x.name}</a></code>
                      </li>
                    ))
                  }
                </ul>
              </Col>
              <Col xs={5}>
                <Panel>
                  <p>
                    <strong>Last run:</strong> {this.getLastRun()}<br />
                    <strong>Next scheduled run:</strong> {this.getNextRun()}
                  </p>
                  <Button
                    bsStyle='primary'
                    disabled={running}
                    onClick={this.handleRun}
                  >
                    {running ? 'Running...' : 'Run Now'}
                  </Button>
                </Panel>
              </Col>
            </Row>
            <h3>Run History <small><a href={`/exports/${exportRegion.job.uid}`}>view export details</a></small></h3>
            {exportRegion.runs.length > 0
              ? <Table>
                <thead>
                  <tr>
                    <th>
                      Run Started
                    </th>
                    <th>
                      Status
                    </th>
                    <th>
                      Elapsed Time
                    </th>
                    <th>
                      Total Size
                    </th>
                  </tr>
                </thead>
                <tbody>{this.getRunRows()}</tbody>
              </Table>
              : <p>This regional export has never been run.</p>
            }
            <Panel>
              <p>
                This will unschedule the export region.
                Any existing datasets created by this region will remain on HDX.
              </p>
              <Button bsStyle='danger' block disabled={deleting} onClick={this.handleDelete}>
                {deleting ? 'Removing Export Region...' : 'Remove Export Region'}
              </Button>
            </Panel>
          </div>
        }
      </div>
    );
  }
}

const mapStateToProps = state => {
  return {
    aoiInfo: state.aoiInfo,
    datasetPrefix: formValueSelector(FORM_NAME)(state, 'dataset_prefix'),
    featureSelection: formValueSelector(FORM_NAME)(state, 'feature_selection'),
    hdx: state.hdx,
    initialValues: {
      feature_selection: `
buildings:
  hdx:
    name:
    tags: building, osm
    caveats:
  types:
    - polygons
  select:
    - name
    - building
    - building:levels
    - building:materials
    - addr:housenumber
    - addr:street
    - addr:city
    - office
  where: building IS NOT NULL

roads:
  hdx:
    name:
    tags: roads, osm
    caveats:
  types:
    - lines
    - polygons
  select:
    - name
    - highway
    - surface
    - smoothness
    - width
    - lanes
    - oneway
    - bridge
    - layer
  where: highway IS NOT NULL

waterways:
  hdx:
    name:
    tags: water, osm
    caveats:
  types:
    - lines
    - polygons
  select:
    - name
    - waterway
    - covered
    - width
    - depth
    - layer
    - blockage
    - tunnel
    - natural
    - water
  where: waterway IS NOT NULL OR water IS NOT NULL OR natural IN ('water','wetland','bay')

points_of_interest:
  hdx:
    name:
    tags: poi, osm
    caveats:
  types:
    - points
    - polygons
  select:
    - name
    - amenity
    - man_made
    - shop
    - tourism
    - opening_hours
    - beds
    - rooms
    - addr:housenumber
    - addr:street
    - addr:city
  where: amenity IS NOT NULL OR man_made IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL

admin_boundaries:
  hdx:
    name:
    tags: admin, osm
    caveats: Boundaries are crowd-sourced and may not align with other datasets
  types:
    - lines
    - polygons
  select:
    - name
    - boundary
    - admin_level
    - place
  where: boundary = 'administrative' OR admin_level IS NOT NULL
`.trim(),
      is_private: true,
      license: 'hdx-odc-by',
      license_human_readable: 'Open Database License (ODC-ODbL)',
      schedule_period: 'daily',
      schedule_hour: 0,
      subnational: true
    },
    name: formValueSelector(FORM_NAME)(state, 'name')
  };
};

const flatten = arr => arr.reduce(
  (acc, val) => acc.concat(
    Array.isArray(val) ? flatten(val) : val
  ),
  []
);

const mapDispatchToProps = dispatch => {
  return {
    clearAOI: () => {
      dispatch(clearAoiInfo());
      dispatch(clickResetMap());
    },
    getExportRegion: id => dispatch(getExportRegion(id)),
    handleDelete: id => dispatch(deleteExportRegion(id)),
    handleRun: (id, jobUid) => dispatch(runExport(id, jobUid)),
    showAllExportRegions: () => dispatch(push('/')),
    updateAOI: geometry => {
      dispatch(updateAoiInfo({
        features: [
          {
            type: 'Feature',
            geometry,
            properties: {}
          }
        ],
        type: 'FeatureCollection',
        geomType: 'Polygon',
        title: 'Custom Polygon'
      }, 'Polygon', 'Custom Polygon', 'Saved'));
    }
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(form(HDXExportRegionForm));
