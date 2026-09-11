import React from "react";

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
      this._element = document.createElement("hot-tool-menu");
      this._container.appendChild(this._element);
    }

    const el = this._element;
    const { showLogos } = this.props;

    if (showLogos) {
      el.setAttribute("show-logos", "");
    } else {
      el.removeAttribute("show-logos");
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
