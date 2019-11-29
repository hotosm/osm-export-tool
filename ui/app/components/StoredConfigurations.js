import React, { Component } from "react";
import { Button, Table } from "react-bootstrap";
import { FormattedMessage, defineMessages, injectIntl } from "react-intl";
import { connect } from "react-redux";
import { push } from "react-router-redux";
import { change } from "redux-form";

import { getConfigurations } from "../actions/configurations";
import { selectConfigurations } from "../selectors";

import FilterForm from "./FilterForm";
import Paginator from "./Paginator";

const messages = defineMessages({
  configurationTitle: {
    id: "configuration.title",
    defaultMessage: "Configurations"
  }
});

class StoredConfigurations extends Component {
  state = {
    filters: {}
  };

  componentWillMount() {
    this.props.getConfigurations();
  }

  onClick = yaml => {
    const { dispatch, setYaml } = this.props;

    setYaml(yaml);
    dispatch(push("/exports/new/select/yaml"));
  };

  search = ({ search, ...values }) => {
    const { getConfigurations } = this.props;
    const { filters } = this.state;

    const newFilters = {
      ...filters,
      ...values,
      search
    };

    this.setState({
      filters: newFilters
    });

    return getConfigurations(newFilters);
  };

  render() {
    const {
      configurations,
      getConfigurations,
      intl: { formatMessage }
    } = this.props;
    const { filters } = this.state;

    if (configurations.total === 0 && filters === {}) {
      // TODO return something better here
      return null;
    }

    return (
      <div>
        <FilterForm
          type={formatMessage(messages.configurationTitle)}
          onSubmit={this.search}
        />
        <Paginator
          collection={configurations}
          getPage={(p) => {
            getConfigurations(filters,p);
          }}
        />
        <Table>
          <thead>
            <tr>
              <th>
                <FormattedMessage
                  id="configuration.name.label"
                  defaultMessage="Name"
                />
              </th>
              <th>
                <FormattedMessage
                  id="configuration.description.label"
                  defaultMessage="Description"
                />
              </th>
              <th />
            </tr>
          </thead>
          <tbody>
            {configurations.items.map((configuration, i) => {
              return (
                <tr key={i}>
                  <td>
                    {configuration.name}
                  </td>
                  <td>
                    {configuration.description}
                  </td>
                  <td>
                    <Button
                      bsSize="small"
                      onClick={() => this.onClick(configuration.yaml)}
                    >
                      <FormattedMessage
                        id="configuration.load_yaml"
                        defaultMessage="Load YAML"
                      />
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </Table>
      </div>
    );
  }
}

export default connect(
  state => ({
    configurations: selectConfigurations(state)
  }),
  dispatch => {
    return {
      getConfigurations: (filters, p) => dispatch(getConfigurations(filters,p)),
      setYaml: yaml => dispatch(change("ExportForm", "feature_selection", yaml))
    };
  }
)(injectIntl(StoredConfigurations));
