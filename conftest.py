# Minimum valid YAML code for the `Job.feature_selection` field.
# Replaces `FeatureSelection.example('simple')` from the `feature_selection` package, 
# # which is no longer installed (because it wasn't declared in `requirements.txt`).
SIMPLE_FEATURE_SELECTION = "buildings:\n  types:\n    - polygons\n  select:\n    - building\n"
