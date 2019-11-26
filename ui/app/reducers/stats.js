import types from "../actions";

const initialState = {
  jobs: []
};

export default function stats(state = initialState,{type,data}) {
  switch (type) {
    case types.RECEIVED_STATS:
      return {
        ...state,
        jobs:data.jobs,
        jobs_count:data.jobs_count,
        users_count:data.users_count
      };

    default:
      return state;
  }
}
