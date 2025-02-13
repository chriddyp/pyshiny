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
    const cachedVersionInfo = localStorage.getItem('cachedNewDashVersion');
    const lastFetched = localStorage.getItem('lastFetched');
    if (
        lastFetched &&
        Date.now() - Number(lastFetched) < DAY_IN_MS &&
        cachedVersionInfo
    ) {
        return JSON.parse(cachedVersionInfo);
    } else {
        return fetch(dashVersionUrl, {
            method: 'POST',
            body: JSON.stringify({
                dash_version: currentDashVersion
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(body => {
                localStorage.setItem(
                    'cachedNewDashVersion',
                    JSON.stringify(body.version)
                );
                localStorage.setItem('lastFetched', Date.now());
                return body.version;
            });
    }
}

function shouldShowUpgradeNotification(currentDashVersion, newDashVersion) {
    const showNotifications = localStorage.getItem('showNotifications');
    const lastDismissed = localStorage.getItem('lastDismissed');
    const lastDismissedVersion = localStorage.getItem('lastDismissedVersion');
    if (
        currentDashVersion == newDashVersion ||
        showNotifications === 'false' ||
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

export const VersionInfo = ({config}) => {
    const [newDashVersion, setNewDashVersion] = useState(undefined);
    const [upgradeTooltipOpened, setUpgradeTooltipOpened] = useState(false);

    const setDontShowAgain = () => {
        // Set local storage to record the last dismissed notification
        localStorage.setItem('showNotifications', false);
        setUpgradeTooltipOpened(false);
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
        requestDashVersionInfo(
            config.dash_version,
            config.dash_version_url
        ).then(version => {
            setNewDashVersion(version);
        });
    }, []);

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
                newDashVersion
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
