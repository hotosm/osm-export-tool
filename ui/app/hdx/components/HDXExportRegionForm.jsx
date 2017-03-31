import React, { Component } from 'react';

import axios from 'axios';
const jsts = require('jsts');
import { FormGroup, ControlLabel, FormControl, HelpBlock, Row, Col, Checkbox, Panel, Button, Table } from 'react-bootstrap';
import cookie from 'react-cookie';
import { connect } from 'react-redux';
import { push } from 'react-router-redux';
import { Field, SubmissionError, formValueSelector, reduxForm } from 'redux-form';

import { updateAoiInfo } from '../actions/exportsActions';
import { getExportRegion } from '../actions/hdxActions';
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

    if (values.id != null) {
      url += `/${values.id}`;
    }

    return axios({
      url,
      method: 'POST',
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
  state = {
    editing: false
  };

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

      console.log(exportRegion);
    }
  }

  render () {
    const { editing } = this.state;
    const { error, handleSubmit, submitting } = this.props;
    let datasetPrefix = this.props.datasetPrefix || '<prefix>';

    return (
      <div className={styles.hdxForm}>
        {/* TODO breadcrumbs back to Export Region List */}
        <form onSubmit={handleSubmit}>
          <h2>{editing ? 'Edit' : 'Create'} Export Region</h2>
          {error && <strong className={styles.error}>{error}</strong>}
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
          <hr />
          <Row>
            <Col xs={6}>
              <Field
                name='schedule_period'
                label='Run this export on an automated schedule:'
                component={renderSelect}
              >
                <option value='day'>Daily</option>
                <option value='week'>Weekly (Sunday)</option>
                <option value='month'>Monthly (1st of month)</option>
                <option value='6hours'>Every 6 hours</option>
                <option value='never'>Don't automatically schedule</option>
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
        {editing &&
          <div>
            <Panel>
              <strong>Next scheduled run:</strong> 2017/03/30 0:00 UTC
              <Button bsStyle='primary' style={{float: 'right'}}>
                Run Now
              </Button>
            </Panel>
            <h3>Run History</h3>
            <Table>
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
              <tbody>
                <tr>
                  <td>
                    2017/03/26
                  </td>
                  <td>
                    10 minutes
                  </td>
                  <td>
                    256 MB
                  </td>
                </tr>
              </tbody>
            </Table>
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
    hdx: state.hdx
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
