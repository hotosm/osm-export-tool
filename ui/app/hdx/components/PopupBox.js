import React, {Component} from 'react';
import styles from '../styles/PopupBox.css';

export class PopupBox extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                {this.props.show ? 
                <div className={styles.container}>
                    <div className={styles.titlebar}>
                        <span className={styles.title}><strong>{this.props.title}</strong></span>
                        <button onClick={this.props.onExit} className={styles.exit}>
                            <i className={"material-icons"}>clear</i>
                        </button>
                    </div>
                    <div className={styles.body}>
                        {this.props.children}
                    </div>
                    <div className={styles.footer}/>
                </div>
                : null}
            </div>
        )
    }
}

PopupBox.propTypes = {
    show: React.PropTypes.bool,
    title: React.PropTypes.string,
    onExit: React.PropTypes.func,
}

export default PopupBox;
