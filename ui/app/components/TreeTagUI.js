import React, { Component } from "react";
import { Button, Col, FormControl, InputGroup } from "react-bootstrap";
import { FormattedMessage, defineMessages, injectIntl } from "react-intl";

import CheckboxHelp from "./CheckboxHelp";
import TreeMenu from "./react-tree-menu/TreeMenu";

const messages = defineMessages({
  tagTreeSearchPlaceholder: {
    id: "export.tag_tree_search.placeholder",
    defaultMessage: "Search for a feature type..."
  }
});

class TreeTagUI extends Component {
  state = {
    hoveredCheckboxName: null
  };
  onCheckboxHover = checkboxName =>
    this.setState({ hoveredCheckboxName: checkboxName });

  render() {
    const {
      clearSearch,
      intl: { formatMessage },
      labelFilter,
      onSearchChange,
      onTreeNodeCheckChange,
      onTreeNodeCollapseChange,
      tagTreeData
    } = this.props;

    return (
      <div>
        <InputGroup
          style={{ width: "100%", marginTop: "20px", marginBottom: "10px" }}
        >
          <FormControl
            id="treeTagSearch"
            type="text"
            placeholder={formatMessage(messages.tagTreeSearchPlaceholder)}
            onChange={onSearchChange}
          />
          <InputGroup.Button>
            <Button onClick={clearSearch}>
              <FormattedMessage id="ui.clear" defaultMessage="Clear" />
            </Button>
          </InputGroup.Button>
        </InputGroup>
        <Col xs={6}>
          <TreeMenu
            data={tagTreeData}
            onTreeNodeCollapseChange={onTreeNodeCollapseChange}
            onTreeNodeCheckChange={onTreeNodeCheckChange}
            expandIconClass="fa fa-chevron-right"
            collapseIconClass="fa fa-chevron-down"
            labelFilter={labelFilter}
            onCheckboxHover={this.onCheckboxHover}
          />
        </Col>
        <Col xs={6}>
          <CheckboxHelp name={this.state.hoveredCheckboxName} />
        </Col>
      </div>
    );
  }
}

export default injectIntl(TreeTagUI);
