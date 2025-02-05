
/**remove dcc.logoutbutton completely and
used fetch API to send a POST request to/logout and handle logout action using 
javascript without a form and styled the button while keeping it functional

import React from 'react';
import PropTypes from 'prop-types';

import './css/logout.css';

/**
 * LogoutButton component to handle user logout.
 * Sends a POST request to the provided `logoutUrl` when clicked.
 */
export default class LogoutButton extends React.Component {
    constructor(props) {
        super(props);
        this.handleLogout = this.handleLogout.bind(this);
    }

    handleLogout() {
        const { logoutUrl, onLogout } = this.props;

        fetch(logoutUrl, { method: 'POST', credentials: 'include' })
            .then(response => {
                if (response.ok) {
                    if (onLogout) {
                        onLogout(); // Trigger callback if provided
                    } else {
                        window.location.href = '/'; // Redirect to home by default
                    }
                } else {
                    console.error('Logout failed:', response.statusText);
                }
            })
            .catch(error => console.error('Logout error:', error));
    }

    render() {
        const { id, label, className, style, loadingState } = this.props;

        return (
            <button
                id={id}
                className={`dash-logout-btn ${className || ''}`}
                style={style}
                onClick={this.handleLogout}
                disabled={loadingState && loadingState.is_loading}
            >
                {label}
            </button>
        );
    }
}

// Default Props
LogoutButton.defaultProps = {
    label: 'Logout',
    logoutUrl: '/logout', // Default logout endpoint
};

// Prop Types
LogoutButton.propTypes = {
    id: PropTypes.string,
    label: PropTypes.string,
    logoutUrl: PropTypes.string.isRequired,
    className: PropTypes.string,
    style: PropTypes.object,
    onLogout: PropTypes.func, // Callback after logout
    loadingState: PropTypes.shape({
        is_loading: PropTypes.bool,
    }),
};