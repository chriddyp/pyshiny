import {
    concat,
    flatten,
    isEmpty,
    isNil,
    map,
    path,
    keys,
    pickBy,
    toPairs,
    pathOr
} from 'ramda';

import {IStoreState} from '../store';
import {ThunkDispatch} from 'redux-thunk';
import {AnyAction} from 'redux';

import {
    aggregateCallbacks,
    addRequestedCallbacks,
    removeExecutedCallbacks,
    addCompletedCallbacks,
    addStoredCallbacks
} from '../actions/callbacks';

import {parseIfWildcard} from '../actions/dependencies';

import {
    combineIdAndProp,
    getCallbacksByInput,
    getLayoutCallbacks,
    includeObservers
} from '../actions/dependencies_ts';

import {ICallback, IStoredCallback} from '../types/callbacks';

import {updateProps, setPaths, handleAsyncError} from '../actions';
import {getPath, computePaths} from '../actions/paths';

import {applyPersistence, prunePersistence} from '../persistence';
import {IStoreObserverDefinition} from '../StoreObserver';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({dispatch, getState}) => {
        const {
            callbacks: {executed}
        } = getState();

        function applyProps(
            id: any,
            updatedProps: any,
            enable_persistence: boolean
        ) {
            const {layout, paths} = getState();
            const itempath = getPath(paths, id);
            if (!itempath) {
                return false;
            }

            // This is a callback-generated update.
            // Check if this invalidates existing persisted prop values,
            // or if persistence changed, whether this updates other props.
            updatedProps = prunePersistence(
                path(itempath, layout),
                updatedProps,
                dispatch,
                enable_persistence
            );

            const {props} = applyPersistence(
                {props: updatedProps},
                dispatch,
                enable_persistence
            );

            (dispatch as ThunkDispatch<any, any, AnyAction>)(
                updateProps({
                    itempath,
                    props,
                    source: 'response',
                    enable_persistence
                })
            );

            return props;
        }

        let requestedCallbacks: ICallback[] = [];
        const storedCallbacks: IStoredCallback[] = [];

        executed.forEach(cb => {
            const predecessors = concat(cb.predecessors ?? [], [cb.callback]);

            const {
                callback: {clientside_function, output},
                executionResult
            } = cb;

            if (isNil(executionResult)) {
                return;
            }

            const {data, error, payload} = executionResult;

            if (data !== undefined) {
                Object.entries(data).forEach(
                    ([id, props]: [any, {[key: string]: any}]) => {
                        const parsedId = parseIfWildcard(id);
                        const {
                            graphs,
                            layout: oldLayout,
                            paths: oldPaths
                        } = getState();

                        const enable_persistence =
                            cb.callback.enable_persistence === undefined
                                ? false
                                : cb.callback.enable_persistence;

                        // Components will trigger callbacks on their own as required (eg. derived)
                        const appliedProps = applyProps(
                            parsedId,
                            props,
                            enable_persistence
                        );

                        // Add callbacks for modified inputs
                        requestedCallbacks = concat(
                            requestedCallbacks,
                            flatten(
                                map(
                                    prop =>
                                        getCallbacksByInput(
                                            graphs,
                                            oldPaths,
                                            parsedId,
                                            prop,
                                            true
                                        ),
                                    keys(props)
                                )
                            ).map(rcb => ({
                                ...rcb,
                                predecessors
                            }))
                        );

                        const basePath = getPath(oldPaths, parsedId);
                        if (!basePath) {
                            return;
                        }
                        const oldObj = path(basePath, oldLayout);

                        const childrenProps = pathOr(
                            'defaultValue',
                            [oldObj.namespace, oldObj.type],
                            (window as any).__dashprivate_childrenProps
                        );

                        const handlePaths = (
                            children: any,
                            oldChildren: any,
                            oldChildrenPath: any[],
                            filterRoot: any = false
                        ) => {
                            const oPaths = getState().paths;
                            const paths = computePaths(
                                children,
                                oldChildrenPath,
                                oPaths
                            );
                            dispatch(setPaths(paths));

                            // Get callbacks for new layout (w/ execution group)
                            requestedCallbacks = concat(
                                requestedCallbacks,
                                getLayoutCallbacks(graphs, paths, children, {
                                    chunkPath: oldChildrenPath,
                                    filterRoot
                                }).map(rcb => ({
                                    ...rcb,
                                    predecessors
                                }))
                            );

                            // Wildcard callbacks with array inputs (ALL / ALLSMALLER) need to trigger
                            // even due to the deletion of components
                            requestedCallbacks = concat(
                                requestedCallbacks,
                                getLayoutCallbacks(
                                    graphs,
                                    oldPaths,
                                    oldChildren,
                                    {
                                        removedArrayInputsOnly: true,
                                        newPaths: paths,
                                        chunkPath: oldChildrenPath,
                                        filterRoot
                                    }
                                ).map(rcb => ({
                                    ...rcb,
                                    predecessors
                                }))
                            );
                        };

                        let recomputed = false;

                        ['children']
                            .concat(childrenProps)
                            .forEach(childrenProp => {
                                if (recomputed) {
                                    return;
                                }
                                if (childrenProp.includes('[]')) {
                                    const [frontPath] = childrenProp
                                        .split('[]')
                                        .map(p => p.split('.').filter(e => e));

                                    const frontObj: any[] | undefined = path(
                                        frontPath,
                                        appliedProps
                                    );

                                    if (!frontObj) {
                                        return;
                                    }

                                    // Crawl layout needs the ns/type
                                    handlePaths(
                                        {
                                            ...oldObj,
                                            props: {
                                                ...oldObj.props,
                                                ...appliedProps
                                            }
                                        },
                                        oldObj,
                                        basePath,
                                        keys(appliedProps)
                                    );
                                    // Only do it once for the component.
                                    recomputed = true;
                                } else {
                                    const childrenPropPath =
                                        childrenProp.split('.');
                                    const children = path(
                                        childrenPropPath,
                                        appliedProps
                                    );
                                    if (!children) {
                                        return;
                                    }

                                    const oldChildrenPath = concat(
                                        getPath(oldPaths, parsedId) as string[],
                                        ['props'].concat(childrenPropPath)
                                    );
                                    const oldChildren = path(
                                        oldChildrenPath,
                                        oldLayout
                                    );

                                    handlePaths(
                                        children,
                                        oldChildren,
                                        oldChildrenPath
                                    );
                                }
                            });

                        // persistence edge case: if you explicitly update the
                        // persistence key, other props may change that require us
                        // to fire additional callbacks
                        const addedProps = pickBy(
                            (_, k) => !(k in props),
                            appliedProps
                        );
                        if (!isEmpty(addedProps)) {
                            const {graphs: currentGraphs, paths} = getState();

                            requestedCallbacks = concat(
                                requestedCallbacks,
                                includeObservers(
                                    id,
                                    addedProps,
                                    currentGraphs,
                                    paths
                                ).map(rcb => ({
                                    ...rcb,
                                    predecessors
                                }))
                            );
                        }
                    }
                );

                // Add information about potentially updated outputs vs. updated outputs,
                // this will be used to drop callbacks from execution groups when no output
                // matching the downstream callback's inputs were modified
                storedCallbacks.push({
                    ...cb,
                    executionMeta: {
                        allProps: map(
                            combineIdAndProp,
                            flatten(cb.getOutputs(getState().paths))
                        ),
                        updatedProps: flatten(
                            map(
                                ([id, value]) =>
                                    map(
                                        property =>
                                            combineIdAndProp({id, property}),
                                        keys(value) as string[]
                                    ),
                                toPairs(data)
                            )
                        )
                    }
                });
            }

            if (error !== undefined) {
                let message;
                if (cb.callback.no_output) {
                    const inpts = keys(cb.changedPropIds).join(', ');
                    message = `Callback error with no output from input ${inpts}`;
                } else {
                    const outputs = payload
                        ? map(
                              combineIdAndProp,
                              flatten([payload.outputs])
                          ).join(', ')
                        : output;
                    message = `Callback error updating ${outputs}`;
                }
                if (clientside_function) {
                    const {namespace: ns, function_name: fn} =
                        clientside_function;
                    message += ` via clientside function ${ns}.${fn}`;
                }

                handleAsyncError(error, message, dispatch);

                storedCallbacks.push({
                    ...cb,
                    executionMeta: {
                        allProps: map(
                            combineIdAndProp,
                            flatten(cb.getOutputs(getState().paths))
                        ),
                        updatedProps: []
                    }
                });
            }
        });

        dispatch(
            aggregateCallbacks([
                executed.length ? removeExecutedCallbacks(executed) : null,
                executed.length ? addCompletedCallbacks(executed.length) : null,
                storedCallbacks.length
                    ? addStoredCallbacks(storedCallbacks)
                    : null,
                requestedCallbacks.length
                    ? addRequestedCallbacks(requestedCallbacks)
                    : null
            ])
        );
    },
    inputs: ['callbacks.executed']
};

export default observer;
