import {once, path} from 'ramda';
import {createAction} from 'redux-actions';
import {addRequestedCallbacks} from './callbacks';
import {getAppState} from '../reducers/constants';
import {getAction} from './constants';
import cookie from 'cookie';
import {validateCallbacksToLayout} from './dependencies';
import {includeObservers, getLayoutCallbacks} from './dependencies_ts';
import {getPath} from './paths';
import {recordUiEdit} from '../persistence';

export const onError = createAction(getAction('ON_ERROR'));
export const setAppLifecycle = createAction(getAction('SET_APP_LIFECYCLE'));
export const setConfig = createAction(getAction('SET_CONFIG'));
export const addHttpHeaders = createAction(getAction('ADD_HTTP_HEADERS'));
export const setGraphs = createAction(getAction('SET_GRAPHS'));
export const setHooks = createAction(getAction('SET_HOOKS'));
export const setLayout = createAction(getAction('SET_LAYOUT'));
export const setPaths = createAction(getAction('SET_PATHS'));
export const setRequestQueue = createAction(getAction('SET_REQUEST_QUEUE'));

// Change the variable name of the action
export const onPropChange = createAction(getAction('ON_PROP_CHANGE'));

export function updateProps(payload) {
    return (dispatch, getState) => {
        const component = path(payload.itempath, getState().layout);
        recordUiEdit(component, payload.props, dispatch);
        dispatch(onPropChange(payload));
    };
}

export const dispatchError = dispatch => (message, lines) =>
    dispatch(
        onError({
            type: 'backEnd',
            error: {message, html: lines.join('\n')}
        })
    );

export function hydrateInitialOutputs() {
    return function (dispatch, getState) {
        validateCallbacksToLayout(getState(), dispatchError(dispatch));
        triggerDefaultState(dispatch, getState);
        dispatch(setAppLifecycle(getAppState('HYDRATED')));
    };
}

/* eslint-disable-next-line no-console */
const logWarningOnce = once(console.warn);

export function getCSRFHeader() {
    try {
        return {
            'X-CSRFToken': cookie.parse(document.cookie)._csrf_token
        };
    } catch (e) {
        logWarningOnce(e);
        return {};
    }
}

function triggerDefaultState(dispatch, getState) {
    const {graphs, paths, layout} = getState();

    // overallOrder will assert circular dependencies for multi output.
    try {
        graphs.MultiGraph.overallOrder();
    } catch (err) {
        dispatch(
            onError({
                type: 'backEnd',
                error: {
                    message: 'Circular Dependencies',
                    html: err.toString()
                }
            })
        );
    }

    dispatch(
        addRequestedCallbacks(
            getLayoutCallbacks(graphs, paths, layout, {
                outputsOnly: true
            })
        )
    );
}

export const redo = moveHistory('REDO');
export const undo = moveHistory('UNDO');
export const revert = moveHistory('REVERT');

function moveHistory(changeType) {
    return function (dispatch, getState) {
        const {history, paths} = getState();
        dispatch(createAction(changeType)());
        const {id, props} =
            (changeType === 'REDO'
                ? history.future[0]
                : history.past[history.past.length - 1]) || {};
        if (id) {
            // Update props
            dispatch(
                createAction('UNDO_PROP_CHANGE')({
                    itempath: getPath(paths, id),
                    props
                })
            );

            dispatch(notifyObservers({id, props}));
        }
    };
}

export function notifyObservers({id, props}) {
    return async function (dispatch, getState) {
        const {graphs, paths} = getState();
        dispatch(
            addRequestedCallbacks(includeObservers(id, props, graphs, paths))
        );
    };
}

export function handleAsyncError(err, message, dispatch) {
    // Handle html error responses
    if (err && typeof err.text === 'function') {
        err.text().then(text => {
            const error = {message, html: text};
            dispatch(onError({type: 'backEnd', error}));
        });
    } else {
        const error = err instanceof Error ? err : {message, html: err};
        dispatch(onError({type: 'backEnd', error}));
    }
}
