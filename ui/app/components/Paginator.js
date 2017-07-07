import React from "react";
import { Button } from "react-bootstrap";

export default ({ collection, getPage }) => {
  return (
    <div>
      {collection.total} results.
      {collection.nextPageUrl
        ? <Button
            style={{ float: "right" }}
            onClick={() => getPage(collection.nextPageUrl)}
          >
            Next
          </Button>
        : null}
      {collection.prevPageUrl
        ? <Button
            style={{ float: "right" }}
            onClick={() => getPage(collection.prevPageUrl)}
          >
            Previous
          </Button>
        : null}
    </div>
  );
};
