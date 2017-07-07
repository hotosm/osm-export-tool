import types from "../actions";

export default function exportInfo(state = null, action) {
  switch (action.type) {
    case types.RECEIVED_EXPORT:
      return {
        ...action.job,
        simplified_geom: {
          ...action.job.simplified_geom,
          id: action.job.simplified_geom.id || Math.random()
        }
      };

    default:
      return state;
  }
}
