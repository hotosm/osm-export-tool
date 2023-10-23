import React, { Component } from "react";
import { FormattedMessage } from "react-intl";

class Banner extends Component {
  state = {
    consent: localStorage.getItem("accept-consent", undefined),
  };

  Close = (accept) => {
    localStorage.setItem("accept-consent", accept);
    this.setState({ consent: accept });

    let event = "forgetConsentGiven";
    if (accept === true) {
      event = "rememberConsentGiven";
    }

    // _paq object belongs to Matomo. Check v3.html page.
    window._paq.push([event]);
  };

  render() {
    if (this.state.consent) {
      return null;
    }

    return (
      <div className="banner">
        <h2>
          <FormattedMessage
            id="ui.banner.title"
            defaultMessage="About the information we collect"
          />
        </h2>

        <p>
          <FormattedMessage
            id="ui.banner.message"
            defaultMessage="We use cookies and similar technologies to recognize and analyze your visits, and measure traffic usage and activity. You can learn about how we use the data about your visit or information you provide reading our {policyLink}. By clicking I Agree , you consent to the use of cookies."
            values={{
              policyLink: (
                <a
                  href="https://hotosm.org/privacy"
                  className="red underline link fw6"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  privacy policy
                </a>
              ),
            }}
          />
        </p>
        <div className="banner-wrapper">
          <button onClick={() => this.Close(false)}>
            <FormattedMessage
              id="ui.banner.not_agree"
              defaultMessage="I do not agree"
            />
          </button>
          <button onClick={() => this.Close(true)}>
            <FormattedMessage id="ui.banner.agree" defaultMessage="I agree" />
          </button>
        </div>
      </div>
    );
  }
}

export default Banner;
