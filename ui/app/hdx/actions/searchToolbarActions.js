import axios from 'axios'
const isEqual = require('lodash/isEqual');


export function getGeonames(query) {
    return (dispatch) => {
        dispatch({type: "FETCHING_GEONAMES"});
        return axios.get('/request_geonames', {
            params: {
                q: query
            }
        }).then(response => {
            return response.data;
        }).then(responseData => {
            let data = responseData.geonames;
            let geonames = []
            for (var i = 0; i < data.length; i++) {
                if ((data[i].bbox && !isEqual(data[i].bbox, {})) || (data.lat && data.lng)) {
                    geonames.push(data[i]);
                }
            }
            dispatch({type: "RECEIVED_GEONAMES", geonames: geonames});
        }).catch(error => {
            dispatch({type: "GEONAMES_ERROR", error: error});
        });
    }
}
