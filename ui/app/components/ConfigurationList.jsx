import React, { Component } from "react";

import {
  Col,
  Row,
  Table,
  Button,
  InputGroup,
  FormControl,
  Checkbox
} from "react-bootstrap";
import { connect } from "react-redux";
import { Link } from "react-router-dom";

import ConfigurationForm from "./ConfigurationForm";
import Paginator from "./Paginator";
import {
  getConfigurations,
  getConfiguration
} from "../actions/configurations";
import { selectConfigurations } from "../selectors";

const ConfigurationTable = ({ configurations }) =>
  <tbody>
    {configurations.map((configuration, i) => {
      return (
        <tr key={i}>
          <td>
            <Link to={`/configurations/detail/${configuration.uid}`}>
              {configuration.name}
            </Link>
          </td>
          <td>
            {configuration.description}
          </td>
          <td />
          <td>
            {configuration.user.username}
          </td>
        </tr>
      );
    })}
  </tbody>;

class ConfigurationListPane extends Component {
  componentDidMount() {
    this.state = { searchQuery: "", onlyMine: false };
    this.props.getConfigurations();
  }

  onSearchSubmit = e => {
    console.log("Submit");
    this.setState({ searchQuery: e.target.value });
  };

  clearSearch = e => {
    this.setState({ searchQuery: "" });
  };

  render() {
    const { configurations, getConfigurations } = this.props;

    return (
      <Col xs={6} style={{ height: "100%", overflowY: "scroll" }}>
        <div style={{ padding: "20px" }}>
          <h2 style={{ display: "inline" }}>Configurations</h2>
          <Link
            to="/configurations/new"
            style={{ float: "right" }}
            className="btn btn-primary btn-lg"
          >
            Create New Configuration
          </Link>
          {configurations.total > 0 &&
            <div>
              <InputGroup
                style={{
                  width: "100%",
                  marginTop: "20px",
                  marginBottom: "10px"
                }}
              >
                <InputGroup.Button>
                  <Button>Clear</Button>
                </InputGroup.Button>
                <FormControl
                  type="text"
                  placeholder="Search for a name or description..."
                />
                <InputGroup.Button>
                  <Button>Search</Button>
                </InputGroup.Button>
              </InputGroup>
              <Checkbox>My Configurations</Checkbox>
              <Table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Tables</th>
                    <th>Owner</th>
                  </tr>
                </thead>
                <ConfigurationTable configurations={configurations.items} />
              </Table>
              <Paginator
                collection={configurations}
                getPage={getConfigurations}
              />
            </div>}
        </div>
      </Col>
    );
  }
}

const ConfigurationListPaneContainer = connect(
  state => ({
    configurations: selectConfigurations(state)
  }),
  {
    getConfigurations
  }
)(ConfigurationListPane);

export class ConfigurationNew extends Component {
  render() {
    return (
      <Row style={{ height: "100%" }}>
        <ConfigurationListPaneContainer />
        <Col xs={6} style={{ height: "100%", overflowY: "scroll" }}>
          <div style={{ padding: "20px" }}>
            <ConfigurationForm />
          </div>
        </Col>
      </Row>
    );
  }
}

class ConfigurationDetail extends Component {
  componentDidMount() {
    const { configurationId, getConfiguration } = this.props;

    getConfiguration(configurationId);
  }

  componentWillReceiveProps(props) {
    const { configurationId: prevConfigurationId } = this.props;
    const { configurationId, getConfiguration } = props;

    if (prevConfigurationId !== configurationId) {
      getConfiguration(configurationId);
    }
  }

  render() {
    const { match: { params: { uid } } } = this.props;
    return (
      <Row style={{ height: "100%" }}>
        <ConfigurationListPaneContainer />
        <Col xs={6} style={{ height: "100%", overflowY: "scroll" }}>
          <div style={{ padding: "20px" }}>
            <ConfigurationForm configurationUid={uid} />
          </div>
        </Col>
      </Row>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  configurationId: ownProps.match.params.uid
});

export const ConfigurationDetailContainer = connect(mapStateToProps, {
  getConfiguration
})(ConfigurationDetail);

export class ConfigurationList extends Component {
  render() {
    return (
      <Row style={{ height: "100%" }}>
        <ConfigurationListPaneContainer />
        <Col xs={6} style={{ height: "100%", overflowY: "scroll" }} />
      </Row>
    );
  }
}

export default ConfigurationList;
