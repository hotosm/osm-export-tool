import React, { Component } from 'react';

import { Col, Row, Table } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import ConfigurationForm from './ConfigurationForm';
import { getConfigurations } from '../actions/configurationActions'

const ConfigurationTable = ({configurations}) => <tbody>
  {configurations.map((configuration,i) => {
    return <tr key={i}>
      <td>{configuration.name}</td>
      <td>{configuration.description}</td>
      <td></td>
      <td>{configuration.user.username}</td>
    </tr>
  })}
</tbody>

class ConfigurationListPane extends Component {
  componentDidMount() {
    this.props.getConfigurations()
  }

  render() {
    return (
      <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
        <div style={{padding: '20px'}}>
          <h2 style={{display:"inline"}}>Configurations</h2>
          <Link to='/configurations/new' style={{float: "right"}} className='btn btn-primary btn-lg'>
            Create New Configuration
          </Link>
          <Table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Tables</th>
                <th>Owner</th>
              </tr>
            </thead>
            <ConfigurationTable configurations={this.props.configurations}/>
          </Table>
        </div>
      </Col>
    )
  }
}

const ConfigurationListPaneR = connect(
  state => {
    return {
      configurations: state.configurations
    }
  },
  dispatch => {
    return {
      getConfigurations: () => dispatch(getConfigurations)
    }
  }
)(ConfigurationListPane);

export class ConfigurationNew extends Component {
  render () {
    return (
      <Row style={{height: '100%'}}>
        <ConfigurationListPaneR/>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
          <div style={{padding: '20px'}}>
            <ConfigurationForm/>
          </div>
        </Col>
      </Row>
    );
  }
}

export class ConfigurationDetail extends Component {
  render() {
    return <div></div>
  }
}

export class ConfigurationList extends Component {
  componentDidMount () {
  }

  render () {
    return (
      <Row style={{height: '100%'}}>
        <ConfigurationListPaneR/>
        <Col xs={6} style={{height: '100%', overflowY: 'scroll'}}>
        </Col>
      </Row>
    );
  }
}

const mapStateToProps = state => {
  return {};
};

const mapDispatchToProps = dispatch => {
  return {};
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ConfigurationList);

