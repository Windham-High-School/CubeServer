# Contributing to CubeServer

Firstly, thank you to anyone interested in helping out- I hope you get a chance to learn something valuable!

Contributing to CubeServer should imply **no commitment**, other than to communicate if plans change and you need someone else to take something over. Reflexively, we hope to communicate back and respond to any questions you might have in a timely manner.

## Current Scope

Currently, we are working to deploy CubeServer for a competition at [WHS](https://github.com/Windham-High-School). Because this project's scope is localized, contributions from outside the organization are not currently expected. The majority of general communications will occur through the [cubeserver-dev GitHub team](https://github.com/orgs/Windham-High-School/teams/cubeserver-dev).


## Branching Model & Workflow

1. Create an **issue** & document the problem
2. Assign the **issue**
3. Create a **feature branch** for the issue (use `develop` as the source branch)
4. Checkout branch, commit, and push to branch
5. Create a **pull request** to merge back into `develop`
6. Pass all status checks and get it **reviewed**
7. After merging, wait for the next **release**, at which point your changes will be merged into `main` and tagged

A few notes-
* All releases are frozen. Security updates and bug fixes will be given a separate [semver](https://semver.org/) and constitute an independent release.
* The `main` branch should always be identical to the latest release. All development between releases will be merged into the `develop` branch.
* Changes that render incompatibility with either the API or the database shall not be made whatsoever while the competition is running. Code should be written in a way so as to automatically perform updates of old database documents or to be backwards-compatible with the old system. Changes that produce incompatibility should result in a new major release. Presumably, there will be a new major release each year.

*All* feature requests, bug reports, improvements, or other modifications start as an issue in the [CubeServer development project](https://github.com/orgs/Windham-High-School/projects/1).
Such issues have the following parameters:

- Assignee (once assigned)
- Labels (please find all relevant labels- it really helps with organization)
- Milestone (if applicable)
- Status

    | Status | What it means |
    | ------ | ------------- |
    | New    | In queue, but not really looked at yet |
    | On Hold| Out of the queue temporarily. (not ignored, but not really that important in the short-term) |
    | Backlog| What's desperately waiting |
    | In Progress| Someone's currently working on fixing this issue |
    | In Review| The fixes / implementation for this issue are awaiting someone's review |
    | Done   | All done, resolved, or wontfix |
    | Merged | If a PR, changes have been merged |
- Priority
    | Priority | What it means |
    | -------- | ------------- |
    | Trivial  | Yeah, this is really not that important. At all. |
    | Low      | ... |
    | Medium   | ... |
    | High     | ... |
    | Urgent   | This is pretty darn important. Nothing else matters nearly as much. |
- Size
    | Size | What it means |
    | ---- | ------------- |
    | Tiny | A few lines of code need to be changed |
    | Small| A few lines times a handful files |
    | Medium| Like a hundred lines ish of changes |
    | Large| A good bit of work, maybe a couple hundred lines |
    | Behemoth| Several hundred or even nearly a thousand lines need to be written / changed. This should be rare; most things of this magnitude should be broken into smaller problems and addressed as such |
- Accessibility
    - This is to help newer programmers assess what they can help with, as well as to give more experienced developers an idea of what they're getting themselves into.

    | Accessibility | What it means |
    | ------------- | ------------- |
    | Easy          | Minimal experience necessary. Little more than a spelling change, syntax error, simple graphic design modififcation, etc.
    | Mid           | Requires some programming experience or learning efforts to tackle, but nothing that cannot be figured out reasonably easily by looking at neighboring code and poking around. |
    | Challenging   | Requires practical or more advanced (especially networking, crypto, database, Docker, threading, etc) computer science experience and may not be straightforward whatsoever |
    | Complex       | This is likely a multi-faceted issue that requires some programming intuition to solve in a timely manner. Experience with Linux, bash scripting, web dev, containerization, threading / processes, databases, OOP, networking, some software conventions, and more may be necessary to understand just the scope of the issue. |
## Commit/PR Guidelines

Please run `./clean` before each commit and/or pull request. If the repository is not left tidy (and there is no excuse; this step is pretty darn easy), your pull request may not be approved.
