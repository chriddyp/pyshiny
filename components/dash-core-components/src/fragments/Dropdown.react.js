import {isNil, pluck, without, pick, isEmpty} from 'ramda';
import React, {useState, useCallback, useEffect, useMemo, useRef} from 'react';
import ReactDropdown from 'react-virtualized-select';
import createFilterOptions from 'react-select-fast-filter-options';
import 'react-virtualized-select/styles.css';
import '../components/css/react-virtualized@9.9.0.css';
import '../components/css/Dropdown.css';

import {propTypes} from '../components/Dropdown.react';
import {sanitizeOptions} from '../utils/optionTypes';
import isEqual from 'react-fast-compare';

// Custom tokenizer, see https://github.com/bvaughn/js-search/issues/43
// Split on spaces
const REGEX = /\s+/;
const TOKENIZER = {
    tokenize(text) {
        return text.split(REGEX).filter(
            // Filter empty tokens
            text => text
        );
    },
};

const RDProps = [
    'multi',
    'clearable',
    'searchable',
    'search_value',
    'placeholder',
    'disabled',
    'optionHeight',
    'maxHeight',
    'style',
    'className',
];

const Dropdown = props => {
    const {
        id,
        clearable,
        multi,
        options,
        setProps,
        search_value,
        style,
        value,
    } = props;
    const [optionsCheck, setOptionsCheck] = useState(null);
    const persistentOptions = useRef(null);

    const ctx = window.dash_component_api.useDashContext();
    const loading = ctx.useLoading();

    if (!persistentOptions || !isEqual(options, persistentOptions.current)) {
        persistentOptions.current = options;
    }

    const [sanitizedOptions, filterOptions] = useMemo(() => {
        let sanitized = sanitizeOptions(options);

        const indexes = ['strValue'];
        let hasElement = false,
            hasSearch = false;
        sanitized = Array.isArray(sanitized)
            ? sanitized.map(option => {
                  if (option.search) {
                      hasSearch = true;
                  }
                  if (React.isValidElement(option.label)) {
                      hasElement = true;
                  }
                  return {
                      ...option,
                      strValue: String(option.value),
                  };
              })
            : sanitized;

        if (!hasElement) {
            indexes.push('label');
        }
        if (hasSearch) {
            indexes.push('search');
        }

        return [
            sanitized,
            createFilterOptions({
                options: sanitized,
                tokenizer: TOKENIZER,
                indexes,
            }),
        ];
    }, [persistentOptions.current]);

    const onChange = useCallback(
        selectedOption => {
            if (multi) {
                let value;
                if (isNil(selectedOption)) {
                    value = [];
                } else {
                    value = pluck('value', selectedOption);
                }
                setProps({value});
            } else {
                let value;
                if (isNil(selectedOption)) {
                    value = null;
                } else {
                    value = selectedOption.value;
                }
                setProps({value});
            }
        },
        [multi]
    );

    const onInputChange = useCallback(
        search_value => setProps({search_value}),
        []
    );

    useEffect(() => {
        if (
            !search_value &&
            !isNil(sanitizedOptions) &&
            optionsCheck !== sanitizedOptions &&
            !isNil(value) &&
            !isEmpty(value)
        ) {
            const values = sanitizedOptions.map(option => option.value);
            if (multi && Array.isArray(value)) {
                const invalids = value.filter(v => !values.includes(v));
                if (invalids.length) {
                    setProps({value: without(invalids, value)});
                }
            } else {
                if (!values.includes(value)) {
                    setProps({value: null});
                }
            }
            setOptionsCheck(sanitizedOptions);
        }
    }, [sanitizedOptions, optionsCheck, multi, value]);

    return (
        <div
            id={id}
            className="dash-dropdown"
            style={style}
            data-dash-is-loading={loading || undefined}
        >
            <ReactDropdown
                filterOptions={filterOptions}
                options={sanitizedOptions}
                value={value}
                onChange={onChange}
                onInputChange={onInputChange}
                backspaceRemoves={clearable}
                deleteRemoves={clearable}
                inputProps={{autoComplete: 'off'}}
                {...pick(RDProps, props)}
            />
        </div>
    );
};

Dropdown.propTypes = propTypes;

export default Dropdown;
