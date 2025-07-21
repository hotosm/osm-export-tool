import React, { Component } from "react";

class Message extends Component {
  constructor(props) {
    super(props);
    // Use "messageClosed" as the key to check if the message was previously closed
    const messageClosed = localStorage.getItem("messageClosed") === "true";
    this.state = {
      isVisible: !messageClosed,
    };
  }

  handleClose = () => {
    this.setState({ isVisible: false });
    // When closing, set "messageClosed" in localStorage to "true"
    localStorage.setItem("messageClosed", "true");
  };

  render() {
    if (!this.state.isVisible) {
      return null;
    }
    return (
        <div className="banner" style={{ backgroundColor: "#ffcc00", color: "black", textAlign: "center", padding: "10px", position: "relative" }}>
          <p>We are aware that you are not being able to login , We are actively working on it and will provide fix soon</p>
          <button onClick={this.handleClose} style={{ position: "absolute", top: "5px", right: "10px", cursor: "pointer" }}>
            ×
          </button>
        </div>
      );
  }
}

export default Message;
