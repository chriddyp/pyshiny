'use strict';

/**
 * Generates React components from a newline-separated list of HTML elements.
 */

const fs = require('fs');
const path = require('path');

const srcPath = '../src/components';
const attributesPath = './data/attributes.json';

// Based off https://github.com/iandevlin/html-attributes/blob/master/boolean-attributes.json
const BOOLEAN_PROPERTIES = [
    'allowFullScreen',
    'allowPaymentRequest',
    'async',
    'autoFocus',
    'autoPlay',
    'checked',
    'controls',
    'default',
    'defer',
    'disabled',
    'formNoValidate',
    'hidden',
    'isMap',
    'itemScope',
    'loop',
    'multiple',
    'muted',
    'noModule',
    'noValidate',
    'open',
    'playsInline',
    'readonly',
    'required',
    'reversed',
    'selected',
    'typeMustMatch'
];

// Based off reading through
// "Some of the DOM attributes supported by React include" section in
// https://reactjs.org/docs/dom-elements.html
const NUMERIC_PROPERTIES = [
    'width',
    'height',
    'marginWidth',
    'marginHeight',
    'max',
    'maxLength',
    'min',
    'minLength',
    'rows',
    'rowSpan',
    'cols',
    'colSpan',
    'size',
    'step',
    'tabIndex'
];

const PROP_TYPES = {
    _default: 'string',
    style: 'object',
};
BOOLEAN_PROPERTIES.forEach(property => {
    let capitalizationOptions;
    if (property.toLowerCase() !== property) {
        capitalizationOptions = `${property}', '${property.toLowerCase()}', '${property.toUpperCase()}`
    } else {
        capitalizationOptions = `${property}', '${property.toUpperCase()}`
    }
    PROP_TYPES[property] = (
        'oneOfType([\n' +
        `        PropTypes.oneOf(['${capitalizationOptions}']),\n` +
        '        PropTypes.bool\n' +
        '     ])'
    );
})
NUMERIC_PROPERTIES.forEach(property => {
    PROP_TYPES[property] = (
        'oneOfType([\n' +
        '        PropTypes.string,\n' +
        '        PropTypes.number\n' +
        '     ])'
    );

})

function bail(message) {
    console.error('Error: ' + message);
    process.exit(1);
}

