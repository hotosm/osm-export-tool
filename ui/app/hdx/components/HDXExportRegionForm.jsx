import React, { Component } from 'react';

import axios from 'axios';
const jsts = require('jsts');
import prettyBytes from 'pretty-bytes';
import { FormGroup, ControlLabel, FormControl, HelpBlock, Row, Col, Checkbox, Panel, Button, Table } from 'react-bootstrap';
import cookie from 'react-cookie';
import { Field, SubmissionError, formValueSelector, reduxForm } from 'redux-form';
import { FormattedDate, FormattedNumber, FormattedRelative, IntlMixin } from 'react-intl';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { push } from 'react-router-redux';

import { updateAoiInfo } from '../actions/exportsActions';
import { deleteExportRegion, getExportRegion, runExport } from '../actions/hdxActions';
import styles from '../styles/HDXExportRegionForm.css';

const AVAILABLE_EXPORT_FORMATS = {
  shp: 'ESRI Shapefiles',
  geopackage: 'GeoPackage',
  garmin: 'Garmin .IMG',
  kml: '.KMZ',
  pbf: 'OpenStreetMap .PBF'
};

const form = reduxForm({
  form: 'HDXExportRegionForm',
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

    const formData = {
      ...values,
      the_geom: props.aoiInfo.geojson.features[0].geometry,
      export_formats: exportFormats
    };

    let url = '/api/hdx_export_regions';
    let method = 'POST';

    if (values.id != null) {
      url += `/${values.id}`;
      method = 'PUT';
    }

    return axios({
      url,
      method: method,
      contentType: 'application/json; version=1.0',
      data: formData,
      headers: {
        'X-CSRFToken': cookie.load('csrftoken')
      }
    }).then(rsp => {
      console.log('Success');

      console.log('id:', rsp.data.id);

      if (props.hdx.exportRegion == null) {
        dispatch(push(`/edit/${rsp.data.id}`));
      }
    }).catch(err => {
      console.warn(err);

      if (err.response) {
        throw new SubmissionError(err.response.data);
      }

      throw new SubmissionError({
        _error: 'Export region creation failed.'
      });
    });
  }
});

