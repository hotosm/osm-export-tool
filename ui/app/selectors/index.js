import qs from "query-string";

export const selectAuthToken = state => state.auth.token;

export const selectConfigurations = state => state.configurations;

export const selectExportRegion = (id, state) => state.hdx.exportRegions[id];

export const selectHDXError = state => state.hdx.error;

export const selectHDXStatus = state => state.hdx.status;

export const selectIntl = state => state.intl;

export const selectIsLoggedIn = state => state.auth.isLoggedIn;

export const selectIsLoggingIn = state => state.auth.isLoggingIn;

export const selectLocationHash = state => qs.parse(state.router.location.hash);

export const selectLocationOptions = state => state.hdx.locationOptions;

export const selectPermissions = state =>
  state.meta.user && state.meta.user.permissions;

export const selectRuns = state => state.exportRuns;

export const selectStatus = state => state.status;
