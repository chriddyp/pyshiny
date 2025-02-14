/**
 * Generalized persistence for component props
 *
 * When users input new prop values, they can be stored and reapplied later,
 * when the component is recreated (changing `Tab` for example) or when the
 * page is reloaded (depending on `persistence_type`). Storage is tied to
 * component ID, and the prop values will not be stored with components
 * without an ID.
 *
 * Renderer handles the mechanics, but components must define a few props:
 *
 * - `persistence`: boolean, string, or number. For simple usage, set to `true`
 *   to enable persistence, omit or set `false` to disable. For more complex
 *   scenarios, use any truthy value, and change to a *different* truthy value
 *   when you want the persisted values cleared. (modeled off `uirevision` in)
 *   plotly.js
 *   Typically should have no default, but the other persistence props should
 *   have defaults, so all a user needs to do to enable persistence is set this
 *   one prop.
 *
 * - `persisted_props`: array of prop names or "nested prop IDs" allowed to
 *   persist. Normally should default to the full list of supported props,
 *   so they can all be enabled at once. The main exception to this is if
 *   there's a prop that *can* be persisted but most users wouldn't want this.
 *   A nested prop ID describes *part* of a prop to store. It must be
 *   "<propName>.<piece>" where propName is the prop that has this info, and
 *   piece may or may not map to the exact substructure being stored but is
 *   meaningful to the user. For example, in `dash_table`, `columns.name`
 *   stores `columns[i].name` for all columns `i`. Nested props also need
 *   entries in `persistenceTransforms` - see below.
 *
 * - `persistence_type`: one of "local", "session", or "memory", just like
 *   `dcc.Store`. But the default here should be "local" because the main use
 *   case is to maintain settings across reloads.
 *
 * If any `persisted_props` are nested prop IDs, the component should define a
 * class property (not a React prop) `persistenceTransforms`, as an object:
 * {
 *   [propName]: {
 *     [piece]: {
 *       extract: propValue => valueToStore,
 *       apply: (storedValue, propValue) => newPropValue
 *     }
 *   }
 * }
 * - `extract` turns a prop value into a reduced value to store.
 * - `apply` puts an extracted value back into the prop. Make sure this creates
 *   a new object rather than mutating `proValue`, and that if there are
 *   multiple `piece` entries for one `propName`, their `apply` functions
 *   commute - which should not be an issue if they extract and apply
 *   non-intersecting parts of the full prop.
 * You only need to define these for the props that need them.
 * It's important that `extract` pulls out *only* the relevant pieces of the
 * prop, because persistence is only maintained if the extracted value of the
 * prop before applying persistence is the same as it was before the user's
 * changes.
 */

import {
    equals,
    filter,
    forEach,
    keys,
    lensPath,
    mergeRight,
    set,
    type
} from 'ramda';
import {createAction} from 'redux-actions';

import Registry from './registry';
import {stringifyId} from './actions/dependencies';

export const storePrefix = '_dash_persistence.';

function err(e) {
    const error = typeof e === 'string' ? new Error(e) : e;

    return createAction('ON_ERROR')({
        type: 'frontEnd',
        error
    });
}

/*
 * Does a key fit this prefix? Must either be an exact match
 * or, if a separator is provided, a scoped match - exact prefix
 * followed by the separator (then anything else)
 */
function keyPrefixMatch(prefix, separator) {
    const fullStr = prefix + separator;
    const fullLen = fullStr.length;
    return key => key === prefix || key.substr(0, fullLen) === fullStr;
}

const UNDEFINED = 'U';
const _parse = val => (val === UNDEFINED ? undefined : JSON.parse(val || null));
const _stringify = val => (val === undefined ? UNDEFINED : JSON.stringify(val));

class WebStore {
    constructor(backEnd) {
        this._name = backEnd;
        this._storage = window[backEnd];
    }

    hasItem(key) {
        return this._storage.getItem(storePrefix + key) !== null;
    }

    getItem(key) {
        // note: _storage.getItem returns null on missing keys
        // and JSON.parse(null) returns null as well
        return _parse(this._storage.getItem(storePrefix + key));
    }

    _setItem(key, value) {
        // unprotected version of setItem, for use by tryGetWebStore
        this._storage.setItem(storePrefix + key, _stringify(value));
    }
    /*
     * In addition to the regular key->value to set, setItem takes
     * dispatch as a parameter, so it can report OOM to devtools
     */
    setItem(key, value, dispatch) {
        try {
            this._setItem(key, value);
        } catch (e) {
            dispatch(
                err(
                    `${key} failed to save in ${this._name}. Persisted props may be lost.`
                )
            );
            // TODO: at some point we may want to convert this to fall back
            // on memory, pulling out all persistence keys and putting them
            // in a MemStore that gets used from then onward.
        }
    }

    removeItem(key) {
        this._storage.removeItem(storePrefix + key);
    }

