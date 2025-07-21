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
        <p>If you are experiencing issues logging in after our fixes, please logout and login again to resolve the issue.</p>
        <button onClick={this.handleClose} style={{ position: "absolute", top: "5px", right: "10px", cursor: "pointer" }}>
          ×
        </button>
      </div>
    );
  }
}

export default Message;
