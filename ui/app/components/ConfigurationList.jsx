import React, { Component } from "react";

import {
  Col,
  Row,
  Table,
  Button,
  InputGroup,
  FormControl,
  Checkbox,
  Form,
  FormGroup
} from "react-bootstrap";
import { connect } from "react-redux";
import { Link } from "react-router-dom";
import ConfigurationForm from "./ConfigurationForm";
import {
  getConfigurations,
  getConfiguration
} from "../actions/configurationActions";
import { Paginator } from "./utils";

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
          <InputGroup
            style={{ width: "100%", marginTop: "20px", marginBottom: "10px" }}
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
            <ConfigurationTable
              configurations={this.props.configurations.items}
            />
          </Table>
          <Paginator
            collection={this.props.configurations}
            getPage={this.props.getConfigurations}
          />
        </div>
      </Col>
    );
  }
}

const ConfigurationListPaneContainer = connect(
  state => {
    return {
      configurations: state.configurations
    };
  },
  dispatch => {
    return {
      getConfigurations: url => dispatch(getConfigurations(url))
    };
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
    const { match: { params: { uid } }, getConfiguration } = this.props;
    this.props.getConfiguration(uid);
  }

  componentWillReceiveProps(props) {
    const { match: { params: { uid } }, getConfiguration } = props;
    this.props.getConfiguration(uid);
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

export const ConfigurationDetailContainer = connect(
  state => {
    return {
      configurations: state.configurations
    };
  },
  dispatch => {
    return {
      getConfiguration: uid => dispatch(getConfiguration(uid))
    };
  }
)(ConfigurationDetail);

export class ConfigurationList extends Component {
  componentDidMount() {}

  render() {
    return (
      <Row style={{ height: "100%" }}>
        <ConfigurationListPaneContainer />
        <Col xs={6} style={{ height: "100%", overflowY: "scroll" }} />
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

export default connect(mapStateToProps, mapDispatchToProps)(ConfigurationList);
