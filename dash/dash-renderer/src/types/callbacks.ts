type CallbackId = string | {[key: string]: any};

export interface ICallbackDefinition {
    clientside_function?: {
        namespace: string;
        function_name: string;
    };
    input: string;
    inputs: ICallbackProperty[];
    output: string;
    outputs: ICallbackProperty[];
    prevent_initial_call: boolean;
    state: ICallbackProperty[];
    long?: LongCallbackInfo;
    dynamic_creator?: boolean;
    running: any;
    no_output?: boolean;
    enable_persistence?: boolean;
}

export interface ICallbackProperty {
    id: CallbackId;
    property: string;
}

export interface ILayoutCallbackProperty extends ICallbackProperty {
    path: (string | number)[];
}

export interface ICallbackTemplate {
    anyVals: any[] | string;
    callback: ICallbackDefinition;
    changedPropIds: any;
    executionGroup?: string;
    initialCall: boolean;
    getInputs: (paths: any) => ILayoutCallbackProperty[][];
    getOutputs: (paths: any) => ILayoutCallbackProperty[][];
    getState: (paths: any) => ILayoutCallbackProperty[][];
    resolvedId: any;
}

export interface ICallback extends ICallbackTemplate {
    predecessors?: ICallbackDefinition[];
    priority?: string;
}

// tslint:disable-next-line:no-empty-interface
export type IPrioritizedCallback = ICallback;

export interface IBlockedCallback extends IPrioritizedCallback {
    allOutputs: ILayoutCallbackProperty[][];
    allPropIds: any[];
    isReady: Promise<any> | true;
}

export interface IExecutingCallback extends IPrioritizedCallback {
    executionPromise: Promise<CallbackResult> | CallbackResult | null;
}

// tslint:disable-next-line:no-empty-interface
export type IWatchedCallback = IExecutingCallback;

export interface IExecutedCallback extends IWatchedCallback {
    executionResult: CallbackResult | null;
}

export interface IStoredCallback extends IExecutedCallback {
    executionMeta: {
        allProps: string[];
        updatedProps: string[];
    };
}

export interface ICallbackPayload {
    changedPropIds: any[];
    parsedChangedPropsIds: any[];
    inputs: any[];
    output: string;
    outputs: any[];
    state?: any[] | null;
}

export type CallbackResult = {
    data?: CallbackResponse;
    error?: Error;
    payload: ICallbackPayload | null;
};

export type LongCallbackInfo = {
    interval?: number;
    progress?: any;
    running?: any;
};

export type CallbackResponse = {
    [k: string]: any;
};

export type CallbackResponseData = {
    response?: CallbackResponse;
    multi?: boolean;
    cacheKey?: string;
    job?: string;
    progressDefault?: CallbackResponse;
    progress?: CallbackResponse;
    running?: CallbackResponse;
    runningOff?: CallbackResponse;
    cancel?: ICallbackProperty[];
    dist?: any;
    sideUpdate?: any;
};

export type SideUpdateOutput = {
    [key: string]: any;
};
