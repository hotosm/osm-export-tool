import types from '../actions/actionTypes';
import initialState from './initialState';

export function configurationsReducer(state = initialState.configurations, action) {
  switch(action.type) {
    case types.RECEIVED_CONFIGURATIONS_LIST:
      return action.configurations
  }
  return state;
}
