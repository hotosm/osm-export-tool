import React, { Component } from "react";
import { Button } from "react-bootstrap";
import { updateIntl } from "react-intl-redux";
import { connect } from "react-redux";

import { selectIntl } from "../selectors";

class LocaleSelector extends Component {
  selectLocale = locale => {
    const { updateIntl } = this.props;

    updateIntl({
      locale,
      messages: require(`../i18n/locales/${locale}.json`)[locale]
    });
  };

  render() {
    return (
      <ul className="locales">
        <li>
          <Button
            type="button"
            bsStyle="link"
            onClick={() => this.selectLocale("id")}
          >
            Bahasa Indonesia
          </Button>
        </li>
        <li>
          <Button
            type="button"
            bsStyle="link"
            onClick={() => this.selectLocale("de")}
          >
            Deutsch
          </Button>
        </li>
        <li>
          <Button
            type="button"
            bsStyle="link"
            onClick={() => this.selectLocale("en")}
          >
            English
          </Button>
        </li>
        <li>
          <Button
            type="button"
            bsStyle="link"
            onClick={() => this.selectLocale("es")}
          >
            Español
          </Button>
        </li>
        <li>
          <Button
            type="button"
            bsStyle="link"
            onClick={() => this.selectLocale("fr")}
          >
            Français
          </Button>
        </li>
        <li>
          <Button
            type="button"
            bsStyle="link"
            onClick={() => this.selectLocale("it")}
          >
            Italiano
          </Button>
        </li>
        <li>
          <Button
            type="button"
            bsStyle="link"
            onClick={() => this.selectLocale("nl_NL")}
          >
            Nederlands
          </Button>
        </li>
        <li>
          <Button
            type="button"
            bsStyle="link"
            onClick={() => this.selectLocale("pt")}
          >
            Português
          </Button>
        </li>
      </ul>
    );
  }
}

const mapStateToProps = state => ({
  intl: selectIntl(state)
});

export default connect(mapStateToProps, { updateIntl })(LocaleSelector);
