import React, {Component} from 'react';
import {connect} from 'react-redux';
import { FormGroup,ControlLabel,FormControl,HelpBlock,Row,Col, Checkbox,Panel,Button,Table } from 'react-bootstrap';
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

export class HDXEditForm extends Component {

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
              <h2>Edit Export Region</h2>
              <FormGroup controlId="formControlsTextarea">
                <ControlLabel>Feature Selection</ControlLabel>
                <FormControl componentClass="textarea" rows="10" placeholder=""/>
              </FormGroup>
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
                    This will immediately update the following datasets on HDX:
                    <ul>
                      <li><code>hotosm_senegal_admin_boundaries</code></li>
                      <li><code>hotosm_senegal_buildings</code></li>
                      <li><code>hotosm_senegal_points_of_interest</code></li>
                      <li><code>hotosm_senegal_roads</code></li>
                      <li><code>hotosm_senegal_waterways</code></li>
                    </ul>
                    <Button bsStyle="primary" bsSize="large" type="submit" block>
                      Save + Sync to HDX
                    </Button>
                  </Panel>
                </Col>
              </Row>
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
            </form>
            <Panel>
              <strong>Next scheduled run:</strong> 2017/03/30 0:00 UTC
              <Button bsStyle="primary" style={{'float':'right'}}>
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
)(HDXEditForm);


