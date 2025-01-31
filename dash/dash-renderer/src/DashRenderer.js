import React from 'react';
import ReactDOM from 'react-dom';

import AppProvider from './AppProvider.react';

class DashRenderer {
    constructor(hooks) {
        // TODO: move this to a more appropriate place?
        const head = document.head;
        const link1 = document.createElement('link');
        link1.rel = 'preconnect';
        link1.href = 'https://fonts.googleapis.com';
        head.appendChild(link1);

        const link2 = document.createElement('link');
        link2.rel = 'preconnect';
        link2.href = 'https://fonts.gstatic.com';
        link2.crossorigin = true;
        head.appendChild(link2);

        const link3 = document.createElement('link');
        link3.href =
            'https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap';
        link3.rel = 'stylesheet';
        head.appendChild(link3);

        // render Dash Renderer upon initialising!
        const container = document.getElementById('react-entry-point');

        if (ReactDOM.createRoot) {
            const root = ReactDOM.createRoot(container);
            root.render(<AppProvider hooks={hooks} />);
        } else {
            ReactDOM.render(<AppProvider hooks={hooks} />, container);
        }
    }
}

export {DashRenderer};
