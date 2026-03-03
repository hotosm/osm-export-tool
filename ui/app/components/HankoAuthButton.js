import React from "react";

const MOBILE_BREAKPOINT = 768;

/**
 * React 15 wrapper for the <hotosm-auth> web component.
 *
 * React 15 doesn't properly handle custom element attributes (especially
 * hyphenated ones like hanko-url). This component uses DOM APIs to create
 * and configure the web component imperatively via a ref.
 */
class HankoAuthButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isMobile: window.innerWidth < MOBILE_BREAKPOINT,
    };
    this._handleResize = this._handleResize.bind(this);
  }

  componentDidMount() {
    window.addEventListener("resize", this._handleResize);
    this._renderWebComponent();
  }

  componentDidUpdate() {
    this._renderWebComponent();
  }

  _handleResize() {
    const isMobile = window.innerWidth < MOBILE_BREAKPOINT;
    if (isMobile !== this.state.isMobile) {
      this.setState({ isMobile });
    }
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

    const buttonVariant = this.props["button-variant"];
    const buttonColor = this.props["button-color"];
    if (buttonVariant) {
      el.setAttribute("button-variant", buttonVariant);
    }
    if (buttonColor) {
      el.setAttribute("button-color", buttonColor);
    }

    const { lang } = this.props;
    if (lang) {
      el.setAttribute("lang", lang);
    }

    el.setAttribute("display", this.state.isMobile ? "bar" : "default");
  }

  componentWillUnmount() {
    window.removeEventListener("resize", this._handleResize);
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
