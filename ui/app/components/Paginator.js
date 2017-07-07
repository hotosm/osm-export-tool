import React from "react";
import { Pagination } from "react-bootstrap";

export default ({ collection, getPage }) =>
  collection.pages > 1
    ? <Pagination
        prev
        next
        ellipsis
        boundaryLinks
        items={collection.pages}
        maxButtons={5}
        activePage={collection.activePage}
        onSelect={getPage}
      />
    : null;
