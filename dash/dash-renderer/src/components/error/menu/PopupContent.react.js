import React from 'react';

import {CallbackGraphContainer} from '../CallbackGraph/CallbackGraphContainer.react';
import {FrontEndErrorContainer} from '../FrontEnd/FrontEndErrorContainer.react';

export const PopupContent = ({
    popup,
    errors,
    backEndConnected,
    errCount,
    toggleErrors,
    showNotifications,
    setShowNotifications
}) => {
    let optOutDialog;
    if (showNotifications == null || showNotifications == undefined) {
        optOutDialog = (
            <div className='dash-debug-menu__version-opt-out'>
                <div className='dash-debug-menu__version-opt-out__text'>
                    <span>
                        {' '}
                        To check for the latest version, Dash sends requests to
                        Plotly.
                    </span>
                    <a href='https://dash.plotly.com/installation'>
                        Learn about what information is included in the request.
                    </a>
                </div>
                <div className='dash-debug-menu__version-opt-out__buttons-container'>
                    <button
                        className='dash-debug-menu__version-opt-out__button-secondary'
                        onClick={() => {
                            localStorage.setItem('showNotifications', true);
                            setShowNotifications(false);
                        }}
                    >
                        No Thanks
                    </button>
                    <button
                        className='dash-debug-menu__version-opt-out__button-primary'
                        onClick={() => {
                            localStorage.setItem('showNotifications', false);
                            setShowNotifications(true);
                        }}
                    >
                        Allow Requests
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className='dash-debug-menu__popup'>
            {optOutDialog}
            {popup == 'callbackGraph' ? <CallbackGraphContainer /> : undefined}
            {popup == 'errors' && errCount > 0 ? (
                <FrontEndErrorContainer
                    clickHandler={toggleErrors}
                    errors={errors}
                    connected={backEndConnected}
                />
            ) : undefined}
        </div>
    );
};