const renderInput = ({ id, input, label, help, meta: { touched, error }, ...props }) =>
  <FormGroup controlId={id || props.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{touched && error && <p className={styles.error}>{error}</p>}{help}</HelpBlock>
  </FormGroup>;

const renderTextArea = ({id, label, input, data, meta: { touched, error }, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl componentClass='textarea' {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{touched && error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

const renderSelect = ({id, label, input, data, meta: { touched, error }, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    <FormControl componentClass='select' {...input} {...props} />
    <FormControl.Feedback />
    <HelpBlock>{touched && error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

const renderCheckboxes = ({id, label, input, data, meta: { touched, error }, description, ...props}) =>
  <FormGroup controlId={id || input.name} validationState={error && 'error'}>
    <ControlLabel>{label}</ControlLabel>
    {props.children}
    <FormControl.Feedback />
    <HelpBlock>{touched && error && <span className={styles.error}>{error}</span>}</HelpBlock>
  </FormGroup>;

const renderCheckbox = ({input, data, meta: { touched, error }, description, ...props}) =>
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

export class HDXExportRegionForm extends Component {
  mixins = [IntlMixin];

  state = {
    deleting: false,
    editing: false,
    running: false
  };

  getLastRun () {
    const { hdx: { exportRegion } } = this.props;

    if (exportRegion.last_run == null) {
      return 'Never';
    }

    return <FormattedRelative value={exportRegion.last_run} />;
  }

  getNextRun () {
    const { hdx: { exportRegion } } = this.props;

    if (exportRegion.next_run == null) {
      return 'Never';
    }

    return <FormattedRelative value={exportRegion.next_run} />;
  }

  componentDidMount () {
    const { getExportRegion, match: { params: { id } } } = this.props;

    if (id != null) {
      // we're editing
      getExportRegion(id);

      this.setState({
        editing: true
      });
    }
  }

  componentWillReceiveProps (props) {
    const { hdx: { statusCode }, showAllExportRegions } = props;

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

    if (this.props.hdx.exportRegion == null &&
        props.hdx.exportRegion != null) {
      // we're receiving an export region

      const { hdx: { exportRegion }, updateAOI } = props;

      // NOTE: this also sets some form properties that we don't care about (but that show up in the onSubmit handler)
      Object.keys(exportRegion).forEach(k =>
        props.change(k, exportRegion[k]));

      exportRegion.export_formats.forEach(x =>
        props.change(x, true));

      updateAOI(exportRegion.the_geom);

      console.log('Export region:', exportRegion);
    }

    if (props.hdx.deleted) {
      this.props.showAllExportRegions();
    }
  }

  getRunRows () {
    const { hdx: { exportRegion } } = this.props;

    return exportRegion.runs.map((run, i) => (
      <tr key={i}>
        <td>
          <FormattedDate value={run.run_at} />
        </td>
        <td>
          <FormattedNumber value={run.elapsed_time / 60} /> minutes
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

    this.props.handleDelete(this.props.hdx.exportRegion.id);
  };

  handleRun = () => {
    this.setState({
      running: true
    });

    this.props.handleRun(this.props.hdx.exportRegion.job.uid);
  };

  render () {
    const { deleting, editing, running } = this.state;
    const { error, handleSubmit, hdx: { exportRegion }, submitting } = this.props;
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
          {error && <p><strong className={styles.error}>{error}</strong></p>}
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
          />
          <Field
            id='formControlExtraNotes'
            name='extraNotes'
            rows='4'
            label='Extra Notes (appended to notes section)'
            component={renderTextArea}
          />
          <Row>
            <Col xs={6}>
              <Field
                name='countryCodes'
                type='text'
                label='Country Codes'
                placeholder='SEN'
                component={renderInput}
              />
            </Col>
            <Col xs={6}>
              <Field
                name='metadataTags'
                type='text'
                label='Tags'
                placeholder='openstreetmap'
                component={renderInput}
              />
            </Col>
          </Row>
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
              <Panel>
                This will immediately create 5 datasets on HDX:
                <ul>
                  {/* TODO these need to be generated from the feature selection */}
                  <li><code>{datasetPrefix}_admin_boundaries</code></li>
                  <li><code>{datasetPrefix}_buildings</code></li>
                  <li><code>{datasetPrefix}_points_of_interest</code></li>
                  <li><code>{datasetPrefix}_roads</code></li>
                  <li><code>{datasetPrefix}_waterways</code></li>
                </ul>
                <Button bsStyle='primary' bsSize='large' type='submit' disabled={submitting} onClick={handleSubmit} block>
                  {editing ? 'Save + Sync to HDX' : 'Create Datasets + Run Export'}
                </Button>
              </Panel>
            </Col>
          </Row>
        </form>
        {editing && exportRegion &&
          <div>
            <Panel>
              <Button bsStyle='primary' style={{float: 'right'}} disabled={running} onClick={this.handleRun}>
                {running ? 'Running...' : 'Run Now'}
              </Button>
              <strong>Last run:</strong> {this.getLastRun()}<br />
              <strong>Next scheduled run:</strong> {this.getNextRun()}
            </Panel>
            <h3>Run History</h3>
            {exportRegion.runs.length > 0
              ? <Table>
                <thead>
                  <tr>
                    <th>
                      Run Started
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
              : <p>This export region has never been run.</p>
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
    datasetPrefix: formValueSelector('HDXExportRegionForm')(state, 'dataset_prefix'),
    hdx: state.hdx,
    name: formValueSelector('HDXExportRegionForm')(state, 'name')
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
    getExportRegion: id => dispatch(getExportRegion(id)),
    handleDelete: id => dispatch(deleteExportRegion(id, cookie.load('csrftoken'))),
    handleRun: id => dispatch(runExport(id, cookie.load('csrftoken'))),
    showAllExportRegions: () => dispatch(push('/')),
    updateAOI: geometry => {
      const envelope = new jsts.io.GeoJSONReader().read(geometry).getEnvelope().getCoordinates();

      const bbox = [envelope[0], envelope[2]]
        .map(c => [c.x, c.y])
        .reduce((acc, val) => acc.concat(val), []);

      dispatch(updateAoiInfo({
        features: [
          {
            // TODO wouldn't it be nice if ExportAOI didn't require a feature collection with a bbox?
            type: 'Feature',
            bbox,
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
