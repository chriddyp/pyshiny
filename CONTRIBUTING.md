# Contributor Guide

## Getting Started
Glad that you decided to make your contribution in Dash. This guide provides instructions to set up and build the Dash repository and describes best practices when contributing to the Dash repository. 

### Fork the Dash repository
When contributing to the Dash repository you should always work in your own copy of the Dash repository. Create a fork of the `dev`-branch, to create a copy of the Dash repository in your own GitHub account. See official instructions for [creating a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) if needed.

Clone the forked repository (either option will work). Replace `<your_user_name>` with your user name. 
```
git clone https://github.com/<your_user_name>/dash.git
```
or
```
git clone git@github.com:<your_user_name>/dash.git
```

When working on a new feature, always create a new branch and create the feature in that branch. For more best practices, read the [Git section](#git).

### Configuring your system

<details>
  <summary>For JavaScript beginners: What are nvm, npm and Node?</summary>
  
  If you are new to JavaScript, many aspects of setting up a working environment and working with the new ecosystem can be a bit overwhelming. Especially if Plotly Dash is your first experience with the JavaScript ecosystem. This section explains common terms that are used when working with JavaScript environments: `nvm`, `Node`, and `npm`
  - `nvm` stands for Node Version Manager. This is a tool that allows you to manage Node installations. Quite convenient if you are working on multiple tools that require different versions of Node.js. `nvm` allows you to switch between Node installations with a single command. 
  - `Node.js` is the actual JavaScript runtime environment. Visit the [official site](https://nodejs.org/en) for more info. Don't download Node just yet, install it through `nvm`.
  - `npm` stands for Node Package Manager. This is the largest software registry for JavaScript packages. Check the [official site](https://docs.npmjs.com/about-npm) for more info.

  ---
</details>

<details>
  
<summary>Installing JavaScript on your system</summary>

  > **For Windows users**: `nvm` is not integrated in Windows so a third-party tool needs to be used. If you don't have one yet, you can start with [NVM for Windows](https://github.com/coreybutler/nvm-windows) (`nvm-windows`). This version manager is widely used and is well recommended.
  >
  > Carefully follow the installation instructions listed on the GitHub page. As recommended by the installation instructions there: uninstall any pre-existsing Node installations. You will run into permission errors otherwise.

  With `nvm` available from the command line open any terminal of your preference and install Node and npm:
  ```
  nvm install latest
  ```
  After installation is complete, activate the Node environment (**admin access required**)
  ```
  nvm use latest
  ```
  Confirm that the activation was successfull
  ```
  node -v
  npm -v
  ```
  If these commands are not recognized, close the terminal, re-open a new instance and retry. If the commands return a version number, you have set up your JavaScript environment successfully!
  
  ---
</details>

## Building Dash
### For Windows users: use a Bash terminal
The scripts that run during the build process are designed for a Bash terminal. The default terminals on Windows systems are either PowerShell or Command Prompt. However, the build process will fail (potentially bricking your Node environment) when using these terminals. 

The listed commands should be executed from a Bash terminal, e.g. you can use the Git Bash terminal (which is normally installed when installing Git using the default settings). Otherwise, you need to find another way to access a Bash terminal. 

### Build process
The build process is mostly the same for Windows and Linux systems. Wherever there are differences between the operating systems, it is marked. 

<details>
  <summary> Pycharm automatically loads Python environments! </summary>
  
  If you work in Pycharm you can open the Dash repo directory as a project (`File -> Open` then browse for the `dash` directory containing your dash repo, and open the directory as a project). You can configure your Python virtual environment using the Python Interpreter tool. 
  
  Secondly, you can open the Git Bash terminal in Pycharm and it will automatically activate your selected Python Interpreter in the terminal. You can verify this by executing `pip --version` in the Git Bash terminal, it will show you the path from where pip is run, which is the path where your virtual environment is installed. If you follow these steps, you can skip the first few steps in the overview below.
  
  ---
</details>

Open a Bash terminal in the `dash` repository, Git Bash terminal for example on Windows. Create and activate virtual environment (skip this part if you manage the Python Interpreter via Pycharm):
- Linux/Mac:

  On some Linux/Mac environments, use `.` instead of `source`
  ```bash
  $ python3 -m venv .venv/dev
  $ source .venv/dev/bin/activate
  ```
- Windows:
  ```bash
  $ python -m venv .venv/dev
  $ source .venv/dev/scripts/activate
  ```

Install dash and dependencies:
```bash
$ pip install -e .[ci,dev,testing,celery,diskcache]  # in some shells you need \ to escape []
$ npm ci
```
`npm ci` does a clean install of all packages listed in package-lock.json. Package versions will be exactly like stated in the file.

Next, build dash-core-components, dash-html-components, dash-table, and renderer bundles. This will build all bundles from source code in their respective directories. The only true source of npm version is defined in package.json for each package:
- Linux/Mac:
  ```bash
  $ npm run build  # runs `renderer build` and `npm build` in dcc, html, table
  ```

- Windows:
  
  On Windows the build is done via the first-build script. This adds extra steps that are automatically applied on Linux systems, but not on Windows systems:
  ```bash
  $ npm run first-build
  ```

When you first clone the repository, and check out a new branch, you must run the full build as above. Later on, when you only work in one part of the library, you could run part of the build process e.g.
```bash
$ dash-update-components "dash-core-components"

```
to only build dcc when developing dcc.

Build and install components used in tests:
```bash
$ npm run setup-tests.py # or npm run setup-tests.R
```

Finally, check that the installation succeeded by checking the output of this command:
```bash
$ pip list | grep dash
```

The output should look like this:
```bash
dash                            <version number>                     /path/to/local/dash/repo/
```

### Dash-Renderer Beginner Guide

`Dash Renderer` began as a separate repository. It was merged into the main `Dash` repository as part of the 1.0 release. It is the common frontend for all Dash backends (**R** and **Python**), and manages React Component layout and backend event handling.

If you want to contribute or simply dig deeper into Dash, we encourage you to play and taste it. This is the most efficient way to learn and understand everything under the hood.

For contributors with a primarily **Python** or **R** background, this section might help you understand more details about developing and debugging in JavaScript world.

As of Dash 1.2, the renderer bundle and its peer dependencies can be packed and generated from the source code. The `dash-renderer\package.json` file is the one version of the truth for dash renderer version and npm dependencies. A build tool `renderer`, which is a tiny Python script installed by Dash as a command-line tool, has a few commands which can be run from within the `dash/dash-renderer` directory:

1. `renderer clean` deletes all the previously generated assets by this same tool.
2. `renderer npm` installs all the npm modules using this `package.json` files. Note that the `package-lock.json` file is the computed reference product for the versions defined with tilde(~) or caret(^) syntax in npm.
3. `renderer bundles` parses the locked version JSON, copies all the peer dependencies into dash_renderer folder, bundles the renderer assets, and generates an `__init__.py` to map all the resources. There are also a list of helpful `scripts` property defined in `package.json` you might need to do some handy tasks like linting, syntax format with prettier, etc.
4. `renderer digest` computes the content hash of each asset in `dash_renderer` folder, prints out the result in logs, and dumps into a JSON file `digest.json`. Use this when you have a doubt about the current assets in `dash_renderer`, and compare it with previous result in one shot by this command.
5. `renderer build` runs 1, 2, 3, 4 in sequence as a complete build process from scratch.
6. `renderer build local` runs the same order as in 5 and also generates source maps for debugging purposes.

When a change in renderer code doesn't reflect in your browser as expected, this could be: confused bundle generation, caching issue in a browser, Python package not in `editable` mode, etc. The new tool reduces the risk of bundle assets by adding the digest to help compare asset changes.

### Development of `dash-core-components`, `dash-html-components`, and `dash_table`

Specific details on making changes and contributing to `dcc`, `html`, and `dash_table` can be found within their respective sub-directories in the `components` directory. Once changes have been made in the specific directories, the `dash-update-components` command line tool can be used to update the build artifacts and dependencies of the respective packages within Dash. For example, if a change has been made to `dash-core-components`, use `dash-update-components "dash-core-components"` to move the build artifacts to Dash. By default, this is set to update `all` packages.

## Git

Use the [GitHub flow](https://guides.github.com/introduction/flow/) when proposing contributions to this repository (i.e. create a feature branch and submit a PR against the default branch).

### Organize your commits

For pull request with notable file changes or a big feature development, we highly recommend to organize the commits in a logical manner, so it

- makes a code review experience much more pleasant
- facilitates a possible cherry picking with granular commits

*an intuitive [example](https://github.com/plotly/dash-core-components/pull/548) is worth a thousand words.*

#### Git Desktop

Git command veterans might argue that a simple terminal and a cherry switch keyboard is the most elegant solution. But in general, a desktop tool makes the task easier.

1. <https://www.gitkraken.com/git-client>
2. <https://desktop.github.com/>

### Emoji

Plotlyers love to use emoji as an effective communication medium for:

**Commit Messages**

Emojis make the commit messages :cherry_blossom:. If you have no idea about what to add ? Here is a nice [cheatsheet](https://gitmoji.carloscuesta.me/) and just be creative!

**Code Review Comments**

- :dancer: `:dancer:` - used to indicate you can merge! Equivalent to GitHub's :squirrel:
- :cow2: `:cow2:` cow tip - minor coding style or code flow point
- :tiger2: `:tiger2:` testing tiger - something needs more tests, or tests need to be improved
- :snake: `:snake:` security snake - known or suspected security flaw
- :goat: `:goat:` grammar goat
- :smile_cat: `:smile_cat:` happy cat - for bits of code that you really like!
- :dolls: `:dolls:` documentation dolls
- :pill: `:pill:` performance enhancing pill
- :hocho: `:hocho:` removal of large chunks of code (obsolete stuff, or feature removals)
- :bug: `:bug:` - a bug of some kind. 8 legged or 6. Sometimes poisonous.
- :camel: :palm_tree: `:camel:` `:palm_tree:` - The Don't Repeat Yourself (DRY) camel or palm tree.
- :space_invader: `:space_invader:` - Too much space or too little.
- :spaghetti: `:spaghetti:` - copy-pasta, used to signal code that was copy-pasted without being updated

### Coding Style

We use `flake8`, `pylint`, and [`black`](https://black.readthedocs.io/en/stable/) for linting. please refer to the relevant steps in `.circleci/config.yml`.

## Tests

Before running tests, make sure to set up the test environment:
```bash
npm run setup-tests.py # or npm run setup-tests.R
```

Our tests use Google Chrome via Selenium. You will need to install [ChromeDriver](https://chromedriver.chromium.org/getting-started) matching the version of Chrome installed on your system. Here are some helpful tips for [Mac](https://www.kenst.com/2015/03/installing-chromedriver-on-mac-osx/) and [Windows](http://jonathansoma.com/lede/foundations-2018/classes/selenium/selenium-windows-install/).

We use [pytest](https://docs.pytest.org/en/latest/) as our test automation framework, plus [jest](https://jestjs.io/) for a few renderer unit tests. You can `npm run test` to run them all, but this command simply runs `pytest` with no arguments, then `cd dash-renderer && npm run test` for the renderer unit tests.

Most of the time, however, you will want to just run a few relevant tests and let CI run the whole suite. `pytest` lets you specify a directory or file to run tests from (eg `pytest tests/unit`) or a part of the test case name using `-k` - for example `pytest -k cbcx004` will run a single test, or `pytest -k cbcx` will run that whole file. See the [testing tutorial](https://dash.plotly.com/testing) to learn about the test case ID convention we use.

### Unit Tests

For simple API changes, please add adequate unit tests under `/tests/unit`

Note: *You might find out that we have more integration tests than unit tests in Dash. This doesn't mean unit tests are not important, the [test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) is still valid. Dash project has its unique traits which needs more integration coverage than typical software project, another reason was that dash was a quick prototype crafted by chris in a lovely montreal summer.*

### Integration Tests

We introduced the `dash.testing` feature in [Dash 1.0](https://community.plotly.com/t/announcing-dash-testing/24868). It makes writing a Dash integration test much easier. Please read the [tutorial](https://dash.plotly.com/testing) and add relevant integration tests with any new features or bug fixes.

## Financial Contributions

Dash, and many of Plotly's open source products, have been funded through direct sponsorship by companies. [Get in touch] about funding feature additions, consulting, or custom app development.

[Dash Core Components]: https://dash.plotly.com/dash-core-components
[Dash HTML Components]: https://github.com/plotly/dash-html-components
[write your own components]: https://dash.plotly.com/plugins
[Dash Component Boilerplate]: https://github.com/plotly/dash-component-boilerplate
[issues]: https://github.com/plotly/dash-core-components/issues
[GitHub flow]: https://guides.github.com/introduction/flow/
[semantic versioning]: https://semver.org/
[Dash Community Forum]: https://community.plotly.com/c/dash
[Get in touch]: https://plotly.com/products/consulting-and-oem
[Documentation]: https://github.com/orgs/plotly/projects/8
[Dash Docs]: https://github.com/plotly/dash-docs
