import React, {Component} from 'react';
import DropZoneError from './DropZoneError';
import DropZoneDialog from './DropZoneDialog';

export class DropZone extends Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <DropZoneDialog />
                <DropZoneError />
            </div>
        )
    }
}

export default DropZone;

