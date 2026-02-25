import React from "react";

/**
 * React 15 wrapper for the <tool-menu> web component.
 *
 * Uses imperative DOM creation because React 15 doesn't handle
 * hyphenated custom element attributes (show-logos) properly.
 */
class ToolMenu extends React.Component {
  componentDidMount() {
    this._renderWebComponent();
  }

  componentDidUpdate() {
    this._renderWebComponent();
  }

  _renderWebComponent() {
    if (!this._container) return;

    if (!this._element) {
      this._element = document.createElement("hotosm-tool-menu");
      this._container.appendChild(this._element);
    }

    const el = this._element;
    const { showLogos, lang } = this.props;

    if (showLogos) {
      el.setAttribute("show-logos", "");
    } else {
      el.removeAttribute("show-logos");
    }

    if (lang) {
      el.setAttribute("lang", lang);
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

export default ToolMenu;