    /*
     * clear matching keys matching (optionally followed by a dot and more
     * characters) - or all keys associated with this store if no prefix.
     */
    clear(keyPrefix) {
        const fullPrefix = storePrefix + (keyPrefix || '');
        const keyMatch = keyPrefixMatch(fullPrefix, keyPrefix ? '.' : '');
        const keysToRemove = [];
        // 2-step process, so we don't depend on any particular behavior of
        // key order while removing some
        for (let i = 0; i < this._storage.length; i++) {
            const fullKey = this._storage.key(i);
            if (keyMatch(fullKey)) {
                keysToRemove.push(fullKey);
            }
        }
        forEach(k => this._storage.removeItem(k), keysToRemove);
    }
}

class MemStore {
    constructor() {
        this._data = {};
    }

    hasItem(key) {
        return key in this._data;
    }

    getItem(key) {
        // run this storage through JSON too so we know we get a fresh object
        // each retrieval
        return _parse(this._data[key]);
    }

    setItem(key, value) {
        this._data[key] = _stringify(value);
    }

    removeItem(key) {
        delete this._data[key];
    }

    clear(keyPrefix) {
        if (keyPrefix) {
            forEach(
                key => delete this._data[key],
                filter(keyPrefixMatch(keyPrefix, '.'), keys(this._data))
            );
        } else {
            this._data = {};
        }
    }
}

// Make a string 2^16 characters long (*2 bytes/char = 130kB), to test storage.
// That should be plenty for common persistence use cases,
// without getting anywhere near typical browser limits
const pow = 16;
function longString() {
    let s = 'Spam';
    for (let i = 2; i < pow; i++) {
        s += s;
    }
    return s;
}

export const stores = {
    memory: new MemStore()
    // Defer testing & making local/session stores until requested.
    // That way if we have errors here they can show up in devtools.
};

const backEnds = {
    local: 'localStorage',
    session: 'sessionStorage'
};

function tryGetWebStore(backEnd, dispatch) {
    const store = new WebStore(backEnd);
    const fallbackStore = stores.memory;
    const storeTest = longString();
    const testKey = storePrefix + 'x.x';
    try {
        store._setItem(testKey, storeTest);
        if (store.getItem(testKey) !== storeTest) {
            dispatch(
                err(`${backEnd} init failed set/get, falling back to memory`)
            );
            return fallbackStore;
        }
        store.removeItem(testKey);
        return store;
    } catch (e) {
        dispatch(
            err(`${backEnd} init first try failed; clearing and retrying`)
        );
    }
    try {
        store.clear();
        store._setItem(testKey, storeTest);
        if (store.getItem(testKey) !== storeTest) {
            throw new Error('nope');
        }
        store.removeItem(testKey);
        dispatch(err(`${backEnd} init set/get succeeded after clearing!`));
        return store;
    } catch (e) {
        dispatch(err(`${backEnd} init still failed, falling back to memory`));
        return fallbackStore;
    }
}

function getStore(type, dispatch) {
    if (!stores[type]) {
        stores[type] = tryGetWebStore(backEnds[type], dispatch);
    }
    return stores[type];
}

const noopTransform = {
    extract: propValue => propValue,
    apply: (storedValue, _propValue) => storedValue
};

const getTransform = (element, propName, propPart) => {
    if (
        element.persistenceTransforms &&
        element.persistenceTransforms[propName]
    ) {
        if (propPart) {
            return element.persistenceTransforms[propName][propPart];
        }
        return element.persistenceTransforms[propName];
    }
    return noopTransform;
};

const getValsKey = (id, persistedProp, persistence) =>
    `${stringifyId(id)}.${persistedProp}.${JSON.stringify(persistence)}`;

const getProps = layout => {
    const {props, type, namespace} = layout;
    if (!type || !namespace) {
        // not a real component - just need the props for recursion
        return {props};
    }
    const {id, persistence} = props;

    const element = Registry.resolve(layout);
    const getVal = prop => props[prop] || (element.defaultProps || {})[prop];
    const persisted_props = getVal('persisted_props');
    const persistence_type = getVal('persistence_type');
    const canPersist = id && persisted_props && persistence_type;

    return {
        canPersist,
        id,
        props,
        element,
        persistence,
        persisted_props,
        persistence_type
    };
};

export function recordUiEdit(layout, newProps, dispatch) {
    if (newProps === undefined) {
        return;
    }

    const {
        canPersist,
        id,
        props,
        element,
        persistence,
        persisted_props,
        persistence_type
    } = getProps(layout);

    if (canPersist && persistence) {
        forEach(persistedProp => {
            const [propName, propPart] = persistedProp.split('.');
            if (newProps[propName] !== undefined) {
                const storage = getStore(persistence_type, dispatch);
                const {extract} = getTransform(element, propName, propPart);
                const valsKey = getValsKey(id, persistedProp, persistence);

                let originalVal = storage.hasItem(valsKey)
                    ? storage.getItem(valsKey)[1]
                    : extract(props[propName]);
                let newVal = extract(newProps[propName]);

                storage.setItem(valsKey, [newVal, originalVal], dispatch);
            }
        }, persisted_props);
    }

    // Recursively record UI edits for children
    const {children} = props;
    if (Array.isArray(children)) {
        children.forEach((child, i) => {
            if (
                type(child) === 'Object' &&
                child.props &&
                newProps['children'] !== undefined
            ) {
                recordUiEdit(child, newProps['children'][i]['props'], dispatch);
            }
        });
    } else if (
        type(children) === 'Object' &&
        children.props &&
        newProps['children'] !== undefined
    ) {
        recordUiEdit(children, newProps['children']['props'], dispatch);
    }
}

