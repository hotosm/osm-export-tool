import React from "react";

import ExportAOI from "./aoi/ExportAOI";

export default ({
  aoi: {
    description: { input: descriptionInput },
    geomType: { input: geomTypeInput },
    title: { input: titleInput }
  },
  the_geom: { input: geojsonInput, meta }
}) => {
  return (
    <ExportAOI
      aoi={{
        description: descriptionInput.value,
        geojson: geojsonInput.value || null,
        geomType: geomTypeInput.value,
        title: titleInput.value
      }}
      clearAoiInfo={() => {
        descriptionInput.onChange();
        geojsonInput.onChange();
        geomTypeInput.onChange();
        titleInput.onChange();
      }}
      errors={meta.error}
      updateAoiInfo={(geojson, geomType, title, description) => {
        descriptionInput.onChange(description);
        geojsonInput.onChange(geojson.features[0].geometry);
        geomTypeInput.onChange(geomType);
        titleInput.onChange(title);
      }}
    />
  );
};
