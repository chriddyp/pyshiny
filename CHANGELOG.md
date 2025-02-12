# Change Log for Dash
All notable changes to `dash` will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).

## [UNRELEASED]

## Fixed

- [#3080](https://github.com/plotly/dash/pull/3080) Fix docstring generation for components using single-line or nonstandard-indent leading comments
- [#3103](https://github.com/plotly/dash/pull/3103) Fix Graph component becomes unresponsive if an invalid figure is passed

## Changed
- [#3113](https://github.com/plotly/dash/pull/3113) Adjusted background polling requests to strip the data from the request, this allows for context to flow as normal. This addresses issue [#3111](https://github.com/plotly/dash/pull/3111)


## [2.18.2] - 2024-11-04

## Fixed

- [#2939](https://github.com/plotly/dash/pull/2939) Fixes bug with whitespace on DataTable when `merge_duplicate_header=True`. Fixes [#2870](https://github.com/plotly/dash/issues/2870)
- [#2994](https://github.com/plotly/dash/pull/2994) Keep generated doc-string order for shape or exact props. Fixes [#2990](https://github.com/plotly/dash/issues/2990)
- [#3011](https://github.com/plotly/dash/pull/3011) Fixed an exception error caused by assigning `None` to array properties with `exact` or `shape` element types. Fixes [#3010](https://github.com/plotly/dash/issues/3010)
- [#2991](https://github.com/plotly/dash/pull/2991) Add support for URL decoding of the search parameter for pages.
- [#3025](https://github.com/plotly/dash/pull/3025) Fix no output callback with error handler setting the response to NoUpdate and triggering an error.
- [#3034](https://github.com/plotly/dash/pull/3034) Remove whitespace from `metadata.json` files to reduce package size.
- [#3009](https://github.com/plotly/dash/pull/3009) Performance improvement on (pattern-matching) callbacks.
- [#3028](https://github.com/plotly/dash/pull/3028) Fix jupyterlab v4 support.
- [#2926](https://github.com/plotly/dash/pull/2926) Fix components defaultProps with react 18.3.1
- [#3051](https://github.com/plotly/dash/pull/3051) Add missing request data to callback context. Fix [#2235](https://github.com/plotly/dash/issues/2235).

## [2.18.1] - 2024-09-12

## Fixed

- [#2987](https://github.com/plotly/dash/pull/2987) Fix multioutput requiring same number of no_update. Fixes [#2986](https://github.com/plotly/dash/issues/2986)
- [2988](https://github.com/plotly/dash/pull/2988) Fix error handler and grouped outputs. Fixes [#2983](https://github.com/plotly/dash/issues/2983)
- [#2841](https://github.com/plotly/dash/pull/2841) Fix typing on Dash init.
- [#1548](https://github.com/plotly/dash/pull/1548) Enable changing of selenium url, fix for selenium grid support.

## Deprecated

- [#2985](https://github.com/plotly/dash/pull/2985) Deprecate dynamic component loader.
- [#2985](https://github.com/plotly/dash/pull/2985) Deprecate `run_server`, use `run` instead.
- [#2899](https://github.com/plotly/dash/pull/2899) Deprecate `dcc.LogoutButton`, can be replaced with a `html.Button` or `html.A`. eg: `html.A(href=os.getenv('DASH_LOGOUT_URL'))` on a Dash Enterprise instance.
- [#2995](https://github.com/plotly/dash/pull/2995) Deprecate `Dash.__init__` keywords:
  - The `plugins` keyword will be removed.
  - Old `long_callback_manager` keyword will be removed, can use `background_callback_manager` instead.

## [2.18.0] - 2024-09-04

## Added

- [#2881](https://github.com/plotly/dash/pull/2881) Add outputs_list to window.dash_clientside.callback_context. Fixes [#2877](https://github.com/plotly/dash/issues/2877).
- [#2903](https://github.com/plotly/dash/pull/2903) Add callback on_error handler, either globally on Dash init or per callback basis. Receives the exception as first argument, can return output(s) or None for `no_update`. Access to original callback context is preserved and `set_props` works inside the error handler.
- [#2936](https://github.com/plotly/dash/pull/2936) Adds support for TypeScript 5.5+.
- [#2789](https://github.com/plotly/dash/pull/2789) Add library loading capacity to `_allow_dynamic_callbacks`

## Fixed

- [#2898](https://github.com/plotly/dash/pull/2898) Fix error thrown when using non-existent components in callback running keyword. Fixes [#2897](https://github.com/plotly/dash/issues/2897).
- [#2892](https://github.com/plotly/dash/pull/2860) Fix ensures dcc.Dropdown menu maxHeight option works with Datatable. Fixes [#2529](https://github.com/plotly/dash/issues/2529) [#2225](https://github.com/plotly/dash/issues/2225)
- [#2896](https://github.com/plotly/dash/pull/2896) The tabIndex parameter of Div can accept number or string type. Fixes [#2891](https://github.com/plotly/dash/issues/2891)
- [#2900](https://github.com/plotly/dash/pull/2900) Allow strings in layout list. Fixes [#2890](https://github.com/plotly/dash/issues/2890)
- [#2908](https://github.com/plotly/dash/pull/2908) Fix when environment variables are ignored by Dash.run() at runtime. Fixes [#2902](https://github.com/plotly/dash/issues/2902)
- [#2888](https://github.com/plotly/dash/pull/2888) Add id to dcc.Loading DOM. Fixes [#2878](https://github.com/plotly/dash/issues/2878)
- [#2922](https://github.com/plotly/dash/pull/2922) Fix background callback hash_function when source is unavailable. Fixes [#1885](https://github.com/plotly/dash/issues/1885)
- [#2915](https://github.com/plotly/dash/pull/2915) Fix 'AttributeError' when layout is a function that returns a list of components. Fixes [#2905](https://github.com/plotly/dash/issues/2905)
- [#2956](https://github.com/plotly/dash/pull/2956) Add missing useEffect dependency to dcc.Loading component.
- [#2909](https://github.com/plotly/dash/pull/2909) Rehighlights dcc.Markdown when it is updated, fixes [#2895](https://github.com/plotly/dash/issues/2895)

## [2.17.1] - 2024-06-12

## Fixed

- [#2860](https://github.com/plotly/dash/pull/2860) Fix dcc.Loading to apply overlay_style only to the children and not the spinner. Fixes [#2858](https://github.com/plotly/dash/issues/2858)
- [#2854](https://github.com/plotly/dash/pull/2854) Fix dcc.Dropdown resetting empty values to null and triggering callbacks. Fixes [#2850](https://github.com/plotly/dash/issues/2850)
- [#2859](https://github.com/plotly/dash/pull/2859) Fix base patch operators. fixes [#2855](https://github.com/plotly/dash/issues/2855)
- [#2856](https://github.com/plotly/dash/pull/2856) Fix multiple consecutive calls with same id to set_props only keeping the last props. Fixes [#2852](https://github.com/plotly/dash/issues/2852)
- [#2867](https://github.com/plotly/dash/pull/2867) Fix clientside no output callback. Fixes [#2866](https://github.com/plotly/dash/issues/2866)
- [#2876](https://github.com/plotly/dash/pull/2876) Fix pattern matching in callback running argument. Fixes [#2863](https://github.com/plotly/dash/issues/2863)

## [2.17.0] - 2024-05-03

## Added

- [#2832](https://github.com/plotly/dash/pull/2832) Add dash startup route setup on Dash init.
- [#2819](https://github.com/plotly/dash/pull/2819) Add dash subcomponents receive additional parameters passed by the parent component. Fixes [#2814](https://github.com/plotly/dash/issues/2814).
- [#2826](https://github.com/plotly/dash/pull/2826) When using Pages, allows for `app.title` and (new) `app.description` to be used as defaults for the page title and description. Fixes [#2811](https://github.com/plotly/dash/issues/2811).
- [#2795](https://github.com/plotly/dash/pull/2795) Allow list of components to be passed as layout.
- [#2760](https://github.com/plotly/dash/pull/2760) New additions to dcc.Loading resolving multiple issues:
  - `delay_show` and `delay_hide` props  to prevent flickering during brief loading periods (similar to Dash Bootstrap Components dbc.Spinner)
  - `overlay_style` for styling the loading overlay,  such as setting  visibility and opacity for children
  - `target_components` specifies components/props triggering the loading spinner
  - `custom_spinner`  enables using a custom component for loading messages instead of built-in spinners
  - `display`  overrides the loading status with options for "show," "hide," or "auto"

- [#2822](https://github.com/plotly/dash/pull/2822) Support no output callbacks. Fixes [#1549](https://github.com/plotly/dash/issues/1549)
- [#2822](https://github.com/plotly/dash/pull/2822) Add global set_props. Fixes [#2803](https://github.com/plotly/dash/issues/2803)

## Fixed

- [#2362](https://github.com/plotly/dash/pull/2362) Global namespace not polluted any more when loading clientside callbacks.
- [#2833](https://github.com/plotly/dash/pull/2833) Allow data url in link props. Fixes [#2764](https://github.com/plotly/dash/issues/2764)
- [#2822](https://github.com/plotly/dash/pull/2822) Fix side update (running/progress/cancel) dict ids. Fixes [#2111](https://github.com/plotly/dash/issues/2111)
- [#2817](https://github.com/plotly/dash/pull/2817) Change hashing algorithm from md5 to sha256, Fixes [#2697](https://github.com/plotly/dash/issues/2697).
- [#2816](https://github.com/plotly/dash/pull/2816) Fix dcc.Dropdown value not updated when option is removed. Fixes [#2733](https://github.com/plotly/dash/issues/2733).
- [#2823](https://github.com/plotly/dash/pull/2823) Fix None in "wait" methods causing incorrectly passing tests. Fixes [#2818](https://github.com/plotly/dash/issues/2818)

## [2.16.1] - 2024-03-06

## Fixed

- [#2783](https://github.com/plotly/dash/pull/2783) Remove dynamic loading.

## [2.16.0] - 2024-03-01

## Fixed

- [#2756](https://github.com/plotly/dash/pull/2756) Prevent false dangerous link warning. Fixes [#2743](https://github.com/plotly/dash/issues/2743)
- [#2752](https://github.com/plotly/dash/pull/2752) Fixed issue with Windows build, for first time build on Windows, the dev needs to use `npm run first-build`

## Changed

- [#2734](https://github.com/plotly/dash/pull/2734) Configure CI for Python 3.10 [#1863](https://github.com/plotly/dash/issues/1863)
- [#2735](https://github.com/plotly/dash/pull/2735) Configure CI for Python 3.8 and 3.12, drop support for Python 3.6 and Python 3.7 [#2736](https://github.com/plotly/dash/issues/2736)

## Added
- [#2762](https://github.com/plotly/dash/pull/2762) Add dynamic loading of component libraries.
  - Add `dynamic_loading=True` to dash init.
  - Add `preloaded_libraries=[]` to dash init, included libraries names will be loaded on the index like before.
- [#2758](https://github.com/plotly/dash/pull/2758)
  - exposing `setProps` to `dash_clientside.clientSide_setProps` to allow for JS code to interact directly with the dash eco-system
- [#2730](https://github.com/plotly/dash/pull/2721) Load script files with `.mjs` ending as js modules
- [#2770](https://github.com/plotly/dash/pull/2770) Add running to regular callbacks.

## [2.15.0] - 2024-01-31

## Added
- [#2695](https://github.com/plotly/dash/pull/2695) Adds  `triggered_id` to `dash_clientside.callback_context`.  Fixes [#2692](https://github.com/plotly/dash/issues/2692)
- [#2723](https://github.com/plotly/dash/pull/2723) Improve dcc Slider/RangeSlider tooltips. Fixes [#1846](https://github.com/plotly/dash/issues/1846)
  - Add `tooltip.template` a string for the format template, {value} will be formatted with the actual value.
  - Add `tooltip.style` a style object to give to the div of the tooltip.
  - Add `tooltip.transform` a reference to a function in the `window.dccFunctions` namespace.
- [#2732](https://github.com/plotly/dash/pull/2732) Add special key `_dash_error` to `setProps`, allowing component developers to send error without throwing in render. Usage `props.setProps({_dash_error: new Error("custom error")})`

## Fixed

- [#2732](https://github.com/plotly/dash/pull/2732) Sanitize html props that are vulnerable to xss vulnerability if user data is inserted. Fix Validate url to prevent XSS attacks [#2729](https://github.com/plotly/dash/issues/2729)

## Changed
- [#2652](https://github.com/plotly/dash/pull/2652) dcc.Clipboard supports htm_content and triggers a copy to clipboard when n_clicks are changed
- [#2721](https://github.com/plotly/dash/pull/2721) Remove ansi2html, fixes [#2613](https://github.com/plotly/dash/issues/2713)

## [2.14.2] - 2023-11-27

## Fixed

- [#2700](https://github.com/plotly/dash/pull/2700) Fix `_allow_dynamic_callbacks` for newly-added components.

## [2.14.1] - 2023-10-26

## Fixed

- [#2672](https://github.com/plotly/dash/pull/2672) Fix `get_caller_name` in case the source is not available.

## Changed

- [#2674](https://github.com/plotly/dash/pull/2674) Raise flask & werkzeug limits to <3.1

## [2.14.0] - 2023-10-11

## Fixed

- [#2634](https://github.com/plotly/dash/pull/2634) Fix deprecation warning on pkg_resources, fix [#2631](https://github.com/plotly/dash/issues/2631)

## Changed

- [#2635](https://github.com/plotly/dash/pull/2635) Get proper app module name, remove need to give `__name__` to Dash constructor.

## Added

- [#2647](https://github.com/plotly/dash/pull/2647) `routing_callback_inputs` allowing to pass more Input and/or State arguments to the pages routing callback
- [#2649](https://github.com/plotly/dash/pull/2649) Add `_allow_dynamic_callbacks`, register new callbacks inside other callbacks.
  **WARNING: dynamic callback creation can be dangerous, use at you own risk. It is not intended for use in a production app, multi-user or multiprocess use as it only works for a single user.**

## [2.13.0] 2023-08-28
## Changed

- [#2610](https://github.com/plotly/dash/pull/2610) Load plotly.js bundle/version from plotly.py

## Added

- [#2630](https://github.com/plotly/dash/pull/2630) New layout hooks in the renderer

## [2.12.1] - 2023-08-16

## Fixed

- [#2625](https://github.com/plotly/dash/pull/2625) Fix background callbacks without cancel arguments failing setup, fix [#2624](https://github.com/plotly/dash/issues/2624)

## [2.12.0] - 2023-08-14

## Fixed

- [#2619](https://github.com/plotly/dash/pull/2619) Fix for dash-table column IDs containing special characters
- [#2616](https://github.com/plotly/dash/pull/2616) Add mapping of tsconfig compiler option `moduleResolution`, fixes [#2618](https://github.com/plotly/dash/issues/2618)
- [#2596](https://github.com/plotly/dash/pull/2596) Fix react-dom throwing unique key prop error for markdown table, fix [#1433](https://github.com/plotly/dash/issues/1433)
- [#2589](https://github.com/plotly/dash/pull/2589) CSS for input elements not scoped to Dash application
- [#2599](https://github.com/plotly/dash/pull/2599) Fix background callback cancel inputs used in multiple callbacks and mixed cancel inputs across pages.

## Changed

- [#2593](https://github.com/plotly/dash/pull/2593) dcc.Input accepts a number for its debounce argument

## Updated

- [#2621](https://github.com/plotly/dash/pull/2621) Update plotly.js to 2.25.2 from 2.24.2
  - Feature release [2.25.0](https://github.com/plotly/plotly.js/releases/tag/v2.25.0), Add "Equal Earth" project, options to include legends for shapes, Plotly.deleteActivateShape.
  - Patch release [2.24.3](https://github.com/plotly/plotly.js/releases/tag/v2.24.3) Fix for doubles clicks and legend group.
  - Patch release [2.25.1](https://github.com/plotly/plotly.js/releases/tag/v2.25.1) Fix clearing legend using react.
  - Patch release [2.25.2](https://github.com/plotly/plotly.js/releases/tag/v2.25.2) Fix potential prototype pollution in plot API calls.

## [2.11.1] - 2023-06-29

## Fixed

- [#2573](https://github.com/plotly/dash/pull/2578) Disable jupyter dash in Databricks, as the implementation here does not work in a Databricks notebook. Dash Enterprise customers can use the separate databricks-dash package for this purpose.

## Changed

- [#2573](https://github.com/plotly/dash/pull/2573) Use `julia --project` command inside `JuliaRunner`.
- [#2579](https://github.com/plotly/dash/pull/2579) Add warning if using `JupyterDash`

## [2.11.0] - 2023-06-23

## Added

- [#2530](https://github.com/plotly/dash/pull/2530) Merge JupyterDash repository with Dash.
  - Add `jupyter_mode` argument to `app.run`, defaults to `inline` and configurable via `jupyter_dash.default_mode`.
  - Add prefixed arguments from `JupyterDash` to `app.run`: `jupyter_width`, `jupyter_height`, `jupyter_server_url`.

## Fixed

- [#2555](https://github.com/plotly/dash/pull/2555) Fix browser back button when removing one of multiple location components from layout, fix [#1312](https://github.com/plotly/dash/issues/1312)
- [#2565](https://github.com/plotly/dash/pull/2565) Fix sorting for > 10 pages, fix [#2564](https://github.com/plotly/dash/issues/2564)

## Updated

- [#2474](https://github.com/plotly/dash/pull/2574) Update plotly js to 2.24.2 from 2.23.2
  - Feature release [2.24.0](https://github.com/plotly/plotly.js/releases/tag/v2.24.0) add pattern to pie, funnelarea, sunburst, icicle and treemap traces
  - Patch release [2.24.1](https://github.com/plotly/plotly.js/releases/tag/v2.24.1) and [2.24.2](https://github.com/plotly/plotly.js/releases/tag/v2.24.2)

## [2.10.2] - 2023-05-31

## Changed

- Set Flask and Werkzeug version upper bound to `<2.3`.

## [2.10.1] - 2023-05-30

## Fixed

- [#2545](https://github.com/plotly/dash/pull/2545) Fix typescript objectOf generation.
- [#2548](https://github.com/plotly/dash/pull/2548) Fix component as props callback triggering other callbacks not in response, fix [#2487](https://github.com/plotly/dash/issues/2487).

## [2.10.0] - 2023-05-25

## Changed

- [#2538](https://github.com/plotly/dash/pull/2538) Add an upper bound to Flask and Werkzeug versions at `<2.2.3` because we expect the Dash ecosystem to be incompatible with the next minor release of Flask (this excludes the current latest Flask release 2.3.x). We will raise the upper bound to `<2.4` after we fix incompatibilities elsewhere in the Dash ecosystem.

## Added

- [#2540](https://github.com/plotly/dash/pull/2540) Add `include_pages_meta=True` to `Dash` constructor, and fix a security issue in pages meta tags [#2536](https://github.com/plotly/dash/issues/2536).

## Fixed

- [#2508](https://github.com/plotly/dash/pull/2508) Fix error message, when callback output has different length than spec
- [#2207](https://github.com/plotly/dash/pull/2207) Fix object of components support.
- [#2500](https://github.com/plotly/dash/pull/2500) Passing customdata by click for scattermapbox, fix [#2493](https://github.com/plotly/dash/issues/2493)
- [#2513](https://github.com/plotly/dash/pull/2513) Raise error when iterating over patch objects, fix [#2512](https://github.com/plotly/dash/issues/2512)

## Updated

- [#2533](https://github.com/plotly/dash/pull/2533) and [#2538](https://github.com/plotly/dash/pull/2538) Update Plotly.js to v2.23.2 from v2.20.0.
  - Feature release [2.23.0](https://github.com/plotly/plotly.js/releases/tag/v2.23.0) adds legend/colorbar xref/yref.
  - Feature release [2.22.0](https://github.com/plotly/plotly.js/releases/tag/v2.22.0) adds `legend` references to traces.
  - Feature release [2.21.0](https://github.com/plotly/plotly.js/releases/tag/v2.21.0) adds `label.texttemplate` to parametric shapes.
  - Patch releases [2.23.1](https://github.com/plotly/plotly.js/releases/tag/v2.23.1) and [2.23.2](https://github.com/plotly/plotly.js/releases/tag/v2.23.2) fix heatmap rendering on iOS and Safari when zsmooth is set to false and shape text when drawing a new shape.

- [#2538](https://github.com/plotly/dash/pull/2538) Update JS dependencies in dcc, html, dash-table, dash-renderer, and dash

## [2.9.3] - 2023-04-13

## Fixed

- [#2489](https://github.com/plotly/dash/pull/2489) Fix location change event handling when `Location` objects are removed from the layout. Event handlers would not be removed and eventually change props of a random DOM element, fix [#1346](https://github.com/plotly/dash/issues/1346)
- [#2498](https://github.com/plotly/dash/pull/2498) Fix error when caching callbacks which return `Patch` objects by making `Patch` objects picklable
- [#2491](https://github.com/plotly/dash/pull/2491) Fix clientside inline function name not found, fix [#2488](https://github.com/plotly/dash/issues/2488)

## [2.9.2] - 2023-03-29

## Fixed

- [#2479](https://github.com/plotly/dash/pull/2479) Fix `KeyError` "Callback function not found for output [...], , perhaps you forgot to prepend the '@'?" issue when using duplicate callbacks targeting the same output. This issue would occur when the app is restarted or when running with multiple `gunicorn` workers.
- [#2471](https://github.com/plotly/dash/pull/2471) Fix `allow_duplicate` output with clientside callback, fix [#2467](https://github.com/plotly/dash/issues/2467)
- [#2473](https://github.com/plotly/dash/pull/2473) Fix background callbacks with different outputs but same function, fix [#2221](https://github.com/plotly/dash/issues/2221)

## [2.9.1] - 2023-03-17

## Fixed

- [#2461](https://github.com/plotly/dash/pull/2461) Fix pytest plugin make report when testing not installed, fix [#2420](https://github.com/plotly/dash/issues/2420)

## [2.9.0] - 2023-03-16

## Breaking
- [#2450](https://github.com/plotly/dash/pull/2450) Set label style `display: block` if `inline` is false in RadioItems & Checklist components. To keep previous behavior, set `inline=True`. This is already how it was described and worked in our documentation and other places with CSS stylesheets that set the default orientation of RadioItems and Checklist options to vertical (including Dash Design Kit), but for unstyled pages it is a breaking change.

## Added

- [#2392](https://github.com/plotly/dash/pull/2392) Improved pages feature:
  - Accept an absolute path or a `pathlib.path` for `pages_folder`, to match `assets_folder`
  - Fix inferring `use_pages=True` when you supply a custom `pages_folder`
  - Fix for `pages_folder` that includes special characters
  - New test fixture `clear_pages_state`
  - Make imported pages act more like regular Python modules
- [#2068](https://github.com/plotly/dash/pull/2068) Added `refresh="callback-nav"` in `dcc.Location`. This allows for navigation without refreshing the page when url is updated in a callback.
- [#2417](https://github.com/plotly/dash/pull/2417) Add wait_timeout property to customize the behavior of the default wait timeout used for by wait_for_page, fix [#1595](https://github.com/plotly/dash/issues/1595)
- [#2417](https://github.com/plotly/dash/pull/2417) Add the element target text for wait_for_text* error message, fix [#945](https://github.com/plotly/dash/issues/945)
- [#2425](https://github.com/plotly/dash/pull/2425) Add `add_log_handler=True` to Dash init, if you don't want a log stream handler at all.
- [#2260](https://github.com/plotly/dash/pull/2260) Experimental support for React 18. The default is still React v16.14.0, but to use React 18 you can either set the environment variable `REACT_VERSION=18.2.0` before running your app, or inside the app call `dash._dash_renderer._set_react_version("18.2.0")`. THIS FEATURE IS EXPERIMENTAL. It has not been tested with component suites outside the Dash core, and we may add or remove available React versions in any future release.
- [#2414](https://github.com/plotly/dash/pull/2414) Add `dash.Patch`for partial update Output props without transferring the previous value in a State.
- [#2414](https://github.com/plotly/dash/pull/2414) Add `allow_duplicate` to `Output` arguments allowing duplicate callbacks to target the same prop.
- [#2349](https://github.com/plotly/dash/pull/2349) Added new `dcc.Geolocation` component

## Fixed

- [#2429](https://github.com/plotly/dash/pull/2429) Fix side effect on updating possible array children triggering callbacks, fix [#2411](https://github.com/plotly/dash/issues/2411).
- [#2417](https://github.com/plotly/dash/pull/2417) Disable the pytest plugin if `dash[testing]` not installed, fix [#946](https://github.com/plotly/dash/issues/946).
- [#2417](https://github.com/plotly/dash/pull/2417) Do not swallow the original error to get the webdriver, easier to know what is wrong after updating the browser but the driver.
- [#2425](https://github.com/plotly/dash/pull/2425) Fix multiple log handler added unconditionally to the logger, resulting in duplicate log message.
- [#2415](https://github.com/plotly/dash/pull/2415) Fix background callbacks progress not deleted after fetch.
- [#2426](https://github.com/plotly/dash/pull/2426) Set default interval to 1 second for app.long_callback, restoring the behavior it had before v2.6.0 when we introduced `backround=True` callbacks.

## Changed

- [#2425](https://github.com/plotly/dash/pull/2425) Moved the logger namespace to `dash.dash`, as library logger it should be on that namespace instead of the user app.

## Updated

- [#2241](https://github.com/plotly/dash/pull/2441) Update Plotly.js to v2.20.0 from v2.18.0.
  - Feature release [2.20.0](https://github.com/plotly/plotly.js/releases/tag/v2.20.0) adds `automargin` to the main plot title.
  - Feature release [2.19.0](https://github.com/plotly/plotly.js/releases/tag/v2.19.0) adds text labels to `layout.shapes`, and adds a `labelalias` property to replace specific axis tick labels.
  - Patch releases [2.18.1](https://github.com/plotly/plotly.js/releases/tag/v2.18.1),
    [2.18.2](https://github.com/plotly/plotly.js/releases/tag/v2.18.2),
    [2.19.1](https://github.com/plotly/plotly.js/releases/tag/v2.19.1) fix various bugs.

## [2.8.1] - 2023-01-30

## Fixed

- [#2400](https://github.com/plotly/dash/pull/2400) Added `disable_n_clicks=True` to the `html.Div` components in `page_container`.

## [2.8.0] - 2023-01-24

### Added

- [#2389](https://github.com/plotly/dash/pull/2389) Added `disable_n_clicks` prop to all html components to make it possible to remove onclick event listeners

## Fixed

- [#2388](https://github.com/plotly/dash/pull/2388) Fix [#2368](https://github.com/plotly/dash/issues/2368) ordering or Pattern Matching ALL after update to the subtree.

### Updated

- [#2367](https://github.com/plotly/dash/pull/2367) Updated the default `favicon.ico` to the current Plotly logo
- [#2394](https://github.com/plotly/dash/pull/2394) Update Plotly.js to v2.18.0 from v2.16.4.
  - Feature release [2.18.0](https://github.com/plotly/plotly.js/releases/tag/v2.18.0) adds `sync` tickmode, so several axes can share ticks and gridlines
  - Feature release [2.17.0](https://github.com/plotly/plotly.js/releases/tag/v2.17.0) adds automargin for multiple Y axes, a grouped mode for `scatter` traces, and rounded corners on `treemap` traces
  - Patch releases [2.17.1](https://github.com/plotly/plotly.js/releases/tag/v2.17.1) and [2.16.5](https://github.com/plotly/plotly.js/releases/tag/v2.16.5) fix various bugs

## [2.7.1] - 2022-12-12

### Fixed

- [#2344](https://github.com/plotly/dash/pull/2344) Fix [#1519](https://github.com/plotly/dash/issues/1519), a case where dependent callbacks can be called too many times and with inconsistent inputs
- [#2332](https://github.com/plotly/dash/pull/2332) Add key to wrapped children props in list.
- [#2336](https://github.com/plotly/dash/pull/2336) Fix inserted dynamic ids in component as props.

### Updated

- [#2361](https://github.com/plotly/dash/pull/2361) Dependencies upgrade.
  - Update Plotly.js to v2.16.4 (from v2.16.1): fix several bugs, particularly related to updating mapbox graphs.
    - Patch release [2.16.4](https://github.com/plotly/plotly.js/releases/tag/v2.16.4)
    - Patch release [2.16.3](https://github.com/plotly/plotly.js/releases/tag/v2.16.3)
    - Patch release [2.16.2](https://github.com/plotly/plotly.js/releases/tag/v2.16.2)
- [#2363](https://github.com/plotly/dash/pull/2363) Update html attributes for ol

## [2.7.0] - 2022-11-03

### Removed

- [#2282](https://github.com/plotly/dash/pull/2282) Dropped support for Internet Explorer. Our build process now targets vendor-supported browsers released in the last 7 years. Currently this means ES2015 but over time this will natually advance as older browser versions pass the 7-year threshold.

### Added

- [#2261](https://github.com/plotly/dash/pull/2261) Added new `placeholder_text` property to `filterOptions` for DataTable which allows overriding the default filter field placeholder.

### Updated

- [#2282](https://github.com/plotly/dash/pull/2282) Widespread dependency upgrades
  - Update Plotly.js to v2.16.1 (from v2.13.3)
    - Feature release [2.14.0](https://github.com/plotly/plotly.js/releases/tag/v2.14.0) adds arrows to `sankey` links, and `editSelection` option to config.
    - Feature release [2.15.0](https://github.com/plotly/plotly.js/releases/tag/v2.15.0) adds directed arrowheads and markers to `scatter` and scatter-like traces and increased control of automargin and legend sizing
    - Feature release [2.16.0](https://github.com/plotly/plotly.js/releases/tag/v2.16.0) adds clustering to `scattermapbox` traces and restricted bounds to `mapbox` plots.
    - Patch releases [2.15.1](https://github.com/plotly/plotly.js/releases/tag/v2.15.1) and [2.16.1](https://github.com/plotly/plotly.js/releases/tag/v2.16.1) fix several bugs.

### Fixed

- [#2292](https://github.com/plotly/dash/pull/2292) Pages: find the 404 page even if `pages_folder` is nested, or the 404 page is nested inside `pages_folder`.
- [#2265](https://github.com/plotly/dash/pull/2265) Removed deprecated `before_first_request` as reported in [#2177](https://github.com/plotly/dash/issues/2177).
- [#2257](https://github.com/plotly/dash/pull/2257) Fix tuple types in the TypeScript component generator.
- [#2293](https://github.com/plotly/dash/pull/2293) Fix Dropdown useMemo not detecting equal objects
- [#2277](https://github.com/plotly/dash/pull/2277) Use dropdown styles from node_modules, instead of from stored css file
- [#2105](https://github.com/plotly/dash/pull/2105) Fix order of dash component libraries imports.

### Changed

- [#2291](https://github.com/plotly/dash/pull/2291) Move `flask-compress` dependency to new extras requires `dash[compress]`

## [2.6.2] - 2022-09-23

### Fixed

- [#2237](https://github.com/plotly/dash/pull/2237) Ensure calls to `plotly.js` from `dcc.Graph` are properly sequenced even if React initiates multiple render cycles in quick succession.
- [#2218](https://github.com/plotly/dash/pull/2218) Fix bug [#1348](https://github.com/plotly/dash/issues/1348) Validate children prop (required or not).
- [#2223](https://github.com/plotly/dash/pull/2223) Exclude hidden folders when building `dash.page_registry`.
- [#2182](https://github.com/plotly/dash/pull/2182) Fix [#2172](https://github.com/plotly/dash/issues/2172)  Make it so that when using pages, if `suppress_callback_exceptions=True` the `validation_layout` is not set.
- [#2152](https://github.com/plotly/dash/pull/2152) Fix bug [#2128](https://github.com/plotly/dash/issues/2128) preventing rendering of multiple components inside a dictionary.
- [#2187](https://github.com/plotly/dash/pull/2187) Fix confusing error message when trying to use pytest fixtures but `dash[testing]` is not installed.
- [#2202](https://github.com/plotly/dash/pull/2202) Fix bug [#2185](https://github.com/plotly/dash/issues/2185) when you copy text with multiple quotes into a table
- [#2226](https://github.com/plotly/dash/pull/2226) Fix [#2219](https://github.com/plotly/dash/issues/2219) pages register & background callbacks.

## [2.6.1] - 2022-08-01

### Fixed

- [#2175](https://github.com/plotly/dash/pull/2175) Fix [#2173](https://github.com/plotly/dash/issues/2173) callback output of ndarray and no_update check.
- [#2146](https://github.com/plotly/dash/pull/2146) Remove leftover debug console.log statement.
- [#2168](https://github.com/plotly/dash/pull/2168)  Reverts [#2126](https://github.com/plotly/dash/pull/2126) (supporting redirect from root when using pages) until the new bugs introduced by that PR are fixed.

### Updated

- [#2167](https://github.com/plotly/dash/pull/2167) Update Plotly.js to v2.13.3 (from v2.13.1) including [patch release v2.13.2](https://github.com/plotly/plotly.js/releases/tag/v2.13.2) and [patch release v2.13.3](https://github.com/plotly/plotly.js/releases/tag/v2.13.3).
  - Emit `plotly_selected` event on plot API calls and GUI edits.
  - Fix `sankey` select error (regression introduced in 2.13.0).
  - Handle missing drag layer of invisible `sankey` traces to fix select error.
  - Emit selection event in shape drawing `dragmode`s when an existing selection is modified.

## [2.6.0] - 2022-07-14

### Added
- [#2109](https://github.com/plotly/dash/pull/2109) Add `maxHeight` to Dropdown options menu.
- [#2039](https://github.com/plotly/dash/pull/2039) Long callback changes:
  - Add `background=False` to `dash.callback` to use instead of `app.long_callback`.
  - Add previous `app.long_callback` arguments to `dash.callback` (`interval`, `running`, `cancel`, `progress`, `progress_default`, `cache_args_to_ignore`, `manager`)
- [#2110](https://github.com/plotly/dash/pull/2110) Add `search` prop to `dcc.Dropdown` options, allowing to search the dropdown options with something other than the label or value.

### Fixed
- [#2126](https://github.com/plotly/dash/pull/2126) Fix bug where it was not possible to redirect from root when using pages.
- [#2114](https://github.com/plotly/dash/pull/2114) Fix bug [#1978](https://github.com/plotly/dash/issues/1978) where text could not be copied from cells in tables with `cell_selectable=False`.
- [#2102](https://github.com/plotly/dash/pull/2102) Fix bug as reported in [dash-labs #113](https://github.com/plotly/dash-labs/issues/113) where files starting with `.` were not excluded when building `dash.page_registry`.
- [#2100](https://github.com/plotly/dash/pull/2100) Fixes bug where module name in for a custom `not_found_404` page is incorrect in the `dash.page_registry` when not using the `pages` folder.
- [#2098](https://github.com/plotly/dash/pull/2098) Accept HTTP code 400 as well as 401 for JWT expiry
- [#2097](https://github.com/plotly/dash/pull/2097) Fix bug [#2095](https://github.com/plotly/dash/issues/2095) with TypeScript compiler and `React.FC` empty valueDeclaration error & support empty props components.
- [#2104](https://github.com/plotly/dash/pull/2104) Fix bug [#2099](https://github.com/plotly/dash/issues/2099) with Dropdown clearing search value when a value is selected.
- [#2039](https://github.com/plotly/dash/pull/2039) Fix bugs in long callbacks:
  - Fix [#1769](https://github.com/plotly/dash/issues/1769) and [#1852](https://github.com/plotly/dash/issues/1852) short interval makes job run in loop.
  - Fix [#1974](https://github.com/plotly/dash/issues/1974) returning `no_update` or raising `PreventUpdate` not supported with celery.
  - Fix use of the callback context in celery long callbacks.
  - Fix support of pattern matching for long callbacks.
- [#2110](https://github.com/plotly/dash/pull/2110) Fix `dcc.Dropdown` search with component as prop for option label.
- [#2131](https://github.com/plotly/dash/pull/2131) Add encoding to file open calls. Fix bug [#2127](https://github.com/plotly/dash/issues/2127).

## Changed

- [#2116](https://github.com/plotly/dash/pull/2116) Rename long callbacks to background callbacks
  - Deprecated `dash.long_callback.managers.CeleryLongCallbackManager`, use `dash.CeleryManager` instead.
  - Deprecated `dash.long_callback.managers.DiskcacheLongCallbackManager`, use `dash.DiskcacheManager` instead.
  - Deprecated dash constructor argument `long_callback_manager` in favor of `background_callback_manager`.

### Updated
- [#2134](https://github.com/plotly/dash/pull/2134) Upgrade Plotly.js to v2.13.1 (from v2.12.1) including [feature release 2.13.0](https://github.com/plotly/plotly.js/releases/tag/v2.13.0) and [patch release 2.13.1](https://github.com/plotly/plotly.js/releases/tag/v2.13.1)
  - Add persistent selections via layout attributes `selections`, `newselection`, and `activeselection`, along with an updated UI allowing you to modify a selection you created.
  - Add unselected line styling to `parcoords` traces.
  - Add more quartile algorithms to `violin` traces.
  - More flexible axis `automargin` behavior.
  - And several other enhancements and bug fixes.

## [2.5.1] - 2022-06-13

### Fixed

- [#2087](https://github.com/plotly/dash/pull/2087) Fix bug [#2086](https://github.com/plotly/dash/issues/2086) in which using id as a key within a component's id breaks the new callback context's `args_grouping` function.
- [#2084](https://github.com/plotly/dash/pull/2084) In dash 2.5.0, a default viewport meta tag was added as recommended for mobile-optimized sites by [mdn](https://developer.mozilla.org/en-US/docs/Web/HTML/Viewport_meta_tag)
This feature can be disabled by providing an empty viewport meta tag.  e.g. `app = Dash(meta_tags=[{"name": "viewport"}])`
- [#2090](https://github.com/plotly/dash/pull/2090), [#2092](https://github.com/plotly/dash/pull/2092).  Fixed bug where the `path` to the `pages_folder` was incorrect on Windows.

### Removed

- [#2087](https://github.com/plotly/dash/pull/2087) Removed the undocumented callback context `args_grouping_values` property which was incompatible with pattern-matching callbacks.

## [2.5.0] - 2022-06-07

### Added

- [#1947](https://github.com/plotly/dash/pull/1947)  Added `pages` - a better way to build multi-page apps. For more information see the [forum post.](https://community.plotly.com/t/introducing-dash-pages-a-dash-2-x-feature-preview/57775)
- [#1965](https://github.com/plotly/dash/pull/1965) Add component as props.
- [#2049](https://github.com/plotly/dash/pull/2049) Added `wait_for_class_to_equal` and `wait_for_contains_class` methods to `dash.testing`

### Changed

- [#2050](https://github.com/plotly/dash/pull/2050) Changed `find_element` and `find_elements` to accept an `attribute` argument that aligns with Selenium's `By` class, allowing you to search elements by other attributes. Default value is `CSS_SELECTOR` to maintain backwards compatibility with previous `find_elements`.

### Fixed

- [#2043](https://github.com/plotly/dash/pull/2043) Fix bug
[#2003](https://github.com/plotly/dash/issues/2003) in which
`dangerously_allow_html=True` + `mathjax=True` works in some cases, and in some cases not.
- [#2065](https://github.com/plotly/dash/pull/2065) Fix bug [#2064](https://github.com/plotly/dash/issues/2064) rendering of `dcc.Dropdown` with a value but no options.
- [#2047](https://github.com/plotly/dash/pull/2047) Fix bug [#1979](https://github.com/plotly/dash/issues/1979) in which `DASH_DEBUG` as environment variable gets ignored.
- [#2070](https://github.com/plotly/dash/pull/2070) Fix bug [#2066](https://github.com/plotly/dash/issues/2066) nested types triggering maximum call stack error when building typescript components.

## [2.4.1] - 2022-05-11

### Fixed

- Fix [#2045](https://github.com/plotly/dash/issues/2045) import error when using pytest but `dash[testing]` is not installed.

## [2.4.0] - 2022-05-11

### Added
- [#1952](https://github.com/plotly/dash/pull/1952) Improved callback_context
  - Closes [#1818](https://github.com/plotly/dash/issues/1818) Closes [#1054](https://github.com/plotly/dash/issues/1054)
  - adds `dash.ctx`, a more concise name for `dash.callback_context`
  - adds `ctx.triggered_prop_ids`, a dictionary of the component ids and props that triggered the callback.
  - adds `ctx.triggered_id`, the `id` of the component that triggered the callback.
  - adds `ctx.args_grouping`, a dict of the inputs used with flexible callback signatures.

- [#2009](https://github.com/plotly/dash/pull/2009) Add support for Promises within Client-side callbacks as requested in [#1364](https://github.com/plotly/dash/pull/1364).

- [#1956](https://github.com/plotly/dash/pull/1956) Add TypeScript components generation.

- [#2034](https://github.com/plotly/dash/pull/2034) Add `link_target` prop to dcc.Markdown component. Closes [#1827](https://github.com/plotly/dash/issues/1827)

- [#2035](https://github.com/plotly/dash/pull/2036) Add type annotations to testing fixtures.

### Fixed

- [#2029](https://github.com/plotly/dash/pull/2029) Restrict the number of props listed explicitly in generated component constructors - default is 250. This prevents exceeding the Python 3.6 limit of 255 arguments. The omitted props are still in the docstring and can still be provided the same as before, they just won't appear in the signature so autocompletion may be affected.

- [#1968](https://github.com/plotly/dash/pull/1968) Fix bug [#1877](https://github.com/plotly/dash/issues/1877), code which uses `merge_duplicate_headers` and `style_header_conditional` to highlight columns, it incorrectly highlights header cells.

- [#2015](https://github.com/plotly/dash/pull/2015) Fix bug [#1854](https://github.com/plotly/dash/issues/1854) in which the combination of row_selectable="single or multi" and filter_action="native" caused the JS error.

- [#1976](https://github.com/plotly/dash/pull/1976) Fix [#1962](https://github.com/plotly/dash/issues/1962) in which DatePickerSingle and DatePickerRange are extremely slow when provided a long list of disabled_days.

- [#2035](https://github.com/plotly/dash/pull/2035) Fix [#2033](https://github.com/plotly/dash/issues/2033) In-App error reporting does not render HTML.

- [#1970](https://github.com/plotly/dash/pull/1970) dcc.Dropdown Refactor fixes:
  - Fix bug [#1868](https://github.com/plotly/dash/issues/1868) value does not update when selected option removed from options.
  - Fix bug [#1908](https://github.com/plotly/dash/issues/1908) Selected options not showing when the value contains a comma.

### Changed

- [#1751](https://github.com/plotly/dash/pull/1751) Rename `app.run_server` to `app.run` while preserving `app.run_server` for backwards compatibility.

- [#1839](https://github.com/plotly/dash/pull/1839) The `callback` decorator returns the original function, not the wrapped function, so that you can still call these functions directly, for example in tests. Note that in this case there will be no callback context so not all callbacks can be tested this way.

- [#2016](https://github.com/plotly/dash/pull/2016) Drop the 375px width from default percy_snapshot calls, keep only 1280px

- [#2027](https://github.com/plotly/dash/pull/1751) Improve the error message when a user doesn't wrap children in a list

### Updated
- [#2016](https://github.com/plotly/dash/pull/2016), [#2032](https://github.com/plotly/dash/pull/2032), and [#2042](https://github.com/plotly/dash/pull/2042) Widespread dependency upgrades
  - Upgrade Plotly.js to v2.12.1 (from v2.11.0).
    - Feature release [2.12.0](https://github.com/plotly/plotly.js/releases/tag/v2.12.0) adds minor ticks and gridlines, as well as dashed gridlines.
    - Patch release [2.11.1](https://github.com/plotly/plotly.js/releases/tag/v2.11.1) fixes regl-based traces in strict CSP mode, however you must manually switch to the strict bundle to use this.
    - Patch release [2.12.1](https://github.com/plotly/plotly.js/releases/tag/v2.12.1) fixes several bugs.
  - Upgrade `black` to v22.3.0 for Python 3.7+ - if you use `dash[ci]` and you call `black`, this may alter your code formatting slightly, including more consistently breaking Python 2 compatibility.
  - Many other mainly JS dependency upgrades to the internals of Dash renderer and components. These may patch bugs or improve performance.


## [2.3.1] - 2022-03-29

### Fixed

- [#1963](https://github.com/plotly/dash/pull/1963) Fix [#1780](https://github.com/plotly/dash/issues/1780) flask shutdown deprecation warning when running dashduo threaded tests.
- [#1995](https://github.com/plotly/dash/pull/1995) Fix [#1992](https://github.com/plotly/dash/issues/1992) ImportError: cannot import name 'get_current_traceback' from 'werkzeug.debug.tbtools'.

## [2.3.0] - 2022-03-13

### Added
- [#1949](https://github.com/plotly/dash/pull/1915) Add built-in MathJax support to both `dcc.Markdown` and `dcc.Graph`. A new boolean prop `mathjax` was added to these two components, defaulting to `False`. Set `mathjax=True` to enable math rendering. This work uses MathJax v3, although `dcc.Graph` and Plotly.js can also be used with MathJax v2.
  - In `dcc.Markdown` this has two flavors: inline math is any content between single dollar signs, for example `"$E=mc^2$"`, and "display" math (on its own line, potentially multi-line) is delimited by double dollar signs.
  - In `dcc.Graph`, most text fields (graph and axis titles, trace names, scatter and bar text) can use math, and it's enabled with single dollar sign delimiters. A limitation here is that currently a given piece of text can only be one or the other: if math is found, everything outside the delimiters is ignored. See https://plotly.com/python/LaTeX/ for details.
  - For an intro to LaTeX math, see https://en.wikibooks.org/wiki/LaTeX/Mathematics.
  - Big thanks to [Equinor](https://www.equinor.com/) for sponsoring this development, including the related work in Plotly.js!

### Updated
- [#1949](https://github.com/plotly/dash/pull/1915) Upgrade Plotly.js to v2.11.0 (from v2.9.0)
  - [Feature release 2.10.0](https://github.com/plotly/plotly.js/releases/tag/v2.10.0):
    - Support for MathJax v3
    - `fillpattern` for `scatter` traces with filled area
  - [Feature release 2.11.0](https://github.com/plotly/plotly.js/releases/tag/v2.11.0):
    - Every trace type can now be rendered in a stricter CSP environment, specifically avoiding `unsafe-eval`. Please note: the `regl`-based traces (`scattergl`, `scatterpolargl`, `parcoords`, and `splom`) are only strict in the `strict` bundle, which is NOT served by default in Dash. To use this bundle with Dash, you must either download it and put it in your `assets/` folder, or include it as an `external_script` from the CDN: https://cdn.plot.ly/plotly-strict-2.11.0.min.js. All other trace types are strict in the normal bundle.
  - Patch release [2.10.1](https://github.com/plotly/plotly.js/releases/tag/v2.10.1) containing a bugfix for `mesh3d` traces.


### Fixed
- [#1915](https://github.com/plotly/dash/pull/1915) Fix bug [#1474](https://github.com/plotly/dash/issues/1474) when both dcc.Graph and go.Figure have animation, and when the second animation in Figure is executed, the Frames from the first animation are played instead of the second one.

- [#1953](https://github.com/plotly/dash/pull/1953) Fix bug [#1783](https://github.com/plotly/dash/issues/1783) in which a failed hot reloader blocks the UI with alerts.

- [#1942](https://github.com/plotly/dash/pull/1942) Fix bug [#1663](https://github.com/plotly/dash/issues/1663) preventing pie traces from sending `customdata` with `clickData` and other events.

## [2.2.0] - 2022-02-18

### Added
- [#1923](https://github.com/plotly/dash/pull/1923):
  - `dash.get_relative_path`
  - `dash.strip_relative_path`
  - `dash.get_asset_url`
  This is similar to `dash.callback` where you don't need the `app` object. It makes it possible to use these
  functions in the `pages` folder of a multi-page app without running into the circular `app` imports issue.

### Updated
- [#1911](https://github.com/plotly/dash/pull/1911) Upgrade Plotly.js to v2.9.0 (from v2.8.3).
  - Adds `ticklabelstep` to axes to reduce tick labels while still showing all ticks.
  - Displays the plotly.js version when hovering on the modebar. This helps debugging situations where there might be multiple sources of plotly.js, for example `/assets` vs the versions built into `dcc` or `ddk`.

- [#1930](https://github.com/plotly/dash/pull/1930) Upgrade JavaScript dependencies across renderer and all components.

### Fixed
- [#1932](https://github.com/plotly/dash/pull/1932) Fixes several bugs:
  - Restores compatibility with IE11 [#1925](https://github.com/plotly/dash/issues/1925)
  - Restores `style_header` text alignment in Dash Table [#1914](https://github.com/plotly/dash/issues/1914)
  - Clears the unneeded `webdriver-manager` requirement from `dash[testing]` [#1919](https://github.com/plotly/dash/issues/1925)

## [2.1.0] - 2022-01-22

### Changed
- [#1876](https://github.com/plotly/dash/pull/1876) Delays finalizing `Dash.config` attributes not used in the constructor until `init_app()`.
- [#1869](https://github.com/plotly/dash/pull/1869), [#1873](https://github.com/plotly/dash/pull/1873) Upgrade Plotly.js to v2.8.3. This includes:
  - [Feature release 2.5.0](https://github.com/plotly/plotly.js/releases/tag/v2.5.0):
    - 3D traces are now compatible with `no-unsafe-eval` CSP rules.
  - [Feature release 2.6.0](https://github.com/plotly/plotly.js/releases/tag/v2.6.0):
    - Add `smith` subplots and `scattersmith` traces, for drawing Smith charts.
  - [Feature release 2.7.0](https://github.com/plotly/plotly.js/releases/tag/v2.7.0):
    - Add text data for `histogram` traces.
    - Fix an interaction between `uirevision` and `autorange` that pops up in some cases of mixed clientside / serverside figure generation.
  - [Feature release 2.8.0](https://github.com/plotly/plotly.js/releases/tag/v2.8.0):
    - Add horizontal colorbars.
    - Add text data on `heatmap` and related trace types.
    - Control legend group title fonts.
  - Patch releases [2.5.1](https://github.com/plotly/plotly.js/releases/tag/v2.5.1), [2.6.1](https://github.com/plotly/plotly.js/releases/tag/v2.6.1), [2.6.2](https://github.com/plotly/plotly.js/releases/tag/v2.6.2), [2.6.3](https://github.com/plotly/plotly.js/releases/tag/v2.6.3), [2.6.4](https://github.com/plotly/plotly.js/releases/tag/v2.6.4), [2.8.1](https://github.com/plotly/plotly.js/releases/tag/v2.8.1), [2.8.2](https://github.com/plotly/plotly.js/releases/tag/v2.8.2), and [2.8.3](https://github.com/plotly/plotly.js/releases/tag/v2.8.3) containing bugfixes.
  - This PR also upgrades various other dependencies of dash renderer and component suites.

- [#1745](https://github.com/plotly/dash/pull/1745):
    Improve our `extras_require`: there are now five options here, each with a well-defined role:
    - `dash[dev]`: for developing and building dash components.
    - `dash[testing]`: for using the `pytest` plugins in the `dash.testing` module
    - `dash[diskcache]`: required if you use `DiskcacheLongCallbackManager`
    - `dash[celery]`: required if you use `CeleryLongCallbackManager`
    - `dash[ci]`: mainly for internal use, these are additional requirements for the Dash CI tests, exposed for other component libraries to use a matching configuration.

### Added
- [#1883](https://github.com/plotly/dash/pull/1883) in DataTable added `page_current` to `persisted_props` as requested in [#1860](https://github.com/plotly/dash/issues/1860)



- [#1763](https://github.com/plotly/dash/pull/1763):
    ## Dash and Dash Renderer

    - `Input`, `State`, and `Output` now accept components instead of ID strings and Dash `callback` will auto-generate the component's ID under-the-hood if not supplied. This allows usage like:

    ```python
    my_input = dcc.Input()
    my_output = html.Div()
    app.layout = html.Div([my_input, my_output])

    @dash.callback(Output(my_output, 'children'), Input(my_input, 'value'))
    def update(value):
        return f'You have entered {value}'
    ```

    Or, if using Python >=3.8 you can use the `:=` walrus operator:
    ```python
    app.layout = html.Div([
        my_input := dcc.Input(),
        my_output := html.Div()
    ])

    @dash.callback(Output(my_output, 'children'), Input(my_input, 'value'))
    def update(value):
        return f'You have entered {value}'
    ```

  [#1894](https://github.com/plotly/dash/pull/1894) restricted this feature so auto-generated IDs are not allowed if the app uses `dash_snapshots` (a Dash Enterprise package) or if the component uses `persistence`, as this can create confusing errors. Callback definitions can still reference components in these cases, but those components must have explicit IDs.

    ## Dash Core Components

    ### Rearranged Keyword Arguments & Flexible Types
    **`Dropdown`, `RadioItem`, and `Checklist`**
    - Rearranged Keyword Arguments - `options` & `value` are now the first two keywords which means they can be supplied as positional arguments without the keyword. Supplying the keywords (`options=` and `value=`) is still supported.
    - Flexible Types - `options` can be supplied in two new forms:
      1. An array of `string|number|bool` where `label` and `value` are equal to the items in the list.
      2. A dictionary where the keys and values set as `value` and `label` respectively.

    Before:

    ```python
    dcc.Dropdown(
        options=[
            {'label': 'New York', 'value': 'New York'},
            {'label': 'Montreal', 'value': 'Montreal'},
        ],
        value='New York'
    )
    ```

    or

    ```python
    dcc.Dropdown(
        options=[
            {'label': 'New York', 'value': 'NYC'},
            {'label': 'Montreal', 'value': 'MTL'},
        ],
        value='New York'
    )
    ```

    After:

    ```python
    dcc.Dropdown(['New York', 'Montreal'], 'New York')
    ```

    Or

    ```python
    dcc.Dropdown({'NYC': 'New York', 'MTL': 'Montreal'}, 'New York')
    ```

    **`RangeSlider` & `Slider`**
    - Rearranged Keyword Arugments - `min`, `max`, and `step` are now the first three keyword arguments which means they can be supplied as positional arguments without the keyword.
    - Flexible Types
      - `step` will be calculated implicitly if not given.
      - `marks` will be auto generated if not given. It will use `min` and `max` and will respect `step` if supplied. Auto generated marks labels are SI unit formatted. Around 5 human-readable marks will be created.
      - To remove the Slider's marks, set `marks=None`.

    Before:

    ```python
    dcc.Slider(marks={1: 2, 2: 2, 3: 3})
    ```

    After:

    ```python
    dcc.Slider(min=1, max=3, step=1)
    ```

    Or equivalently:

    ```python
    dcc.Slider(1, 3, 1)
    ```

    Step can also be omitted and the `Slider` will attempt to create a nice, human readable  step with SI units and around 5 marks:

    ```python
    dcc.Slider(0, 100)
    ```

    The SI units and ranges supported in `marks` are:
    * `µ` - micro, 10⁻⁶
    * `m` - milli, 10⁻³
    * `​` (none) - 10⁰
    * `k` - kilo, 10³
    * `M` - mega, 10⁶
    * `G` - giga, 10⁹
    * `T` - tera, 10¹²
    * `P` - peta, 10¹⁵
    * `E` - exa, 10¹⁸

    _Ranges below 10µ are not supported by the Slider. This is a bug: https://github.com/plotly/dash/issues/1766_

    **`DataTable`**

    - Rearranged Keyword Arguments - `data` and `columns` the first twokeyword arguments which means they can be supplied as positional arguments without the keyword.
    - Inferred Properties - If `columns` isn't supplied then it is extracted from the the first row in `data`

    Before:

    ```python
    dash_table.DataTable(data=df.to_dict('records'), columns=[{'name': i, 'id': i} for i in df.columns])
    ```

    After:

    ```python
    dash_table.DataTable(data=df.to_dict('records'))
    ```

    ### New Component Properties

    **`Checklist` & `RadioItems`**

    - A new property `inline` appends `display: inline-block` to `labelStyle`.

    ```python
    dcc.Checklist(inline=True)
    ```

### Fixed
- [#1879](https://github.com/plotly/dash/pull/1879) Delete redundancy in pattern-matching callback implementation, specifically when `ALL` and `MATCH` wildcards are used together. This patch was submitted by an anonymous Dash Enterprise customer. Many thanks!

- [#1858](https://github.com/plotly/dash/pull/1858) Support `mini-css-extract-plugin` Webpack plugin with `@plotly/webpack-dash-dynamic-import` node package - used by components to support dash async chunks. Updated dependencies of other `@plotly` node packages.

- [#1836](https://github.com/plotly/dash/pull/1836) Fix `__all__` in dcc and table for extras: dcc download helpers and table format helpers. This also restores this functionality to the obsolete top-level packages `dash_core_components` and `dash_table`.

- [#1822](https://github.com/plotly/dash/pull/1822) Remove Radium from renderer dependencies, as part of investigating React 17 support.

- [#1779](https://github.com/plotly/dash/pull/1779):
    - Clean up our handling of serialization problems, including fixing `orjson` for Python 3.6
    - Added the ability for `dash.testing` `percy_snapshot` methods to choose widths to generate.

- [#1778](https://github.com/plotly/dash/pull/1778) DataTable: Fix React warnings stating
  that each child in a list should have a unique "key" prop

- [#1895](https://github.com/plotly/dash/pull/1895) Support debug=True if native namespace-packages are present

## [2.0.0] - 2021-08-03

## Dash and Dash Renderer

### Added
- [#1702](https://github.com/plotly/dash/pull/1702) Added a new `@app.long_callback` decorator to support callback functions that take a long time to run. See the PR and documentation for more information.
- [#1514](https://github.com/plotly/dash/pull/1514) Perform json encoding using the active plotly JSON engine.  This will default to the faster orjson encoder if the `orjson` package is installed.
- [#1736](https://github.com/plotly/dash/pull/1736) Add support for `request_refresh_jwt` hook and retry requests that used expired JWT tokens.

### Changed
- [#1679](https://github.com/plotly/dash/pull/1679) Restructure `dash`, `dash-core-components`, `dash-html-components`, and `dash-table` into a singular monorepo and move component packages into `dash`. This change makes the component modules available for import within the `dash` namespace, and simplifies the import pattern for a Dash app. From a development standpoint, all future changes to component modules will be made within the `components` directory, and relevant packages updated with the `dash-update-components` CLI command.
- [#1707](https://github.com/plotly/dash/pull/1707) Change the default value of the `compress` argument to the `dash.Dash` constructor to `False`. This change reduces CPU usage, and was made in recognition of the fact that many deployment platforms (e.g. Dash Enterprise) already apply their own compression. If deploying to an environment that does not already provide compression, the Dash 1 behavior may be restored by adding `compress=True` to the `dash.Dash` constructor.
- [#1734](https://github.com/plotly/dash/pull/1734) Added `npm run build` script to simplify build process involving `dash-renderer` and subcomponent libraries within `dash`.

### Fixed
- [#1857](https://github.com/plotly/dash/pull/1857) Fixed a regression with `dcc.Slider` and `dcc.RangeSlider` where steps were not being set to marks if None was passed as the prop argument.  Added a check to set the min and max based on the range of marks if they are not explicitly defined (for more info, see [#1843](https://github.com/plotly/dash/issues/1843) and [#1851](https://github.com/plotly/dash/issues/1843)).


## Dash Core Components
### Added

- [#1729](https://github.com/plotly/dash/pull/1729) Include F#, C#, and MATLAB in markdown code highlighting, for the upcoming .NET and MATLAB flavors of dash.

- [#1735](https://github.com/plotly/dash/pull/1735) Upgrade Plotly.js to v2.4.2. This includes:
  - [Feature release 2.3.0](https://github.com/plotly/plotly.js/releases/tag/v2.3.0):
    - More number formatting options due to `d3-format` upgrade.
    - Many new `geo` projections.
    - Improved rendering and performance of `scattergl`, `splom` and `parcoords` traces.
  - [Feature release 2.4.0](https://github.com/plotly/plotly.js/releases/tag/v2.4.0):
    - `legend.groupclick`
    - `bbox` of hover items in event data, to support custom dash-driven hover effects
  - Patch releases [2.3.1](https://github.com/plotly/plotly.js/releases/tag/v2.3.1), [2.4.1](https://github.com/plotly/plotly.js/releases/tag/v2.4.1), and [2.4.2](https://github.com/plotly/plotly.js/releases/tag/v2.4.2) containing various bug fixes.

- [#1735](https://github.com/plotly/dash/pull/1735) New `dcc.Tooltip` component. This is particularly useful for rich hover information on `dcc.Graph` charts, using the `bbox` information included in the event data in plotly.js v2.4.0

## Dash Table
### Added

- [#1729](https://github.com/plotly/dash/pull/1729) Include F#, C#, and MATLAB in markdown code highlighting, for the upcoming .NET and MATLAB flavors of dash.

## Dash HTML Components
### Removed

- [#1734](https://github.com/plotly/dash/pull/1734) Removed the following obsolete `html` elements - `<command>`, `<element>`, `<isindex>`, `<listing>`, `<multicol>`, `<nextid>`. These are obsolete and had been previously removed from the reference table.

## [1.21.0] - 2021-07-09

## Dash and Dash Renderer
### Added
- [#1675](https://github.com/plotly/dash/pull/1675) Add new `Dash` constructor argument `extra_hot_reload_paths`. This allows you to re-initialize the Python code of the app when non-Python files change, if you know that these files impact the app.

### Changed
- [#1675](https://github.com/plotly/dash/pull/1675) Remove the constraint that `requests_pathname_prefix` ends with `routes_pathname_prefix`. When you are serving your app behind a reverse proxy that rewrites URLs that constraint needs to be violated.
- [#1611](https://github.com/plotly/dash/pull/1611) and [#1685](https://github.com/plotly/dash/pull/1685) Package dash-renderer artifacts and dependencies with Dash, and source renderer resources from within Dash.
- [#1567](https://github.com/plotly/dash/pull/1567) Julia component generator puts components into `src/jl` - fixes an issue on case-insensitive filesystems when the component name and module name match (modulo case) and no prefix is used. Also reduces JS/Julia clutter in the overloaded `src` directory.

### Fixed
- [#1664](https://github.com/plotly/dash/pull/1664) Fix [#1649](https://github.com/plotly/dash/issues/1649), makes the devtools readable with a dark theme.
- [#1640](https://github.com/plotly/dash/pull/1640) Fix [#1475](https://github.com/plotly/dash/issues/1475), missing `timing_information` after certain modifications to Flask behavior

## Dash Core Components
### Fixed

- [#963](https://github.com/plotly/dash-core-components/pull/963) Fixes [#885](https://github.com/plotly/dash-core-components/issues/885)

  This applies the fix from [#878](https://github.com/plotly/dash-core-components/pull/878) to the RangeSlider.
  It not only fixes the bug where the tooltips were visible when slider was not, but it also reduces the lag in the
  tooltip when the slider handles are moved.

### Updated
- [#939](https://github.com/plotly/dash-core-components/pull/939) Upgrade Plotly.js to v2.2.1. Note that this is a major version upgrade to Plotly.js, however we are not treating this as a breaking change for DCC as the majority of breaking changes in Plotly.js do not affect the Dash API. The one exception is that several trace types that have long been deprecated are removed entirely.
  - [Major release 2.0.0](https://github.com/plotly/plotly.js/releases/tag/v2.0.0):
    - Stop exporting d3 as `Plotly.d3`, and remove many other deep pieces of the public API. This does not affect the `dcc.Graph` component, but if you make use of `Plotly` from the global scope in some other way you may be affected.
    - Drop the deprecated trace types `contourgl` and `area`, as well as legacy pre-`scatterpolar` polar attributes `bar.r`, `bar.t`, `scatter.r`, `scatter.t`, `layout.radialaxis`, `layout.angularaxis`. Use `scatterpolar`, `barpolar`, and `polar` subplots instead.
    - `heatmapgl` and `pointcloud` trace types, and the `transform` attribute are deprecated, and will be removed in a future release.
    - Increase CSP safety by removing function constructors. 3D plots still use function constructors, but if you place one of the non-3D bundles (including the new `strict` bundle) in your `assets` folder you will have no function constructors.
    - Remove "Aa" text in legends.
    - Default `hovermode` to "closest".
    - Default `textposition` to "auto" in `bar` traces. If you previously used the `bar.text` attribute for hover only, you will need to explicitly set `textposition="none"`.
    - Add `bar.marker.pattern`, `image.zsmooth`, and various other features and bugfixes.
  - [Feature release 2.1.0](https://github.com/plotly/plotly.js/releases/tag/v2.1.0):
    - New `icicle` trace type.
    - New `legendrank` trace attribute.
    - Several other additions and bug fixes.
  - [Feature release 2.2.0](https://github.com/plotly/plotly.js/releases/tag/v2.2.0):
    - Legend group titles
    - Half-year directive (`%h`) for date formatting
    - Several other bug fixes and performance improvements
  - [Patch release 2.2.1](https://github.com/plotly/plotly.js/releases/tag/v2.2.1) containing a security fix.

### Added
- [#932](https://github.com/plotly/dash-core-components/pull/932) Adds a new copy to clipboard component.
- [#948](https://github.com/plotly/dash-core-components/pull/948)] Adds `disabled_days` prop to `DatePickerRange` and `DatePickerSingle` components. With this prop you can specify days that should be made unselectable in the date picker, in addition to those that fall outside of the range specified by `min_date_allowed` and `max_date_allowed`.

### Changed
- [#972](https://github.com/plotly/dash-core-components/pull/972) Updated R package vignettes and `dash-info.yaml` to regenerate examples without attaching now-deprecated core component packages (`dashHtmlComponents`, `dashCoreComponents`, or `dashTable`).

## Dash HTML Components
### Changed
- [#194](https://github.com/plotly/dash-html-components/pull/194) Updated dependencies and build process
- [#190](https://github.com/plotly/dash-core-components/pull/190) Updated R package vignettes and `dash-info.yaml` to regenerate examples without attaching now-deprecated core component packages (`dashHtmlComponents`, `dashCoreComponents`, or `dashTable`).

## Dash Table
### Fixed
- [#907](https://github.com/plotly/dash-table/pull/907)
  - Fix a bug where pagination did not work or was not visible. [#834](https://github.com/plotly/dash-table/issues/834)
  - Fix a bug where if you are on a page that no longer exists after the data is updated, no data is displayed. [#892](https://github.com/plotly/dash-table/issues/892)


### Added
- [#916](https://github.com/plotly/dash-table/pull/916)
  - Added `html` option to `markdown_options` prop. This enables the use of html tags in markdown text.

- [#545](https://github.com/plotly/dash-table/issues/545)
    - Case insensitive filtering
    - New props: `filter_options` - to control case of all filters, `columns.filter_options` - to control filter case for each column
    - New operators: `i=`, `ieq`, `i>=`, `ige`, `i>`, `igt`, `i<=`, `ile`, `i<`, `ilt`, `i!=`, `ine`, `icontains` - for case-insensitive filtering, `s=`, `seq`, `s>=`, `sge`, `s>`, `sgt`, `s<=`, `sle`, `s<`, `slt`, `s!=`, `sne`, `scontains` - to force case-sensitive filtering on case-insensitive columns

### Changed
- [#918](https://github.com/plotly/dash-core-components/pull/918) Updated all dependencies. In particular the `highlight.js` upgrade changes code highlighting in markdown: we have long used their "github" style, this has been updated to more closely match current github styles.
- [#901](https://github.com/plotly/dash-core-components/pull/901) Updated R package `dash-info.yaml` to regenerate example without attaching now-deprecated core component packages (`dashHtmlComponents`, `dashCoreComponents`, or `dashTable`).


## [1.20.0] - 2021-04-08

## Dash and Dash Renderer
### Changed
- [#1531](https://github.com/plotly/dash/pull/1531) Update the format of the docstrings to make them easier to read in the reference pages of Dash Docs and in the console. This also addresses [#1205](https://github.com/plotly/dash/issues/1205)
- [#1553](https://github.com/plotly/dash/pull/1553) Increase the z-index of the Dash error menu from 1001 to 1100 in order to make sure it appears above Bootstrap components.

### Fixed
- [#1546](https://github.com/plotly/dash/pull/1546) Validate callback request `outputs` vs `output` to avoid a perceived security issue.

## Dash Core Components
### Added
- [#863](https://github.com/plotly/dash-core-components/pull/863) Adds a new `Download` component. Along with this several utility functions are added to help construct the appropriate data format:
  - `dcc.send_file` - send a file from disk
  - `dcc.send_data_frame` - send a `DataFrame`, using one of its writer methods
  - `dcc.send_bytes` - send a bytestring or the result of a bytestring writer
  - `dcc.send_string` - send a string or the result of a string writer

### Changed
- [#923](https://github.com/plotly/dash-core-components/pull/923)
  Set `autoComplete` to off in `dcc.Dropdown`. This fixes [#808](https://github.com/plotly/dash-core-components/issues/808)

### Fixed
- [#930](https://github.com/plotly/dash-core-components/pull/930) Fixed a bug [#867](https://github.com/plotly/dash-core-components/issues/867) with `DatePickerRange` that would sometimes shift the allowed dates by one day.
- [#934](https://github.com/plotly/dash-core-components/pull/934) Fixed a bug in `EnhancedTab` component that ignored `disabled_className` property

## Dash HTML Components
### Fixed
- [#179](https://github.com/plotly/dash-html-components/pull/179) - Fixes [#77](https://github.com/plotly/dash-html-components/issues/77) Added `allow` and `referrerPolicy` properties to `html.Iframe`

- [#178](https://github.com/plotly/dash-html-components/pull/178) - Fix [#161](https://github.com/plotly/dash-html-components/issues/161) <object> `data` property, and fix [#129](https://github.com/plotly/dash-html-components/issues/129) obsolete, deprecated, and discouraged elements. No elements were removed, but comments were added to the documentation about these elements detailing their limitations.

## Dash Table
### Changed
- [#862](https://github.com/plotly/dash-table/pull/862) - update docstrings per https://github.com/plotly/dash/issues/1205
- [#878](https://github.com/plotly/dash-table/pull/878) - update build process to use Webpack 5 and other latest dependencies

## [1.19.0] - 2021-01-19

## Dash and Dash Renderer
### Added
- [#1508](https://github.com/plotly/dash/pull/1508) Fix [#1403](https://github.com/plotly/dash/issues/1403): Adds an x button
to close the error messages box.
- [#1525](https://github.com/plotly/dash/pull/1525) Adds support for callbacks which have overlapping inputs and outputs. Combined with `dash.callback_context` this addresses many use cases which require circular callbacks.

### Changed
- [#1503](https://github.com/plotly/dash/pull/1506) Fix [#1466](https://github.com/plotly/dash/issues/1466): loosen `dash[testing]` requirements for easier integration in external projects. This PR also bumps many `dash[dev]` requirements.

### Fixed
- [#1530](https://github.com/plotly/dash/pull/1530) Dedent error messages more carefully.
- [#1527](https://github.com/plotly/dash/issues/1527) 🐛 `get_asset_url` now pulls from an external source if `assets_external_path` is set.
  - updated `_add_assets_resource` to build asset urls the same way as `get_asset_url`.
  - updated doc string for `assets_external_path` Dash argument to be more clear that it will always be joined with the `assets_url_path` argument when determining the url to an external asset.
- [#1493](https://github.com/plotly/dash/pull/1493) Fix [#1143](https://github.com/plotly/dash/issues/1143), a bug where having a file with one of several common names (test.py, code.py, org.py, etc) that imports a dash component package would make `import dash` fail with a cryptic error message asking whether you have a file named "dash.py"

## Dash Core Components
### Fixed
- [#905](https://github.com/plotly/dash-core-components/pull/905) Make sure the `figure` prop of `dcc.Graph` receives updates from user interactions in the graph, by using the same `layout` object as provided in the prop rather than cloning it. Fixes [#879](https://github.com/plotly/dash-core-components/issues/879).
- [#903](https://github.com/plotly/dash-core-components/pull/903) Part of fixing dash import bug https://github.com/plotly/dash/issues/1143

### Updated
- [#911](https://github.com/plotly/dash-core-components/pull/911), [#906](https://github.com/plotly/dash-core-components/pull/906)
  - Upgraded Plotly.js to [1.58.4](https://github.com/plotly/plotly.js/releases/tag/v1.58.4)
    - Patch Release [1.58.4](https://github.com/plotly/plotly.js/releases/tag/v1.58.4)
    - Patch Release [1.58.3](https://github.com/plotly/plotly.js/releases/tag/v1.58.3)

### Added
- [#888](https://github.com/plotly/dash-core-components/pull/888) Adds a `drag_value` prop to `dcc.Slider`to be able to fire callbacks from dragging and releasing the slider.

## Dash HTML Components
### Fixed
- [#169](https://github.com/plotly/dash-html-components/pull/169) - part of fixing dash import bug https://github.com/plotly/dash/issues/1143

## Dash Table
### Fixed
- [#854](https://github.com/plotly/dash-table/pull/854) - part of fixing dash import bug https://github.com/plotly/dash/issues/1143

## [1.18.1] - 2020-12-09

## [1.18.0] - 2020-12-07

## [1.17.0] - 2020-10-29
### Changed
- [#1442](https://github.com/plotly/dash/pull/1442) Update from React 16.13.0 to 16.14.0
### Fixed
- [#1434](https://github.com/plotly/dash/pull/1434) Fix [#1432](https://github.com/plotly/dash/issues/1432) for Julia to import non-core component packages without possible errors.

### Changed
- [#1448](https://github.com/plotly/dash/pull/1448) Provide a hint in the callback error when the user forgot to make `app.callback(...)` a decorator.

## [1.16.3] - 2020-10-07
### Fixed
- [#1426](https://github.com/plotly/dash/pull/1426) Fix a regression caused by `flask-compress==1.6.0` causing performance degradation on server requests

## [1.16.2] - 2020-09-25
### Fixed
- [#1415](https://github.com/plotly/dash/pull/1415) Fix a regression with some layouts callbacks involving dcc.Tabs, not yet loaded dash_table.DataTable and dcc.Graph to not be called
- [#1416](https://github.com/plotly/dash/pull/1416) Make callback graph more robust for complex apps and some specific props (`width` in particular) that previously caused errors.

## [1.16.1] - 2020-09-16
### Changed
- [#1376](https://github.com/plotly/dash/pull/1376) Extends the `getTransform` logic in the renderer to handle `persistenceTransforms` for both nested and non-nested persisted props. This was used to to fix [dcc#700](https://github.com/plotly/dash-core-components/issues/700) in conjunction with [dcc#854](https://github.com/plotly/dash-core-components/pull/854) by using persistenceTransforms to strip the time part of the datetime so that datepickers can persist when defined in callbacks.

### Fixed
- [#1408](https://github.com/plotly/dash/pull/1408) Fixes a bug where the callback graph layout would reset whenever a callback fired, losing user-initiated layout changes ([#1402](https://github.com/plotly/dash/issues/1402)) or creating a new force layout ([#1401](https://github.com/plotly/dash/issues/1401))

## [1.16.0] - 2020-09-03
### Added
- [#1371](https://github.com/plotly/dash/pull/1371) You can now get [CSP `script-src` hashes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src) of all added inline scripts by calling `app.csp_hashes()` (both Dash internal inline scripts, and those added with `app.clientside_callback`) .

### Changed
- [#1385](https://github.com/plotly/dash/pull/1385) Closes [#1350](https://github.com/plotly/dash/issues/1350) and fixes a previously undefined callback behavior when multiple elements are stacked on top of one another and their `n_clicks` props are used as inputs of the same callback. The callback will now trigger once with all the triggered `n_clicks` props changes.
- [#1179](https://github.com/plotly/dash/pull/1179) New and improved callback graph in the debug menu. Now based on Cytoscape for much more interactivity, plus callback profiling including number of calls, fine-grained time information, bytes sent and received, and more. You can even add custom timing information on the server with `callback_context.record_timing(name, seconds)`

### Fixed
- [#1384](https://github.com/plotly/dash/pull/1384) Fixed a bug introduced by [#1180](https://github.com/plotly/dash/pull/1180) breaking use of `prevent_initial_call` as a positional arg in callback definitions

## [1.15.0] - 2020-08-25
### Added
- [#1355](https://github.com/plotly/dash/pull/1355) Removed redundant log message and consolidated logger initialization. You can now control the log level - for example suppress informational messages from Dash with `app.logger.setLevel(logging.WARNING)`.
- [#1253](https://github.com/plotly/dash/pull/1253), [#1377](https://github.com/plotly/dash/pull/1377) Added experimental `--jl-prefix` option to `dash-generate-components`, optionally generates Julia version of components and corresponding Julia package

### Changed
- [#1180](https://github.com/plotly/dash/pull/1180) and [#1375](https://github.com/plotly/dash/pull/1375) `Input`, `Output`, and `State` in callback definitions don't need to be in lists. You still need to provide `Output` items first, then `Input` items, then `State`, and the list form is still supported. In particular, if you want to return a single output item wrapped in a length-1 list, you should still wrap the `Output` in a list. This can be useful for procedurally-generated callbacks.
- [#1368](https://github.com/plotly/dash/pull/1368) Updated pytest to v6.0.1. To avoid deprecation warnings, this also updated pytest-sugar to 0.9.4 and pytest-mock to 3.2.0. The pytest-mock update only effects python >= 3.0. Pytest-mock remains pinned at 2.0.0 for python == 2.7.

## [1.14.0] - 2020-07-27
### Added
- [#1343](https://github.com/plotly/dash/pull/1343) Add `title` parameter to set the
document title. This is the recommended alternative to setting app.title or overriding
the index HTML.
- [#1315](https://github.com/plotly/dash/pull/1315) Add `update_title` parameter to set or disable the "Updating...." document title during updates. Closes [#856](https://github.com/plotly/dash/issues/856) and [#732](https://github.com/plotly/dash/issues/732)

## [1.13.4] - 2020-06-25
### Fixed
- [#1310](https://github.com/plotly/dash/pull/1310) Fix a regression since 1.13.0 preventing more than one loading state from being shown at a time.

## [1.13.3] - 2020-06-19

## [1.13.2] - 2020-06-18
### Fixed
- [#1305](https://github.com/plotly/dash/issues/1305)
    - Fix regression that causes crash when `FLASK_ENV` is modified during app execution
    - Fix regression that caused tests using `_wait_for_callbacks` to fail

## [1.13.1] - 2020-06-17

## [1.13.0] - 2020-06-17
### Added
- [#1289](https://github.com/plotly/dash/pull/1289) Supports `DASH_PROXY` env var to tell `app.run_server` to report the correct URL to view your app, when it's being proxied. Throws an error if the proxy is incompatible with the host and port you've given the server.
- [#1240](https://github.com/plotly/dash/pull/1240) Adds `callback_context` to clientside callbacks (e.g. `dash_clientside.callback_context.triggered`). Supports `triggered`, `inputs`, `inputs_list`, `states`, and `states_list`, all of which closely resemble their serverside cousins.

### Changed
- [#1237](https://github.com/plotly/dash/pull/1237) Closes [#920](https://github.com/plotly/dash/issues/920): Converts hot reload fetch failures into a server status indicator showing whether the latest fetch succeeded or failed. Callback fetch failures still appear as errors but have a clearer message.
- [#1254](https://github.com/plotly/dash/pull/1254) Modifies the callback chain implementation and improves performance for apps with a lot of components

### Fixed
- [#1255](https://github.com/plotly/dash/pull/1255) Hard hot reload targets only the current window, not the top - so if your app is in an iframe you will only reload the app
- [#1249](https://github.com/plotly/dash/pull/1249) Fixes [#919](https://github.com/plotly/dash/issues/919) so `dash.testing` is compatible with more `pytest` plugins, particularly `pytest-flake8` and `pytest-black`.
- [#1248](https://github.com/plotly/dash/pull/1248) Fixes [#1245](https://github.com/plotly/dash/issues/1245), so you can use prop persistence with components that have dict IDs, ie for pattern-matching callbacks.
- [#1185](https://github.com/plotly/dash/pull/1185) Sort asset directories, same as we sort files inside those directories. This way if you need your assets loaded in a certain order, you can add prefixes to subdirectory names and enforce that order.
- [#1288](https://github.com/plotly/dash/pull/1288) Closes [#1285](https://github.com/plotly/dash/issues/1285): Debug=True should work in the __main__ module.

## [1.12.0] - 2020-05-05
### Added
- [#1228](https://github.com/plotly/dash/pull/1228) Adds control over firing callbacks on page (or layout chunk) load. Individual callbacks can have their initial calls disabled in their definition `@app.callback(..., prevent_initial_call=True)` and similar for `app.clientside_callback`. The app-wide default can also be changed with `app=Dash(prevent_initial_callbacks=True)`, then individual callbacks may disable this behavior.
- [#1201](https://github.com/plotly/dash/pull/1201) New attribute `app.validation_layout` allows you to create a multi-page app without `suppress_callback_exceptions=True` or layout function tricks. Set this to a component layout containing the superset of all IDs on all pages in your app.
- [#1078](https://github.com/plotly/dash/pull/1078) Permit usage of arbitrary file extensions for assets within component libraries

### Fixed
- [#1224](https://github.com/plotly/dash/pull/1224) Fixes [#1223](https://github.com/plotly/dash/issues/1223), a very specific situation in which initial callbacks will not fire.
- [#1220](https://github.com/plotly/dash/pull/1220) Fixes [#1216](https://github.com/plotly/dash/issues/1216), a set of related issues about pattern-matching callbacks with `ALL` wildcards in their `Output` which would fail if no components matched the pattern.
- [#1212](https://github.com/plotly/dash/pull/1212) Fixes [#1200](https://github.com/plotly/dash/issues/1200) - prior to Dash 1.11, if none of the inputs to a callback were on the page, it was not an error. This was, and is now again, treated as though the callback raised PreventUpdate. The one exception to this is with pattern-matching callbacks, when every Input uses a multi-value wildcard (ALL or ALLSMALLER), and every Output is on the page. In that case the callback fires as usual.
- [#1201](https://github.com/plotly/dash/pull/1201) Fixes [#1193](https://github.com/plotly/dash/issues/1193) - prior to Dash 1.11, you could use `flask.has_request_context() == False` inside an `app.layout` function to provide a special layout containing all IDs for validation purposes in a multi-page app. Dash 1.11 broke this when we moved most of this validation into the renderer. This change makes it work again.

## [1.11.0] - 2020-04-10
### Added
- [#1103](https://github.com/plotly/dash/pull/1103) Pattern-matching IDs and callbacks. Component IDs can be dictionaries, and callbacks can reference patterns of components, using three different wildcards: `ALL`, `MATCH`, and `ALLSMALLER`, available from `dash.dependencies`. This lets you create components on demand, and have callbacks respond to any and all of them. To help with this, `dash.callback_context` gets three new entries: `outputs_list`, `inputs_list`, and `states_list`, which contain all the ids, properties, and except for the outputs, the property values from all matched components.
- [#1103](https://github.com/plotly/dash/pull/1103) `dash.testing` option `--pause`: after opening the dash app in a test, will invoke `pdb` for live debugging of both Javascript and Python. Use with a single test case like `pytest -k cbwc001 --pause`.

### Changed
- [#1103](https://github.com/plotly/dash/pull/1103) Multiple changes to the callback pipeline:
  - `dash.callback_context.triggered` now does NOT reflect any initial values, and DOES reflect EVERY value which has been changed either by activity in the app or as a result of a previous callback. That means that the initial call of a callback with no prerequisite callbacks will list nothing as triggering. For backward compatibility, we continue to provide a length-1 list for `triggered`, but its `id` and `property` are blank strings, and `bool(triggered)` is `False`.
  - A user interaction which returns the same property value as was previously present will not trigger the component to re-render, nor trigger callbacks using that property as an input.
  - Callback validation is now mostly done in the browser, rather than in Python. A few things - mostly type validation, like ensuring IDs are strings or dicts and properties are strings - are still done in Python, but most others, like ensuring outputs are unique, inputs and outputs don't overlap, and (if desired) that IDs are present in the layout, are done in the browser. This means you can define callbacks BEFORE the layout and still validate IDs to the layout; and while developing an app, most errors in callback definitions will not halt the app.

### Fixed
- [#1103](https://github.com/plotly/dash/pull/1103) Fixed multiple bugs with chained callbacks either not triggering, inconsistently triggering, or triggering multiple times. This includes: [#635](https://github.com/plotly/dash/issues/635), [#832](https://github.com/plotly/dash/issues/832), [#1053](https://github.com/plotly/dash/issues/1053), [#1071](https://github.com/plotly/dash/issues/1071), and [#1084](https://github.com/plotly/dash/issues/1084). Also fixed [#1105](https://github.com/plotly/dash/issues/1105): async components that aren't rendered by the page (for example in a background Tab) would block the app from executing callbacks.

## [1.10.0] - 2020-04-01
### Added
- [#1134](https://github.com/plotly/dash/pull/1134) Allow `dash.run_server()` host and port parameters to be set with environment variables HOST & PORT, respectively

### Changed
- [#1145](https://github.com/plotly/dash/pull/1145) Update from React 16.8.6 to 16.13.0

### Fixed
- [#1142](https://github.com/plotly/dash/pull/1142) [Persistence](https://dash.plot.ly/persistence): Also persist 0, empty string etc

## [1.9.1] - 2020-02-27
### Added
- [#1133](https://github.com/plotly/dash/pull/1133) Allow the `compress` config variable to be set with an environment variable with DASH_COMPRESS=FALSE

## [1.9.0] - 2020-02-04
### Fixed
- [#1080](https://github.com/plotly/dash/pull/1080) Handle case where dash fails to load when used inside an iframe with a sandbox attribute that only has allow-scripts

## [1.8.0] - 2020-01-14
### Added
- [#1073](https://github.com/plotly/dash/pull/1073) Two new functions to simplify usage handling URLs and pathnames: `app.get_relative_path` & `app.trim_relative_path`.
These functions are particularly useful for apps deployed on Dash Enterprise where the apps served under a URL prefix (the app name) which is unlike apps served on localhost:8050.
    - `app.get_relative_path` returns a path with the config setting `requests_pathname_prefix` prefixed. Use `app.get_relative_path` anywhere you would provide a relative pathname, like `dcc.Link(href=app.relative_path('/page-2'))` or even as an alternative to `app.get_asset_url` with e.g. `html.Img(src=app.get_relative_path('/assets/logo.png'))`.
    - `app.trim_relative_path` a path with `requests_pathname_prefix` and leading & trailing
    slashes stripped from it. Use this function in callbacks that deal with `dcc.Location` `pathname`
    routing.
    Example usage:
    ```python
    app.layout = html.Div([
        dcc.Location(id='url'),
        html.Div(id='content')
    ])
    @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
    def display_content(path):
        page_name = app.strip_relative_path(path)
        if not page_name:  # None or ''
            return html.Div([
                html.Img(src=app.get_relative_path('/assets/logo.png')),
                dcc.Link(href=app.get_relative_path('/page-1')),
                dcc.Link(href=app.get_relative_path('/page-2')),
            ])
        elif page_name == 'page-1':
            return chapters.page_1
        if page_name == "page-2":
            return chapters.page_2
    ```

### Changed
- [#1035](https://github.com/plotly/dash/pull/1035) Simplify our build process.
- [#1074](https://github.com/plotly/dash/pull/1074) Error messages when providing an incorrect property to a component have been improved: they now specify the component type, library, version, and ID (if available).

### Fixed
- [#1037](https://github.com/plotly/dash/pull/1037) Fix no_update test to allow copies, such as those stored and retrieved from a cache.

## [1.7.0] - 2019-11-27
### Added
- [#967](https://github.com/plotly/dash/pull/967) Add support for defining
clientside JavaScript callbacks via inline strings.
- [#1020](https://github.com/plotly/dash/pull/1020) Allow `visit_and_snapshot` API in `dash.testing.browser` to stay on the page so you can run other checks.

### Changed
- [#1026](https://github.com/plotly/dash/pull/1026) Better error message when you forget to wrap multiple `children` in an array, and they get passed to other props.

### Fixed
- [#1018](https://github.com/plotly/dash/pull/1006) Fix the `dash.testing` **stop** API with process application runner in Python2. Use `kill()` instead of `communicate()` to avoid hanging.
- [#1027](https://github.com/plotly/dash/pull/1027) Fix bug with renderer callback lock never resolving with non-rendered async component using the asyncDecorator

## [1.6.1] - 2019-11-14
### Fixed
- [#1006](https://github.com/plotly/dash/pull/1006) Fix IE11 / ES5 compatibility and validation issues
- [#1006](https://github.com/plotly/dash/pull/1006) Fix bug with renderer wrapper component TreeContainer to prevent useless re-renders
- [#1001](https://github.com/plotly/dash/pull/1001)
  - Fix and improve the `clear_input()` API in `dash.testing`, so it's more robust handling react `input`.
  - make the `percy_snapshot()` API more robust, and the timeout of `wait_for_callbacks` (if set to True) will not fail the snapshot execution, but logged as potential error.

## [1.6.0] - 2019-11-04
### Fixed
- [#999](https://github.com/plotly/dash/pull/999) Fix fingerprint for component suites with `metadata` in version.
- [#983](https://github.com/plotly/dash/pull/983) Fix the assets loading issues when dashR application runner is handling with an app defined by string chunk.

## [1.5.1] - 2019-10-29
### Fixed
- [#987](https://github.com/plotly/dash/pull/987) Fix cache string handling for component suites with nested folders in their packages.
- [#986](https://github.com/plotly/dash/pull/986) Fix a bug with evaluation of `_force_eager_loading` when application is loaded with gunicorn

## [1.5.0] - 2019-10-29
### Added
- [#964](https://github.com/plotly/dash/pull/964) Adds support for preventing updates in clientside functions.
  - Reject all updates with `throw window.dash_clientside.PreventUpdate;`
  - Reject a single output by returning `window.dash_clientside.no_update`
- [#899](https://github.com/plotly/dash/pull/899) Add support for async dependencies and components
- [#973](https://github.com/plotly/dash/pull/973) Adds support for resource caching and adds a fallback caching mechanism through etag

### Fixed
- [#974](https://github.com/plotly/dash/pull/974) Fix and improve a percy snapshot behavior issue we found in dash-docs testing. It adds a flag `wait_for_callbacks` to ensure that, in the context of a dash app testing, the percy snapshot action will happen only after all callbacks get fired.

## [1.4.1] - 2019-10-17
### Fixed
- [#969](https://github.com/plotly/dash/pull/969) Fix warnings emitted by react devtools coming from our own devtools components.

## [1.4.0] - 2019-10-08
### Added
- [#948](https://github.com/plotly/dash/pull/948) Support setting working directory for R apps run using the `dashr` fixture, primarily useful for tests with assets. `dashr.start_server` supports a `cwd` argument to set an explicit working directory, and has smarter defaults when it's omitted: if `app` is a path to an R script, uses the directory of that path; if `app` is a string, uses the directory the test file itself is in.
- [#944](https://github.com/plotly/dash/pull/944)
  - Relevant `dash.testing` methods can now be called with either an element or a CSS selector: `select_dcc_dropdown`, `multiple_click`, `clear_input`, `zoom_in_graph_by_ratio`, `click_at_coord_fractions`.
  - Three new `dash.testing` methods: `clear_local_storage`, `clear_session_storage`, and `clear_storage` (to clear both together)
- [#937](https://github.com/plotly/dash/pull/937) `dash.testing` adds two APIs `zoom_in_graph_by_ratio` and `click_at_coord_fractions` about advanced interactions using mouse `ActionChain`
- [#938](https://github.com/plotly/dash/issues/938) Add debugging traces to dash backend about serving component suites, to verify the installed packages whenever in doubt.

### Fixed
- [#944](https://github.com/plotly/dash/pull/944) Fix a bug with persistence being toggled on/off on an existing component.

## [1.3.1] - 2019-09-19
### Changed
- Bump dash-core-components version from 1.2.0 to [1.2.1](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#120---2019-09-19)

## [1.3.0] - 2019-09-17
### Added
- [#923](https://github.com/plotly/dash/pull/923) Add one configuration `--percy-assets` in `pytest` to specify extra application assets path if needed.

- [#918](https://github.com/plotly/dash/pull/918) Add `wait_for_element_by_id` and `visit_and_snapshot` APIs in browser, add `raw_command` option (with higher priority than the default waitress one) and optional `start_timeout` argument to handle large applications within the process runner.

- [#903](https://github.com/plotly/dash/pull/903) Persistence: enable props edited by the user to persist across recreating the component or reloading the page. Components need to define three new props: `persistence`, `persisted_props`, and `persistence_type` as described in the lead comment of `src/persistence.js`. App developers then enable this behavior by, in the simplest case, setting `persistence: true` on the component. First use case is table, see [dash-table#566](https://github.com/plotly/dash-table/pull/566)

### Changed
- Bump dash-table version from 4.2.0 to [4.3.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#430---2019-09-17)
- Bump dash-core-components version from 1.1.2 to [1.2.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#120---2019-09-17)
- Bump dash-renderer version from 1.0.1 to [1.1.0](https://github.com/plotly/dash/blob/master/dash-renderer/CHANGELOG.md#110---2019-09-17)

### Fixed
- [#915](https://github.com/plotly/dash/issues/915) Fix `dash-generate-components` on Windows.
- [#829](https://github.com/plotly/dash/issues/829) Fix the `--remote` pytest argument which was not effective in the code, adding a new argument `--remote-url` to support the selenium grid usage in the cloud.
- [#910](https://github.com/plotly/dash/pull/910) Reduce the dash-renderer packages size on **PyPI** about 55% by removing the source maps. To do more advanced debugging, the source maps needs to be generated from source code with `npm run build:local` and pip install in editable mode, i.e. `pip install -e .`

## [1.2.0] - 2019-08-27
### Added
- [#860](https://github.com/plotly/dash/pull/860) Add a new arg `dev_tools_prune_errors` to `app.run_server` and `app.enable_dev_tools`. Default `True`, tracebacks only include user code and below. Set it `False` for the previous behavior showing all the Dash and Flask parts of the stack.

### Changed
- Bump dash-table version from 4.1.0 to [4.2.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#420---2019-08-27)
- Bump dash-core-components version from 1.1.1 to [1.1.2](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#112---2019-08-27)
- Bump dash-html-components version from 1.0.0 to [1.0.1](https://github.com/plotly/dash-html-components/blob/master/CHANGELOG.md#101---2019-08-27)
- Bump dash-renderer version from 1.0.0 to [1.0.1](https://github.com/plotly/dash/blob/dev/dash-renderer/CHANGELOG.md#101---2019-08-27)

### Fixed
- [#874](https://github.com/plotly/dash/pull/874) Clean all the binary assets in dash-renderer, add tool to build all the required bundles from fresh source code to avoid confusion of the assets and improve the release process. Fixes [#868](https://github.com/plotly/dash/pull/868) and [#734](https://github.com/plotly/dash/pull/734)

## [1.1.1] - 2019-08-06
### Changed
- Bump dash-core-components version from 1.1.0 to [1.1.1](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#111---2019-08-06)

## [1.1.0] - 2019-08-05
### Added
- [#827](https://github.com/plotly/dash/pull/827) Add support for dashR testing to the `dash.testing` pytest framework.

### Changed
- Bump dash-table version from 4.0.2 to [4.1.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#410---2019-08-05)
- Bump dash-core-components version from 1.0.0 to [1.1.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#110---2019-08-05)

## [1.0.2] - 2019-07-15
### Changed
- Bump dash-table version from 4.0.1 to [4.0.2](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#402---2019-07-15)

### Fixed
- [#821](https://github.com/plotly/dash/pull/821) Fix a bug with callback error reporting, [#791](https://github.com/plotly/dash/issues/791).

## [1.0.1] - 2019-07-09
### Changed
- 💥 [#808](https://github.com/plotly/dash/pull/808) Remove strong `dash.testing` dependencies per community feedback. Testing users should do `pip install dash[testing]` afterwards.

- [#805](https://github.com/plotly/dash/pull/805) Add headless mode for dash.testing, add `pytest_setup_options` hook for full configuration of `WebDriver Options`.

- Bump dash-table version from 4.0.0 to [4.0.1](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#401---2019-07-09)

## [1.0.0] - 2019-06-20
### Changed
- 💥 [#761](https://github.com/plotly/dash/pull/761) Several breaking changes to the `dash.Dash` API:
  - Remove two obsolete constructor kwargs: `static_folder` and `components_cache_max_age`
  - Remove the misspelled `supress_callback_exceptions` fallback
  - Remove the unused `resources.config.infer_from_layout`
  - Revamp `app.config`: ALL constructor args are now stored in `config`, with three exceptions: `server`, `index_string`, and `plugins`. None of these are stored in any other instance attributes anymore.
  - Change `hot_reload_interval` from msec to seconds, for consistency with `hot_reload_watch_interval`
  - When called from `enable_dev_tools`, `debug=True` by default. It's still `False` by default from `run_server`.

- ✨ [#744](https://github.com/plotly/dash/pull/744) Introducing Dash Testing (`dash.testing`) - read the full tutorial at <https://dash.plotly.com/testing>.

- [#753](https://github.com/plotly/dash/pull/753) `Component` no longer inherits `MutableMapping`, so `values`, `keys`, and more are no longer methods. Fixes an issue reported in [dcc#440](https://github.com/plotly/dash-core-components/issues/440) where components with certain prop names defined but not provided would cause a failure to render. During component generation we now disallow all props with leading underscores or matching a few remaining reserved words: `UNDEFINED`, `REQUIRED`, `to_plotly_json`, `available_properties`, and `available_wildcard_properties`.

- [#739](https://github.com/plotly/dash/pull/739) Allow the Flask app to be provided to Dash after object initialization. This allows users to define Dash layouts etc when using the app factory pattern, or any other pattern that inhibits access to the app object. This broadly complies with the flask extension API, allowing Dash to be considered as a Flask extension where it needs to be.

- [#774](https://github.com/plotly/dash/pull/774) Allow the Flask app to set the Dash app name if the name is not provided by users.

- [#722](https://github.com/plotly/dash/pull/722) Assets are served locally by default. Both JS scripts and CSS files are affected. This improves robustness and flexibility in numerous situations, but in certain cases initial loading could be slowed. To restore the previous CDN serving, set `app.scripts.config.serve_locally = False` (and similarly with `app.css`, but this is generally less important).

- [#724](https://github.com/plotly/dash/pull/724), [renderer#175](https://github.com/plotly/dash-renderer/pull/175) Undo/redo toolbar is removed by default, you can enable it with `app=Dash(show_undo_redo=true)`. The CSS hack `._dash-undo-redo:{display:none;}` is no longer needed

- 💥 [#709](https://github.com/plotly/dash/pull/709) Merge the `dash-renderer` project into the main dash repo to simplify feature dev workflow. We will keep the [deprecated one](https://github.com/plotly/dash-renderer) for archive purpose.

## [0.43.0] - 2019-05-15
### Changed
- Bump dash-core-components version from 0.47.0 to [0.48.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0480---2019-05-15)
- Bump dash-renderer version from 0.23.0 to [0.24.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0240---2019-05-15)
- Bump dash-table version from 3.6.0 to [3.7.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#370---2019-05-15)

### Fixed
- [renderer#170](https://github.com/plotly/dash-renderer/pull/170) Fix regression on handling PreventUpdate (204 NO CONTENT)

## [0.42.0] - 2019-04-25
### Added
- [#687](https://github.com/plotly/dash/pull/687), [renderer#100](https://github.com/plotly/dash-renderer/pull/100) Dev Tools support. A new UI in the application that automatically display JavaScript & Python error messages, validates your component's properties, and displays a graph of your callback's dependencies. Only enabled in debug mode. Turn this on and off with two new config flags in `app.run_server`:
  - `dev_tools_props_check` - turn on/off property validation.
  - `dev_tools_ui` - turn on/off the UI.

### Fixed
- [renderer#148](https://github.com/plotly/dash-renderer/issues/148) Fix regression for `children=0` case.

## [0.41.0] - 2019-04-10
### Added
- [#672](https://github.com/plotly/dash/pull/672), [renderer#143](https://github.com/plotly/dash-renderer/pull/143) Support for "Clientside Callbacks" - an escape hatch to execute your callbacks in JavaScript instead of Python
- [#676](https://github.com/plotly/dash/pull/676) Add `dev_tools_ui` config flag in `app.run_server` (serialized in `<script id="_dash-config" type="application/json">`) to display or hide the forthcoming Dev Tools UI in Dash's front-end (dash-renderer).
- [#680](https://github.com/plotly/dash/pull/680) Partial updates: leave some multi-output updates unchanged while updating others

### Removed
- [renderer#145](https://github.com/plotly/dash-renderer/pull/145) Remove `dash_renderer._set_react_version` support for 15.4.2 and 16.2.0

### Changed
- Bump dash-core-components version from 0.45.0 to [0.46.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0460---2019-04-10)
- [renderer#145](https://github.com/plotly/dash-renderer/pull/145) Update from React 15.4.2 to React 16.8.6

## [0.40.0] - 2019-03-25
### Changed
- Bump dash-core-components version from 0.44.0 to [0.45.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0450---2019-03-25)
- Bump dash-html-components version from 0.14.0 to [0.15.0](https://github.com/plotly/dash-html-components/blob/master/CHANGELOG.md#0150---2019-03-25)
- [renderer#140](https://github.com/plotly/dash-renderer/pull/140), [renderer#126](https://github.com/plotly/dash-renderer/pull/126) Optimize rendering, and always assign `setProps` to components even with no callbacks to use it.

## [0.39.0] - 2019-03-04
### Added
- [#436](https://github.com/plotly/dash/pull/436) Allow multiple outputs from a single callback.
- [#367](https://github.com/plotly/dash/pull/367) Support custom JavaScript hooks to modify callback payloads and responses.
- [#623](https://github.com/plotly/dash/pull/623) Modify the flask response with custom cookies or headers, using `dash.callback_context.response`.
- [renderer#93](https://github.com/plotly/dash-renderer/pull/93) Loading states API

### Changed
- Bump dash-core-components version from 0.43.1 to [0.44.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0440---2019-03-04)
- Bump dash-html-components version from 0.13.5 to [0.14.0](https://github.com/plotly/dash-html-components/blob/master/CHANGELOG.md#0140---2019-03-04)
- Bump dash-table version from 3.5.0 to [3.6.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#360---2019-03-04)

## [0.38.0] - 2019-02-25
### Added
- [#603](https://github.com/plotly/dash/pull/603) Add components libraries js/css distribution to hot reload watch.
- [#608](https://github.com/plotly/dash/pull/608), [renderer#124](https://github.com/plotly/dash-renderer/pull/124) Callback context:
  - Know which inputs caused a callback to fire: `dash.callback_context.triggered`
  - Input/State values by name `dash.callback_context.states.get('btn.n_clicks')`

### Changed
- Bump dash-table version from 3.4.0 to [3.5.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#350---2019-02-25)
- Bump dash-renderer version from 0.18.0 to [0.19.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0190---2019-02-25)

### Fixed
- Fix missing indentation for generated metadata.json [#600](https://github.com/plotly/dash/issues/600)
- Fix missing component prop docstring error [#598](https://github.com/plotly/dash/issues/598)
- [#492](https://github.com/plotly/dash/pull/492) Move `__repr__` to base component instead of being generated.
- [#605](https://github.com/plotly/dash/pull/605) Raise exception when same input & output are used in a callback

## [0.37.0] - 2019-02-11
### Removed
- [renderer#118](https://github.com/plotly/dash-renderer/pull/118) Removed redux logger for the dev.

### Changed
- [#565](https://github.com/plotly/dash/pull/565) Add core libraries as version locked dependencies
- Bump dash-table version from 3.3.0 to [3.4.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#340---2019-02-08)
- Bump dash-renderer version from 0.17.0 to [0.18.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0180---2019-02-11)
- Bump dash-core-components version from 0.43.0 to [0.43.1](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0431---2019-02-11)

### Fixed
- [#563](https://github.com/plotly/dash/pull/563) Fix collections.abc deprecation warning for Python 3.8

## [0.36.0] - 2019-01-25
### Removed
- [#550](https://github.com/plotly/dash/pull/550), [renderer#114](https://github.com/plotly/dash-renderer/pull/114) Remove support for `Event` system. Use event properties instead, for example the `n_clicks` property instead of the `click` event, see [#531](https://github.com/plotly/dash/issues/531). `dash_renderer` MUST be upgraded to >=0.17.0 together with this, and it is recommended to update `dash_core_components` to >=0.43.0 and `dash_html_components` to >=0.14.0.

## [0.35.3] - 2019-01-23
### Changed
- [#547](https://github.com/plotly/dash/pull/547)
  - `assets_folder` argument now defaults to 'assets'
  - The assets folder is now always relative to the given root path of `name` argument, the default of `__main__` will get the `cwd`.
  - No longer coerce the name argument from the server if the server argument is provided.

### Fixed
- [#547](https://github.com/plotly/dash/pull/547)
  - Asset blueprint takes routes prefix into it's static path.
  - Asset url path no longer strip routes from requests.
- [#548](https://github.com/plotly/dash/pull/548) Remove print statement from PreventUpdate error handler.
- [#524](https://github.com/plotly/dash/pull/524) Removed ComponentRegistry dist cache.

## [0.35.2] - 2019-01-11
### Fixed
- [#522](https://github.com/plotly/dash/pull/522) Fix typo in some exception names
- [renderer#110](https://github.com/plotly/dash-renderer/pull/110)
  - Keep the config store state on soft reload.
  - AppProvider returns `Loading...` if no configs as before [renderer#108](https://github.com/plotly/dash-renderer/pull/108).

## 0.35.1 - 2018-12-27
### Fixed
- [#518](https://github.com/plotly/dash/pull/518) Always skip `dynamic` resources from index resources collection.

## 0.35.0 - 2018-12-18
### Added
- [#483](https://github.com/plotly/dash/pull/483) Experimental `--r-prefix` option to `dash-generate-components`, optionally generates R version of components and corresponding R package.

## 0.34.0 - 2018-12-17
### Added
- [#490](https://github.com/plotly/dash/pull/490) Add `--ignore` option to `dash-generate-components`, defaults to `^_`.

### Removed
- [renderer#108](https://github.com/plotly/dash-renderer/pull/108) Unused login api and Authentication component

### Fixed
- Add `key` to rendered components, fixing [renderer#379](https://github.com/plotly/dash-core-components/issues/379)

## 0.33.0 - 2018-12-10
### Added
- [#487](https://github.com/plotly/dash/pull/487) Add specific Dash exception types to replace generic exceptions (`InvalidIndexException`, `DependencyException`, `ResourceException`)

## 0.32.2 - 2018-12-09
### Fixed
- [#485](https://github.com/plotly/dash/pull/485) Fix typo in missing events/inputs error message

## 0.32.1 - 2018-12-07
### Changed
- [#484](https://github.com/plotly/dash/pull/484) Mute dash related missing props docstring from extract-meta warnings

## 0.32.0 - 2018-12-07
### Added
- [#478](https://github.com/plotly/dash/pull/478), [renderer#104](https://github.com/plotly/dash-renderer/issues/104) Support for .map file extension and dynamic (on demand) loading
- [renderer#107](https://github.com/plotly/dash-renderer/pull/107) [Redux devtools](https://github.com/zalmoxisus/redux-devtools-extension) support

## 0.31.1 - 2018-11-29
### Fixed
- [#473](https://github.com/plotly/dash/pull/473) Fix `_imports_.py` indentation generation.

## 0.31.0 - 2018-11-29
### Added
- [#451](https://github.com/plotly/dash/pull/451) Combine `extract-meta` and Python component files generation in a cli

### Fixed
- Fix a bug [renderer#66](https://github.com/plotly/dash-renderer/issues/66) in the ON_PROP_CHANGE callback where history was not correctly set when acting on more than one component. In particular, the 'undo' button should now work as expected.

## 0.30.0 - 2018-11-14
### Added
- [#362](https://github.com/plotly/dash/pull/362), [renderer#73](https://github.com/plotly/dash-renderer/pull/73) Hot reloading from the browser.
- Silence routes logging with `dev_tools_silence_routes_logging`.

## 0.29.0 - 2018-11-06
### Added
- [#444](https://github.com/plotly/dash/pull/444) Add component namespaces registry, collect the resources needed by component library when they are imported instead of crawling the layout.

## 0.28.7 - 2018-11-05
### Fixed
- [#450](https://github.com/plotly/dash/pull/450) Use the same prop name black list for component generation in all supported Python versions. Closes [#361](https://github.com/plotly/dash/issues/361).

## 0.28.6 - 2018-11-05
### Fixed
- [#443](https://github.com/plotly/dash/pull/443) `Dash.registered_paths` changed to a `collections.defaultdict(set)`, was appending the same package paths on every index.

## 0.28.5 - 2018-10-18
### Fixed
- [#431](https://github.com/plotly/dash/pull/431) Replace windows endline when generating components class docstrings.

## 0.28.4 - 2018-10-18
### Fixed
- [#430](https://github.com/plotly/dash/pull/430) Fix `Component.traverse()` and `Component.traverse_with_paths()` for components with `children` of type `tuple`, not just `list`.

## 0.28.3 - 2018-10-17
### Fixed
- [#418](https://github.com/plotly/dash/pull/418) Fix http-equiv typo
- Include missing polyfills to restore Internet Explorer support, restore whatwg-fetch [renderer#87](https://github.com/plotly/dash-renderer/issues/87)

## 0.28.2 - 2018-10-05
### Changed
- [#377](https://github.com/plotly/dash/pull/377) Move `add_url` function definition out of `Dash.__init__`

## 0.28.1 - 2018-09-26
### Fixed
- [#407](https://github.com/plotly/dash/pull/407) Missing favicon package_data from setup.py

## 0.28.0 - 2018-09-26
### Added
- [#406](https://github.com/plotly/dash/pull/406) Default favicon for dash apps.
- Bust the cache of the assets favicon.

### Fixed
- [#403](https://github.com/plotly/dash/pull/403) Remove the first and last blank lines from the HTML index string.

## 0.27.0 - 2018-09-20
### Added
- [#369](https://github.com/plotly/dash/pull/369), [renderer#77](https://github.com/plotly/dash-renderer/pull/77) Allow serving dev bundles from the components suite, enable with `app.run_server(dev_tools_serve_dev_bundles=True)`

### Fixed
- [#350](https://github.com/plotly/dash/pull/350) Use HTML5 syntax for the meta tag

## 0.26.6 - 2018-09-19
### Fixed
- [#387](https://github.com/plotly/dash/pull/387) Add `Cache-Control` headers to files served by `Dash.serve_component_suites`, and time modified query string to collected components suites resources.
- [#394](https://github.com/plotly/dash/pull/394) Add `InvalidResourceError` error and a Flask error handler so unregistered paths in `serve_component_suites` return a 404 instead of 500.

## 0.26.5 - 2018-09-10
### Fixed
- [#374](https://github.com/plotly/dash/pull/374) Fix `get_asset_url` with a different `assets_url_path`.

## 0.26.4 - 2018-08-28
### Fixed
- Set `url_base_pathname` to `None` in `Dash.__init__`. Fix [#364](https://github.com/plotly/dash/issues/364)

## 0.26.3 - 2018-08-27
### Added
- `Dash.get_asset_url` will give the prefixed url for the asset file.

### Fixed
- [#351](https://github.com/plotly/dash/pull/351) Prefix assets files with `requests_pathname_prefix`.

## 0.26.2 - 2018-08-26
### Fixed
- [#343](https://github.com/plotly/dash/pull/343) Only create the assets blueprint once for apps that provide the same flask instance to multiple dash instances.

## 0.26.1 - 2018-08-26
### Fixed
- [#336](https://github.com/plotly/dash/pull/336) Fix bug in `_validate_layout` which would not let a user set `app.layout` to be a function that returns a layout [(fixes #334)](https://github.com/plotly/dash/issues/334).

## 0.26.0 - 2018-08-20
### Added
- [#318](https://github.com/plotly/dash/pull/318) Add `assets_ignore` init keyword, regex filter for the assets files.

## 0.25.1 - 2018-08-20
### Fixed
- [#335](https://github.com/plotly/dash/pull/335) Ensure CSS/JS external resources are loaded before the assets.

## 0.25.0 - 2018-08-14
### Added
- [#322](https://github.com/plotly/dash/pull/322) Take config values from init or environ variables (Prefixed with `DASH_`).

### Fixed
- Take `requests_pathname_prefix` config when creating scripts tags.
- `requests/routes_pathname_prefix` must start and end with `/`.
- `requests_pathname_prefix` must end with `routes_pathname_prefix`. If you supplied both `requests` and `routes` pathname before this update, make sure `requests_pathname_prefix` ends with the same value as `routes_pathname_prefix`.
- `url_base_pathname` sets both `requests/routes` pathname, cannot supply it with either `requests` or `routes` pathname prefixes.

## 0.24.2 - 2018-08-13
### Fixed
- [#320](https://github.com/plotly/dash/pull/320) Disallow duplicate component ids in the initial layout.

## 0.24.1 - 2018-08-10
### Fixed
- Fix bug [#321](https://github.com/plotly/dash/issues/321) where importing Dash components with no props would result in an error.
- Fix a bug in 0.23.1 where importing components with arguments that are Python keywords could cause an error. In particular, this fixes `dash-html-components` with Python 3.7.

## 0.24.0 - 2018-08-10
### Added
- [#319](https://github.com/plotly/dash/pull/309) Add a modified time query string to assets included in the index in order to bust the cache.

## 0.23.1 - 2018-08-02
### Added
- [#316](https://github.com/plotly/dash/pull/316) Add `ie-compat` meta tag to the index by default.
- [#305](https://github.com/plotly/dash/pull/305) Add `external_script` and `external_css` keywords to dash `__init__`.
- Dash components are now generated at build-time and then imported rather than generated when a module is imported. This should reduce the time it takes to import Dash component libraries, and makes Dash compatible with IDEs.

## 0.22.1 - 2018-08-01
### Fixed
- [#273](https://github.com/plotly/dash/pull/273) Raise a more informative error if a non-JSON-serializable value is returned from a callback.

## 0.22.0 - 2018-07-25
### Added
- [#286](https://github.com/plotly/dash/pull/286) Asset files & index customization.
- [#294](https://github.com/plotly/dash/pull/294) Raise an error if there is no layout present when the server is run.
- [renderer#55](https://github.com/plotly/dash-renderer/pull/55) Add `_dash-error` class to the "Error loading layout" and "Error loading dependencies" messages.

### Fixed
- Attempting to render a `Boolean` value to the page no longer crashes the app.
- [renderer#57](https://github.com/plotly/dash-renderer/issues/57) If a callback references an `id` which does not exist in the DOM tree at the time it is executed, throw a more informative front-end exception.
- [renderer#54](https://github.com/plotly/dash-renderer/pull/54) Previously, if a component called `updateProps` with multiple properties, Dash would fire the callback multiple times (once for each property). Now the callback only fires once.

## 0.21.1 - 2018-04-10
### Added
- [#237](https://github.com/plotly/dash/pull/237) Support `aria-*` and `data-*` attributes in all dash html components. These new keywords can be added using a dictionary expansion, e.g. `html.Div(id="my-div", **{"data-toggle": "toggled", "aria-toggled": "true"})`
- [renderer#45](https://github.com/plotly/dash-renderer/pull/45) Allow user to choose between React versions '15.4.2' and '16.2.0':
```python
import dash_renderer

# Set the react version before setting up the Dash application
dash_renderer._set_react_version('16.2.0')

app = dash.Dash(...)
```

### Fixed
- [renderer#50](https://github.com/plotly/dash-renderer/pull/50) Update MANIFEST.in to include `react` and `react-dom` bundles for development mode

## 0.21.0 - 2018-02-21
### Added
- [#207](https://github.com/plotly/dash/pull/207) Support React components using [Flow](https://flow.org/en/docs/react/) types. `component_loader` now has the following behavior to create docstrings as determined in discussion in [#187](https://github.com/plotly/dash/issues/187):
  1. If a Dash component has `PropTypes`-generated typing, the docstring uses the `PropTypes`, _regardless of whether the component also has Flow types (current behavior)._
  2. Otherwise if a Dash component has Flow types but _not `PropTypes`_, the docstring now uses the objects generated by `react-docgen` from the Flow types.

### Fixed
- [renderer#42](https://github.com/plotly/dash-renderer/pull/42) Fix [renderer#41](https://github.com/plotly/dash-renderer/issues/41) and [renderer#44](https://github.com/plotly/dash-renderer/issues/44).
  - In some cases, during initialization, callbacks may fired multiple times instead of just once. This only happens in certain scenarios where outputs have overlapping inputs and those inputs are leaves (they don't have any inputs of their own).
  - If an output component is returned from a callback and its inputs were _not_ returned from the same input (i.e. they were already visible), then the callback to update the output would not fire. This has now been fixed. A common scenario where this app structure exists is within a Tabbed app, where there are global controls that update each tab's contents and the tab's callback just displays new output containers.

## 0.20.0 - 2018-01-19
### Added
- [#190](https://github.com/plotly/dash/pull/190) `exceptions.PreventUpdate` can be raised inside a callback to prevent the callback from updating the app. See <https://community.plotly.com/t/improving-handling-of-aborted-callbacks/7536/2>.

### Removed
- Removes logging from redux middleware from production build based on process.env.NODE_ENV.

### Changed
- Many pylint style fixes: [#163](https://github.com/plotly/dash/pull/163), [#164](https://github.com/plotly/dash/pull/164), [#165](https://github.com/plotly/dash/pull/165), [#166](https://github.com/plotly/dash/pull/166), [#167](https://github.com/plotly/dash/pull/167), [#168](https://github.com/plotly/dash/pull/168), [#169](https://github.com/plotly/dash/pull/169), [#172](https://github.com/plotly/dash/pull/172), [#173](https://github.com/plotly/dash/pull/173), [#181](https://github.com/plotly/dash/pull/181), [#185](https://github.com/plotly/dash/pull/185), [#186](https://github.com/plotly/dash/pull/186), [#193](https://github.com/plotly/dash/pull/193)
- [#184](https://github.com/plotly/dash/pull/184) New integration test framework.
- [#174](https://github.com/plotly/dash/pull/174) Submodules are now imported into the `dash` namespace for better IDE completion.

## 0.19.0 - 2017-10-16
### Changed
- 🔒 Remove CSRF protection measures. CSRF-style attacks are not relevant to Dash apps. Dash's API uses `POST` requests with content type `application/json` which are not susceptible to unwanted requests from 3rd party sites. See [#141](https://github.com/plotly/dash/issues/141).
- 🔒 `app.server.secret_key` is no longer required since CSRF protection was removed. Setting `app.server.secret_key` was difficult to document and a very common source of confusion, so it's great that users won't get bitten by this anymore :tada:
- 🐞 [renderer#22](https://github.com/plotly/dash-renderer/pull/22), [renderer#28](https://github.com/plotly/dash-renderer/pull/28) Previously, old requests could override new requests if their response was longer than the new one. This caused subtle bugs when apps are deployed on multiple processes or threads with component callbacks that update at varying rates like urls. Originally reported in [#133](https://github.com/plotly/dash/issues/133). This fix should also improve performance when many updates happen at once as outdated requests will get dropped instead of updating the UI. Performance issue with the first PR reported in [renderer#27](https://github.com/plotly/dash-renderer/issues/27) and fixed in the second PR.
- [renderer#21](https://github.com/plotly/dash-renderer/pull/21) Fix an issue where a callback would be fired excessively. Previously, the callback would be called as many times as it had inputs. Now, it is called less.

## 0.18.3 - 2017-09-08
### Added
- `app.config` is now a `dict` instead of a class. You can set config variables with `app.config['suppress_callback_exceptions'] = True` now. The previous class-based syntax (e.g. `app.config.suppress_callback_exceptions`) has been maintained for backwards compatibility.
- 🐌 Experimental behaviour for a customizable "loading state". When a callback is in motion, Dash now appends a `<div class="_dash-loading-callback"/>` to the DOM. Users can style this element using custom CSS to display loading screen overlays. This feature is in alpha, we may remove it at any time.

### Fixed
- Fix a bug from 0.18.2 that removed the ability for dash to serve the app on any route besides `/`.
- Fix a bug from 0.18.0 with the new config variables when used in a multi-app setting, causing config to be shared across apps. Originally reported in <https://community.plotly.com/t/flask-endpoint-error/5691/7>
- Rename config setting `supress_callback_exceptions` to `suppress_callback_exceptions`. The original spelling is kept for backward compatibility.
- 🐞 (renderer) Fix a bug where Dash would fire updates for each parent of a grandchild node that shared the same grandparent. Originally reported in <https://community.plotly.com/t/specifying-dependency-tree-traversal/5080/5>
- 🐞 (renderer) Fix a bug where the document title that displays "Updating..." wouldn't change if the callback raised an Exception. Now it will be removed on any response, even a failure.

## 0.18.2 - 2017-09-07
### Added
- [#70](https://github.com/plotly/dash/pull/70) 🔧 Add an `endpoint` to each of the URLs to allow for multiple routes.

## 0.18.1 - 2017-09-07
### Fixed
- [#128](https://github.com/plotly/dash/pull/128) 🐛 If `app.layout` is a function, then it used to be called excessively. Now it is called just once on startup and just once on page load.

## 0.18.0 - 2017-09-07
### Changed
- 🔒 Remove the `/static/` folder and endpoint that is implicitly initialized by flask. This is too implicit for my comfort level: I worry that users will not be aware that their files in their `static` folder are accessible
- ⚡️ Remove all API calls to the Plotly API (<https://api.plotly.com/>), the authentication endpoints and decorators, and the associated `filename`, `sharing` and `app_url` arguments. This was never documented or officially supported. Authentication has been moved to the [`dash-auth` package](https://github.com/plotly/dash-auth).
- [#107](https://github.com/plotly/dash/pull/107) ✏️ Sort prop names in exception messages.

### Added
- 🔧 Add two new `config` variables: `routes_pathname_prefix` and `requests_pathname_prefix` to provide more flexibility for API routing when Dash apps are run behind proxy servers. `routes_pathname_prefix` is a prefix applied to the backend routes and `requests_pathname_prefix` prefixed in requests made by Dash's front-end. `dash-renderer==0.8.0rc3` uses these endpoints.
- [#112](https://github.com/plotly/dash/pull/112) 🔧 Add `id` to `KeyError` exceptions in components.

### Fixed
- ✏️ Fix a typo in an exception.
- 🔧 Replaced all illegal characters in environment variables.

### 🔧 Maintenance
- 📝 Update README.md
- ✅ Fix CircleCI tests. Note that the [`dash-renderer`](https://github.com/plotly/dash-renderer) contains the bulk of the integration tests.
- 💄 Flake8 fixes and tests (fixes [#99](https://github.com/plotly/dash/issues/99))
- ✨ Add this CHANGELOG.md.

## 0.17.3 - 2017-06-22
✨ This is the initial open-source release of Dash.
