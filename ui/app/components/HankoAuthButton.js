import React from "react";

const MOBILE_BREAKPOINT = 768;

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

  _bindCacheListeners() {
    this._onLogin = (e) => {
      localStorage.setItem("hotosm-auth-user", JSON.stringify(e.detail.user));
    };
    this._onLogout = () => {
      localStorage.removeItem("hotosm-auth-user");
    };
    this._element.addEventListener("hanko-login", this._onLogin);
    this._element.addEventListener("logout", this._onLogout);
  }

  _renderWebComponent() {
    if (!this._container) return;

    if (!this._element) {
      this._element = document.createElement("hotosm-auth");
      this._container.appendChild(this._element);
      this._bindCacheListeners();
      requestAnimationFrame(() => {
        const root = this._element.shadowRoot;
        if (root) {
          const style = document.createElement("style");
          style.textContent = ".dropdown-content { background-color: white !important; -webkit-transform: translateZ(0); }";
          root.appendChild(style);
        }
      });
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
    if (this._element) {
      this._element.removeEventListener("hanko-login", this._onLogin);
      this._element.removeEventListener("logout", this._onLogout);
      if (this._container) {
        this._container.removeChild(this._element);
      }
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
