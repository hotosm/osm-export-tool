import React, { Component } from "react";
import { MenuItem, NavDropdown } from "react-bootstrap";
import { updateIntl } from "react-intl-redux";
import { connect } from "react-redux";

import { selectIntl } from "../selectors";

const LOCALES = ["id", "de", "en", "es", "fr", "it", "nl_NL", "pt"];
const LANGUAGES = {
  id: "Bahasa Indonesia",
  de: "Deutsch",
  en: "English",
  es: "Español",
  fr: "Français",
  it: "Italiano",
  nl_NL: "Nederlands",
  pt: "Português"
};

const getLanguage = locale => LANGUAGES[locale] || "Unknown";

class LocaleSelector extends Component {
  selectLocale = locale => {
    const { updateIntl } = this.props;

    try {
      updateIntl({
        locale,
        messages: require(`../i18n/locales/${locale}.json`)[locale]
      });
    } catch (err) {
      updateIntl({
        locale
      });
    }
  };

  render() {
    const { intl: { locale } } = this.props;

    return (
      <NavDropdown title={getLanguage(locale)}>
        {LOCALES.map((locale, idx) =>
          <MenuItem eventKey={locale} key={idx} onSelect={this.selectLocale}>
            {getLanguage(locale)}
          </MenuItem>
        )}
      </NavDropdown>
    );
  }
}

const mapStateToProps = state => ({
  intl: selectIntl(state)
});

export default connect(mapStateToProps, { updateIntl })(LocaleSelector);