function upperCase(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function nameComponent(elementName) {
    const reservedWords = {
        'object': 'ObjectEl',
        'map': 'MapEl'
    };

    return reservedWords[elementName] || upperCase(elementName);
}

function generatePropTypes(element, attributes) {
    const elements = attributes.elements;
    // Always add the list of global attributes.
    const supportedAttributes = elements[element] ?
        elements[element].concat(elements.Globalattribute) :
        elements.Globalattribute;

    return `
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    'id': PropTypes.string,

    /**
     * The children of this component
     */
    'children': PropTypes.node,

    /**
     * An integer that represents the number of times
     * that this element has been clicked on.
     */
    'n_clicks': PropTypes.number,

    /**
     * An integer that represents the time (in ms since 1970)
     * at which n_clicks changed. This can be used to tell
     * which button was changed most recently.
     */
    'n_clicks_timestamp': PropTypes.number,

    /**
     * When True, this will disable the n_clicks prop.  Use this to remove
     * event listeners that may interfere with screen readers.
     */
    'disable_n_clicks': PropTypes.bool,

    /**
     * A unique identifier for the component, used to improve
     * performance by React.js while rendering components
     * See https://reactjs.org/docs/lists-and-keys.html for more info
     */
    'key': PropTypes.string,

    /**
     * A wildcard data attribute
     */
    'data-*': PropTypes.string,

    /**
     * A wildcard aria attribute
     */
    'aria-*': PropTypes.string,` +

        supportedAttributes.reduce((propTypes, attributeName) => {
            const attribute = attributes.attributes[attributeName];
            const propType = PROP_TYPES[attributeName] || PROP_TYPES._default;
            if (attributeName === 'id') {
                return propTypes;
            }
            return propTypes + `

    /**
     *${attribute.description ? ' ' + attribute.description : ''}
     */
    '${attributeName}': PropTypes.${propType},`;
        }, '') + `

    /**
     * Object that holds the loading state object coming from dash-renderer
     */
    'loading_state': PropTypes.shape({
        /**
         * Determines if the component is loading or not
         */
        is_loading: PropTypes.bool,
        /**
         * Holds which property is loading
         */
        prop_name: PropTypes.string,
        /**
         * Holds the name of the component that is loading
         */
        component_name: PropTypes.string,
    }),

    /**
     * Dash-assigned callback that gets fired when the element is clicked.
     */
    'setProps': PropTypes.func`
}

const obsoleteDoc = element => `
 * OBSOLETE: <${element}> is included for completeness, but should be avoided
 * as it is not supported by any modern browsers.`;

const customDocs = {
    basefont: `
 * OBSOLETE: <basefont> is included for completeness, but should be avoided
 * as it is only supported by Internet Explorer.`,
    blink: obsoleteDoc('blink'),
    command: obsoleteDoc('command'),
    element: obsoleteDoc('element'),
    isindex: obsoleteDoc('isindex'),
    keygen: `
 * DEPRECATED: <keygen> is included for completeness, but should be avoided
 * as it is not supported by all browsers and may be removed at any time from
 * those that do support it.`,
    listing: obsoleteDoc('listing') + ' Use <pre> or <code> instead.',
    marquee: `
 * DEPRECATED: <marquee> is included for completeness, but should be avoided
 * as browsers may remove it at any time.`,
    meta: `
 * CAUTION: <meta> is included for completeness, but generally will not behave
 * as expected since <meta> tags should be static HTML content in the <head> of
 * the document. Dash components are dynamic <body> content.`,
    multicol: obsoleteDoc('multicol'),
    nextid: obsoleteDoc('nextid'),
    output: `
 * CAUTION: <output> is included for completeness, but its typical usage
 * requires the oninput attribute of the enclosing <form> element, which
 * is not accessible to Dash.`,
    script: `
 * CAUTION: <script> is included for completeness, but you cannot execute
 * JavaScript code by providing it to a <script> element. Use a clientside
 * callback for this purpose instead.`,
    plaintext: `
 * OBSOLETE: <plaintext> is included for completeness, but should be avoided
 * as browsers may remove it at any time, and its behavior when added
 * dynamically by Dash is not what it would be statically on page load.
 * Use <pre> or <code> instead.`,
    shadow: `
 * DEPRECATED: <shadow> is included for completeness, but should be avoided
 * as it is not supported by all browsers and may be removed at any time from
 * those that do support it.`,
    spacer: obsoleteDoc('spacer'),
    title: `
 * CAUTION: <title> is included for completeness, but is not expected to
 * do anything outside of <head>. Dash components are always created in the
 * <body>.`
};

const customImportsForComponents = {};

function createXSSProtection(propName) {
    return `
    const cleanUrl = window.dash_clientside.clean_url;
    const ${propName} = React.useMemo(() => props.${propName} && cleanUrl(props.${propName}), [props.${propName}]);
    
    if (${propName}) {
        extraProps.${propName} = ${propName};
    }
    
    React.useEffect(() => {
        if (${propName} && ${propName} !== props.${propName}) {
            props.setProps({_dash_error: new Error(\`Dangerous link detected: \${props.${propName}}\`)})
        }
    }, [props.${propName}, ${propName}]);
    `
}


const customCodesForComponents = {
    a: createXSSProtection('href'),
    form: createXSSProtection('action'),
    iframe: createXSSProtection('src'),
    object: createXSSProtection('data'),
    embed: createXSSProtection('src'),
    button: createXSSProtection('formAction')
}

function generateComponent(Component, element, attributes) {
    const propTypes = generatePropTypes(element, attributes);

    const customImport = customImportsForComponents[element] || '';
    const customDoc = customDocs[element] ? ('\n *' + customDocs[element] + '\n *') : '';

    const customCode = customCodesForComponents[element] || '';

    return `
import React from 'react';
import PropTypes from 'prop-types';
import {omit} from 'ramda';
${customImport}

/**
 * ${Component} is a wrapper for the <${element}> HTML5 element.${customDoc}
 * For detailed attribute info see:
 * https://developer.mozilla.org/en-US/docs/Web/HTML/Element/${element}
 */
const ${Component} = ({n_clicks = 0, n_clicks_timestamp = -1, ...props}) => {
    const extraProps = {};
    if(props.loading_state && props.loading_state.is_loading) {
        extraProps['data-dash-is-loading'] = true;
    }
${customCode}
     /* remove unnecessary onClick event listeners  */
    const isStatic = props.disable_n_clicks || !props.id;
    return (
        <${element}
            {...(!isStatic && {onClick:
            () => props.setProps({
                n_clicks: n_clicks + 1,
                n_clicks_timestamp: Date.now()
            })
            })}
            {...omit(['n_clicks', 'n_clicks_timestamp', 'loading_state', 'setProps', 'disable_n_clicks'], props)}
            {...extraProps}
        >
            {props.children}
        </${element}>
    );
};


${Component}.propTypes = {${propTypes}
};

export default ${Component};
`;
}

/**
 * Generate an object with Component names as keys, component definitions as
 * values
 */
function generateComponents(list, attributes) {
    return list.reduce((componentMap, element) => {
        const componentName = nameComponent(element);
        const Component = generateComponent(componentName, element, attributes);

        componentMap[componentName] = Component;

        return componentMap;
    }, {});
}

/**
 * Writes component definitions to disk.
 */
function writeComponents(components, destination) {
    console.log(`Writing ${Object.keys(components).length} component files to ${srcPath}.`);
    let componentPath;
    for (const Component in components) {
        componentPath = path.join(destination, `${Component}.react.js`);
        fs.mkdirSync(path.join(destination), { recursive: true });
        fs.writeFileSync(componentPath, components[Component]);
    }
}


// Get first command-line argument
const listPath = process.argv[2];

if (!listPath) {
    bail('Must specify an element list.');
}

// Read the list of elements
const list = fs
    .readFileSync(listPath, 'utf8')
    .split('\n')
    .filter(item => Boolean(item));

// Get the mapping of attributes to elements
const attributes = JSON.parse(fs.readFileSync(attributesPath, 'utf-8'));

const components = generateComponents(list, attributes);

writeComponents(components, srcPath);

console.log('Done.');
