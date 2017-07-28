import React from "react";
import { Link } from "react-router-dom";

export default () =>
  <div className="help">
    <ol className="breadcrumb">
      <li>
        <Link to="/help">Help</Link>
      </li>
      <li className="active">Export Tool API</li>
    </ol>

    <h2>Export Tool API</h2>
    <div className="well">
      <p>
        The Export Tool exposes a web API that can be used to create and manage
        jobs.
      </p>
    </div>

    <h3>Authorization</h3>
    <div className="well">
      <p>User authentication and authorization is a two-step process.</p>
      <p>
        The Export Tool requires that users log into OpenStreetMap using{" "}
        <a href="https://oauth.net/1/">OAuth 1.0a</a> (you don't need to know
        this). This provides user identity, specifically an OSM username to
        associate with exports. You generally don't need to care about this,
        except to know that usernames are the same as on OSM.
      </p>
      <p>
        Export client authorization is handled using{" "}
        <a href="https://oauth.net/2/">OAuth 2.0</a>. In a nutshell, client
        applications (such as this one) request access (in the form of "scopes";
        "read" / "write" in this case) from the API, identifying themselves with
        a client ID. Users are prompted to authorize the application after being
        redirected. If they grant access, the Export Tool will mint a "bearer
        token" and provide it back to the client application for use when making
        API requests.
      </p>
      <p>
        When making requests to protected resources,{" "}
        <code>Authorization: Bearer &lt;token&gt;</code> can be included in the
        HTTP request headers, both to identify the user and to authorize the
        application.
      </p>
      <p>
        More information on the Export Tool's implementation of OAuth 2.0 can be
        found in the{" "}
        <a href="https://django-oauth-toolkit.readthedocs.io/en/latest/">
          Django OAuth Toolkit documentation
        </a>. For Export Tool purposes, bearer tokens don't expire, but{" "}
        <a href="/o/authorized_tokens/">can be revoked</a>.
      </p>
      <p>
        Client applications can be created and managed using the{" "}
        <a href="/o/applications/">application management console</a>.
      </p>
    </div>

    <h3>Endpoints</h3>
    <div className="well">
      <p>
        This is an incomplete list of API endpoints. For more information,
        please consult the{" "}
        <a href="https://github.com/hotosm/osm-export-tool2/tree/master/api">
          source code on GitHub
        </a>{" "}
        or explore <a href="/api/">the auto-generated API documentation</a>.
      </p>
      <ul>
        <li>
          <a href="/api/jobs">
            Job management -- "jobs" define the properties and area of interest
            of an export
          </a>
        </li>
        <li>
          <a href="/api/runs">
            Run management -- "runs" represent each time a job is evaluated
          </a>
        </li>
      </ul>
    </div>
  </div>;
