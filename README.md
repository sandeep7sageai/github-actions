# github-actions

A sandbox for learning GitHub Actions. It contains four workflows, ordered
from the simplest possible example up to a real CI/CD pipeline for the
`devboard` app, so you can read them in order and see each new concept
layered on top of the last.

## Concepts

### 1. What is a workflow

A workflow is an automated process defined in a YAML file under
`.github/workflows/`. GitHub picks up every file in that folder automatically
— no other registration is needed. Each file has three top-level pieces:

```yaml
name: My Workflow        # shown in the Actions tab

on:                       # the event(s) that trigger a run
  workflow_dispatch:      # e.g. a manual "Run workflow" button

jobs:                     # one or more jobs (an object, so it's indented)
  my-job:
    runs-on: ubuntu-latest  # a fresh, ephemeral VM — created, used, destroyed
    steps:                  # ordered commands/actions run inside that VM
      - name: Say hi
        run: echo "hi"      # `run:` executes a shell command...
      - name: Checkout
        uses: actions/checkout@v7  # ...`uses:` runs a pre-built action instead
```

Key things to know:

- **Jobs run in parallel by default.** If one job must wait for another, say
  so explicitly with `needs: [other-job]`.
- **Triggers (`on`) decide when a workflow fires** — a manual button
  (`workflow_dispatch`), a `push`, a `pull_request`, and so on. Triggers can
  be narrowed with `branches:` and `paths:` filters so a workflow only runs
  for the commits that actually matter to it.
- **Steps are either `run` or `uses`.** `run` executes a raw shell command;
  `uses` runs a reusable action someone else published (checkout code, set up
  a language runtime, log in to Docker, etc.).
- **Secrets and variables** are injected as `${{ secrets.NAME }}` /
  `${{ vars.NAME }}` and are configured in the repo's Settings, never
  hard-coded in the YAML.

### 2. The example workflows, in order

| # | File | Triggers on | What it teaches |
|---|------|-------------|------------------|
| 1 | [`.github/workflows/hello.yml`](.github/workflows/hello.yml) | Manual (`workflow_dispatch`) | The bare minimum: `name` / `on` / `jobs` / `runs-on` / `steps`, one job, one `run` step. |
| 2 | [`.github/workflows/example_cicd.yml`](.github/workflows/example_cicd.yml) | Manual (`workflow_dispatch`) | Multiple jobs and ordering them with `needs`. |
| 3 | [`.github/workflows/lint.yml`](.github/workflows/lint.yml) | `push` to `main` touching `*.py` | Automatic (event-based) triggers, filtering by branch/path, and using a real third-party action (`actions/checkout`). |
| 4 | [`.github/workflows/devboard_ci.yml`](.github/workflows/devboard_ci.yml) | `push` / `pull_request` to `main` touching `devboard/**` | A full CI/CD pipeline: monorepo path scoping, parallel jobs per app component, caching, secrets, and building/pushing Docker images. |

#### 1. `hello.yml` — the "hello world" workflow

One job (`say-hello`), one step, triggered only by hand from the **Actions**
tab. There's nothing here to check out or build — it exists purely to show
the required shape of a workflow file.

#### 2. `example_cicd.yml` — job ordering with `needs`

Four jobs that model a classic pipeline: `code` → `build` → `test` → `deploy`.
`build` needs `code`, `test` needs `build`, and `deploy` needs *both* `build`
and `test`. None of the jobs do real work (each just echoes a message), which
keeps the focus on the dependency graph rather than the tooling — this is the
piece to look at when you want to understand how `needs:` controls run order
and which jobs can run in parallel (`code` alone, then nothing else can start
until it finishes).

#### 3. `lint.yml` — reacting to real events

This one fires automatically: on every `push` to `main` that touches a `.py`
file. Its single job checks the code out (`actions/checkout@v7`), installs
[`ruff`](https://docs.astral.sh/ruff/), and lints the repo. [`example.py`](example.py)
is the file it's meant to check — it currently has a typo (`ifo` instead of
`if`) on line 12, so running this workflow is a quick way to see what a
failing lint step looks like in the Actions log.

#### 4. `devboard_ci.yml` — a real CI/CD pipeline

The most complete example, covering the `devboard` app under
[`devboard/`](devboard/). Notable ideas it introduces:

- **Path-scoped triggers**: `paths: ['devboard/**']` means this workflow only
  runs when something under `devboard/` changes — useful in a monorepo where
  you don't want every workflow firing on every commit.
- **One job per component**: `frontend_ci` and `backend_ci` run in parallel
  since neither declares `needs`, each scoped to its folder with
  `working-directory:`.
- **Language setup + caching**: `actions/setup-node` and `actions/setup-go`
  install the right runtime version, with dependency caching so repeat runs
  are faster.
- **Lint → test → build**, the same shape as `example_cicd.yml`, but with
  real commands (`npm run lint`, `npm run test`, `go vet`, `go test`) instead
  of placeholders.
- **Docker build & push**: `docker/login-action` authenticates to Docker Hub
  using a repo **variable** (`vars.DOCKERHUB_USERNAME`) and a **secret**
  (`secrets.DOCKERHUB_TOKEN`), then `docker/build-push-action` builds each
  service's image and pushes it — the difference between a var (non-secret,
  visible in logs) and a secret (masked) is deliberate here.

### 3. Trying these workflows yourself

- `hello.yml` and `example_cicd.yml` only run when you trigger them manually:
  go to the repo's **Actions** tab, pick the workflow, and click **Run
  workflow**.
- `lint.yml` and `devboard_ci.yml` run automatically on `push`/`pull_request`
  once their path filters match — edit `example.py` or anything under
  `devboard/` and push to `main` (or open a PR) to see them fire.

