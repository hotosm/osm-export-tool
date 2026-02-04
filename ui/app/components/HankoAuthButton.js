import React from "react";

/**
 * React 15 wrapper for the <hotosm-auth> web component.
 *
 * React 15 doesn't properly handle custom element attributes (especially
 * hyphenated ones like hanko-url). This component uses DOM APIs to create
 * and configure the web component imperatively via a ref.
 */
class HankoAuthButton extends React.Component {
  componentDidMount() {
    this._renderWebComponent();
  }

  componentDidUpdate() {
    this._renderWebComponent();
  }

  _renderWebComponent() {
    if (!this._container) return;

    // Only create the element once
    if (!this._element) {
      this._element = document.createElement("hotosm-auth");
      this._container.appendChild(this._element);
    }

    const el = this._element;
    const { hankoUrl, redirectAfterLogin } = this.props;

    if (hankoUrl) {
      el.setAttribute("hanko-url", hankoUrl);
      el.setAttribute("base-path", hankoUrl);
    }
    if (redirectAfterLogin) {
      el.setAttribute("redirect-after-login", redirectAfterLogin);
      el.setAttribute("redirect-after-logout", redirectAfterLogin);
    }

    // Set mapping-check-url for onboarding flow
    const { mappingCheckUrl, appId } = this.props;
    if (mappingCheckUrl) {
      el.setAttribute("mapping-check-url", mappingCheckUrl);
    }
    if (appId) {
      el.setAttribute("app-id", appId);
    }
  }

  componentWillUnmount() {
    if (this._element && this._container) {
      this._container.removeChild(this._element);
      this._element = null;
    }
  }

  render() {
    return React.createElement("span", {
      ref: (el) => { this._container = el; },
      style: { display: "inline-block" }
    });
  }
}

export default HankoAuthButton;
