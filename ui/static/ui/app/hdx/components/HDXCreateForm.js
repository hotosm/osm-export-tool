import React, {Component} from 'react';
import {connect} from 'react-redux';
import { FormGroup,ControlLabel,FormControl,HelpBlock,Row,Col, Checkbox,Panel,Button } from 'react-bootstrap';
import styles from '../styles/HDXCreateForm.css';

function FieldGroup({ id, label, help, ...props }) {
  return (
    <FormGroup controlId={id}>
      <ControlLabel>{label}</ControlLabel>
      <FormControl {...props} />
      {help && <HelpBlock>{help}</HelpBlock>}
    </FormGroup>
  );
}

export class HDXCreateForm extends Component {

    constructor(props) {
        super(props);
        this.state = {
        }
    }

    componentWillReceiveProps(nextProps) {
    }

    render() {
        return (
          <div className={styles.hdxCreateForm}>
            <form action="/hdx/" method="get">
              <h2>Create Export Region</h2>
              <FieldGroup
                id="formControlsText"
                type="text"
                label="Dataset Prefix"
                placeholder="hotosm_senegal"
              />
              <div>Example: prefix <code>hotosm_senegal</code> results in datasets <code>hotosm_senegal_roads</code>, <code>hotosm_senegal_buildings</code>, etc.</div>
              <hr/>
              <FormGroup controlId="formControlsTextarea">
                <ControlLabel>Feature Selection</ControlLabel>
                <FormControl componentClass="textarea" rows="10" placeholder=""/>
              </FormGroup>
              <hr/>
              <Row>
                <Col xs={6}>
                  <FormGroup controlId="formControlsSelect">
                    <ControlLabel>Run this export on an automated schedule:</ControlLabel>
                    <FormControl componentClass="select" placeholder="select">
                      <option value="day">Daily</option>
                      <option value="week">Weekly (Sunday)</option>
                      <option value="month">Monthly (1st of month)</option>
                      <option value="6hours">Every 6 hours</option>
                      <option value="never">Don't automatically schedule</option>
                    </FormControl>
                  </FormGroup>
                </Col>
                <Col xs={5} xsOffset={1}>
                  <FormGroup controlId="formControlsSelect">
                    <ControlLabel>At time:</ControlLabel>
                    <FormControl componentClass="select" placeholder="select">
                      <option value="0">0:00 UTC</option>
                    </FormControl>
                  </FormGroup>
                </Col>
              </Row>
              <Row>
                <Col xs={5}>
                  <FormGroup controlId="formControlsFormats">
                    <ControlLabel>File Formats</ControlLabel>
                    <Checkbox>
                      ESRI Shapefiles
                    </Checkbox>
                    <Checkbox>
                      Geopackage
                    </Checkbox>
                    <Checkbox>
                      Garmin .IMG
                    </Checkbox>
                    <Checkbox>
                      .KMZ
                    </Checkbox>
                    <Checkbox>
                      OpenStreetMap .PBF
                    </Checkbox>
                  </FormGroup>
                </Col>
                <Col xs={7}>
                  <Panel>
                    This will immediately create 5 datasets on HDX:
                    <ul>
                      <li><code>hotosm_senegal_admin_boundaries</code></li>
                      <li><code>hotosm_senegal_buildings</code></li>
                      <li><code>hotosm_senegal_points_of_interest</code></li>
                      <li><code>hotosm_senegal_roads</code></li>
                      <li><code>hotosm_senegal_waterways</code></li>
                    </ul>
                    <Button bsStyle="primary" bsSize="large" type="submit" block>
                      Create Datasets + Run Export
                    </Button>
                  </Panel>
                </Col>
              </Row>
            </form>
          </div>
        )
    }
}


function mapStateToProps(state) {
    return {
    };
}

function mapDispatchToProps(dispatch) {
    return {
    }
}

export default connect(
)(HDXCreateForm);

