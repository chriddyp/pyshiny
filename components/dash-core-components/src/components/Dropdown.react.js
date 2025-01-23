import PropTypes from 'prop-types';
import React, {Component, lazy, Suspense} from 'react';
import dropdown from '../utils/LazyLoader/dropdown';

const RealDropdown = lazy(dropdown);

/**
 * Dropdown is an interactive dropdown element for selecting one or more
 * items.
 * The values and labels of the dropdown items are specified in the `options`
 * property and the selected item(s) are specified with the `value` property.
 *
 * Use a dropdown when you have many options (more than 5) or when you are
 * constrained for space. Otherwise, you can use RadioItems or a Checklist,
 * which have the benefit of showing the users all of the items at once.
 */
export default class Dropdown extends Component {
    render() {
        return (
            <Suspense fallback={null}>
                <RealDropdown {...this.props} />
            </Suspense>
        );
    }
}

Dropdown.propTypes = {
    /**
     * An array of options {label: [string|number], value: [string|number]},
     * an optional disabled field can be used for each option
     */
    options: PropTypes.oneOfType([
        /**
         * Array of options where the label and the value are the same thing - [string|number|bool]
         */
        PropTypes.arrayOf(
            PropTypes.oneOfType([
                PropTypes.string,
                PropTypes.number,
                PropTypes.bool,
            ])
        ),
        /**
         * Simpler `options` representation in dictionary format. The order is not guaranteed.
         * {`value1`: `label1`, `value2`: `label2`, ... }
         * which is equal to
         * [{label: `label1`, value: `value1`}, {label: `label2`, value: `value2`}, ...]
         */
        PropTypes.object,
        /**
         * An array of options {label: [string|number], value: [string|number]},
         * an optional disabled field can be used for each option
         */
        PropTypes.arrayOf(
            PropTypes.exact({
                /**
                 * The option's label
                 */
                label: PropTypes.node.isRequired,

                /**
                 * The value of the option. This value
                 * corresponds to the items specified in the
                 * `value` property.
                 */
                value: PropTypes.oneOfType([
                    PropTypes.string,
                    PropTypes.number,
                    PropTypes.bool,
                ]).isRequired,

                /**
                 * If true, this option is disabled and cannot be selected.
                 */
                disabled: PropTypes.bool,

                /**
                 * The HTML 'title' attribute for the option. Allows for
                 * information on hover. For more information on this attribute,
                 * see https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title
                 */
                title: PropTypes.string,

                /**
                 * Optional search value for the option, to use if the label
                 * is a component or provide a custom search value different
                 * from the label. If no search value and the label is a
                 * component, the `value` will be used for search.
                 */
                search: PropTypes.string,
            })
        ),
    ]),

    /**
     * The value of the input. If `multi` is false (the default)
     * then value is just a string that corresponds to the values
     * provided in the `options` property. If `multi` is true, then
     * multiple values can be selected at once, and `value` is an
     * array of items with values corresponding to those in the
     * `options` prop.
     */
    value: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
        PropTypes.bool,
        PropTypes.arrayOf(
            PropTypes.oneOfType([
                PropTypes.string,
                PropTypes.number,
                PropTypes.bool,
            ])
        ),
    ]),

    /**
     * If true, the user can select multiple values
     */
    multi: PropTypes.bool,

    /**
     * If false and multi=true, then selecting a value will leave the menu open
     * to select more values
     */
    close_on_select: PropTypes.bool,

    /**
     * Whether or not the dropdown is "clearable", that is, whether or
     * not a small "x" appears on the right of the dropdown that removes
     * the selected value.
     */
    clearable: PropTypes.bool,

    /**
     * Whether to enable the searching feature or not
     */
    searchable: PropTypes.bool,

    /**
     * The value typed in the DropDown for searching.
     */
    search_value: PropTypes.string,

    /**
     * The grey, default text shown when no option is selected
     */
    placeholder: PropTypes.string,

    /**
     * If true, this dropdown is disabled and the selection cannot be changed.
     */
    disabled: PropTypes.bool,

    /**
     * height of each option. Can be increased when label lengths would wrap around
     */
    optionHeight: PropTypes.number,

    /**
     * height of the options dropdown.
     */
    maxHeight: PropTypes.number,

    /**
     * Defines CSS styles which will override styles previously set.
     */
    style: PropTypes.object,

    /**
     * className of the dropdown element
     */
    className: PropTypes.string,

    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * Dash-assigned callback that gets fired when the input changes
     */
    setProps: PropTypes.func,

    /**
     * Object that holds the loading state object coming from dash-renderer
     */
    loading_state: PropTypes.shape({
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
     * Used to allow user interactions in this component to be persisted when
     * the component - or the page - is refreshed. If `persisted` is truthy and
     * hasn't changed from its previous value, a `value` that the user has
     * changed while using the app will keep that change, as long as
     * the new `value` also matches what was given originally.
     * Used in conjunction with `persistence_type`.
     */
    persistence: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.string,
        PropTypes.number,
    ]),

    /**
     * Properties whose user interactions will persist after refreshing the
     * component or the page. Since only `value` is allowed this prop can
     * normally be ignored.
     */
    persisted_props: PropTypes.arrayOf(PropTypes.oneOf(['value'])),

    /**
     * Where persisted user changes will be stored:
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    persistence_type: PropTypes.oneOf(['local', 'session', 'memory']),
};

Dropdown.defaultProps = {
    clearable: true,
    disabled: false,
    multi: false,
    close_on_select: true,
    searchable: true,
    optionHeight: 35,
    maxHeight: 200,
    persisted_props: ['value'],
    persistence_type: 'local',
};

export const propTypes = Dropdown.propTypes;
export const defaultProps = Dropdown.defaultProps;
