import React, {useEffect, useState} from 'react';

import './VersionInfo.css';

const DAY_IN_MS = 86400000;

function compareVersions(v1, v2) {
    const v1Parts = v1.split('.').map(Number);
    const v2Parts = v2.split('.').map(Number);

    for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
        const part1 = v1Parts[i] || 0;
        const part2 = v2Parts[i] || 0;

        if (part1 > part2) return 1;
        if (part1 < part2) return -1;
    }

    return 0;
}

async function requestDashVersionInfo(currentDashVersion, dashVersionUrl) {
    return fetch(dashVersionUrl, {
        method: 'POST',
        body: JSON.stringify({
            dash_version: currentDashVersion
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json());
}

function shouldShowUpgradeNotification(
    currentDashVersion,
    newDashVersion,
    showNotifications
) {
    const lastDismissed = localStorage.getItem('lastDismissed');
    const lastDismissedVersion = localStorage.getItem('lastDismissedVersion');
    if (
        currentDashVersion == newDashVersion ||
        !showNotifications ||
        newDashVersion === undefined
    ) {
        return false;
    } else if (
        lastDismissed &&
        Date.now() - Number(lastDismissed) > DAY_IN_MS
    ) {
        return true;
    } else if (
        lastDismissedVersion &&
        !lastDismissed &&
        compareVersions(
            localStorage.getItem('lastDismissedVersion'),
            newDashVersion
        ) < 0
    ) {
        return true;
    } else {
        return !lastDismissed && !lastDismissedVersion;
    }
}

export const VersionInfo = ({
    config,
    showNotifications,
    setShowNotifications
}) => {
    const [upgradeInfo, setUpgradeInfo] = useState([]);
    const [upgradeTooltipOpened, setUpgradeTooltipOpened] = useState(false);

    const newDashVersion = upgradeInfo[0] ? upgradeInfo[0].version : undefined;

    const setDontShowAgain = () => {
        // Set local storage to record the last dismissed notification
        setUpgradeTooltipOpened(false);
        setShowNotifications(false);
    };

    const setRemindMeLater = () => {
        // Set local storage to record the last dismissed notification
        localStorage.setItem('lastDismissed', Date.now());
        setUpgradeTooltipOpened(false);
    };

    const setSkipThisVersion = () => {
        // Set local storage to record the last dismissed version
        localStorage.setItem('lastDismissedVersion', newDashVersion);
        setUpgradeTooltipOpened(false);
    };

    useEffect(() => {
        if (showNotifications) {
            requestDashVersionInfo(
                config.dash_version,
                config.dash_version_url
            ).then(body => {
                setUpgradeInfo(body);
            });
        }
    }, [showNotifications]);

    useEffect(() => {
        const hideUpgradeTooltip = e => {
            if (
                upgradeTooltipOpened &&
                !e.target.matches(
                    '.dash-debug-menu__version, .dash-debug-menu__version *'
                )
            ) {
                setUpgradeTooltipOpened(false);
            }
        };
        // Close the upgrade tooltip if the user clicks outside of it
        document.addEventListener('click', hideUpgradeTooltip);

        return () => document.removeEventListener('click', hideUpgradeTooltip);
    }, [upgradeTooltipOpened]);

    return (
        <div className='dash-debug-menu__version'>
            {upgradeTooltipOpened ? (
                <div className='dash-debug-menu__upgrade-tooltip'>
                    <a
                        target='_blank'
                        href='https://dash.plotly.com/installation'
                    >
                        Read details
                    </a>
                    <button onClick={setSkipThisVersion}>
                        Skip this version
                    </button>
                    <button onClick={setRemindMeLater}>
                        Remind me tomorrow
                    </button>
                    <button onClick={setDontShowAgain}>
                        Silence all version notifications
                    </button>
                </div>
            ) : null}
            <span>v{config.dash_version}</span>
            {shouldShowUpgradeNotification(
                config.dash_version,
                newDashVersion,
                showNotifications
            ) ? (
                <button
                    className='dash-debug-menu__upgrade-button'
                    onClick={() =>
                        setUpgradeTooltipOpened(!upgradeTooltipOpened)
                    }
                >
                    Dash update available - v{newDashVersion}
                </button>
            ) : null}
        </div>
    );
};