/*
 * Used for entire layouts (on load) or partial layouts (from children
 * callbacks) to apply previously-stored UI edits to components
 */
export function applyPersistence(layout, dispatch) {
    if (type(layout) !== 'Object' || !layout.props) {
        return layout;
    }

    return persistenceMods(layout, layout, [], dispatch);
}

const UNDO = true;
function modProp(key, storage, element, props, persistedProp, update, undo) {
    if (storage.hasItem(key)) {
        const [newVal, originalVal] = storage.getItem(key);
        const fromVal = undo ? newVal : originalVal;
        const toVal = undo ? originalVal : newVal;
        const [propName, propPart] = persistedProp.split('.');
        const transform = getTransform(element, propName, propPart);

        if (equals(fromVal, transform.extract(props[propName]))) {
            update[propName] = transform.apply(
                toVal,
                propName in update ? update[propName] : props[propName]
            );
        } else {
            // clear this saved edit - we've started with the wrong
            // value for this persistence ID
            storage.removeItem(key);
        }
    }
}

function persistenceMods(layout, component, path, dispatch) {
    const {
        canPersist,
        id,
        props,
        element,
        persistence,
        persisted_props,
        persistence_type
    } = getProps(component);

    let layoutOut = layout;
    if (canPersist && persistence) {
        const storage = getStore(persistence_type, dispatch);
        const update = {};
        forEach(
            persistedProp =>
                modProp(
                    getValsKey(id, persistedProp, persistence),
                    storage,
                    element,
                    props,
                    persistedProp,
                    update
                ),
            persisted_props
        );

        for (const propName in update) {
            layoutOut = set(
                lensPath(path.concat('props', propName)),
                update[propName],
                layoutOut
            );
        }
    }

    // recurse inward
    const {children} = props;
    if (Array.isArray(children)) {
        children.forEach((child, i) => {
            if (type(child) === 'Object' && child.props) {
                layoutOut = persistenceMods(
                    layoutOut,
                    child,
                    path.concat('props', 'children', i),
                    dispatch
                );
            }
        });
    } else if (type(children) === 'Object' && children.props) {
        layoutOut = persistenceMods(
            layoutOut,
            children,
            path.concat('props', 'children'),
            dispatch
        );
    }
    return layoutOut;
}

/*
 * When we receive new explicit props from a callback,
 * these override UI-driven edits of those exact props
 * but not for props nested inside children
 */
export function prunePersistence(layout, newProps, dispatch) {
    const {
        canPersist,
        id,
        props,
        persistence,
        persisted_props,
        persistence_type,
        element
    } = getProps(layout);

    const getFinal = (propName, prevVal) =>
        propName in newProps ? newProps[propName] : prevVal;
    const finalPersistence = getFinal('persistence', persistence);

    if (!canPersist || !(persistence || finalPersistence)) {
        return newProps;
    }

    const finalPersistenceType = getFinal('persistence_type', persistence_type);
    const finalPersistedProps = getFinal('persisted_props', persisted_props);
    const persistenceChanged =
        finalPersistence !== persistence ||
        finalPersistenceType !== persistence_type ||
        finalPersistedProps !== persisted_props;

    const notInNewProps = persistedProp =>
        !(persistedProp.split('.')[0] in newProps);

    const update = {};

    let depersistedProps = props;

    if (persistenceChanged && persistence) {
        // clear previously-applied persistence
        const storage = getStore(persistence_type, dispatch);
        forEach(
            persistedProp =>
                modProp(
                    getValsKey(id, persistedProp, persistence),
                    storage,
                    element,
                    props,
                    persistedProp,
                    update,
                    UNDO
                ),
            filter(notInNewProps, persisted_props)
        );
        depersistedProps = mergeRight(props, update);
    }

    if (finalPersistence) {
        const finalStorage = getStore(finalPersistenceType, dispatch);

        if (persistenceChanged) {
            // apply new persistence
            forEach(
                persistedProp =>
                    modProp(
                        getValsKey(id, persistedProp, finalPersistence),
                        finalStorage,
                        element,
                        depersistedProps,
                        persistedProp,
                        update
                    ),
                filter(notInNewProps, finalPersistedProps)
            );
        }

        // now the main point - clear any edit of a prop that changed
        // note that this is independent of the new prop value.
        const transforms = element.persistenceTransforms || {};
        for (const propName in newProps) {
            const propTransforms = transforms[propName];
            if (propTransforms) {
                for (const propPart in propTransforms) {
                    finalStorage.removeItem(
                        getValsKey(
                            id,
                            `${propName}.${propPart}`,
                            finalPersistence
                        )
                    );
                }
            } else {
                finalStorage.removeItem(
                    getValsKey(id, propName, finalPersistence)
                );
            }
        }
    }
    return persistenceChanged ? mergeRight(newProps, update) : newProps;
}
