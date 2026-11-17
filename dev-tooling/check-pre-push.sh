#!/usr/bin/env bash
set -uo pipefail

# Ratified shell-quality deviation: this pre-push gate intentionally does not
# use errexit because a green-token miss should fall through to the full check.
if uv run python -m livespec_dev_tooling.green_token check 2>&1; then
    # A token match no longer skips the aggregate: the token memoizes a tree, and members that read
    # state outside the tree (master CI, branch protection, the ledger, the workflow-edit exemption)
    # can answer differently for the same tree, so a refused or partial earlier run must not
    # stand in for this push (livespec-dev-tooling-mj37jk; dev-tooling fdd0ea878).
    echo ":: pre-push: green token matched - NOT skipping the aggregate; members that read state outside the tree must run on this push"
fi

# A delegating host hands the gate to the remote executor. The exec is
# load-bearing: a delegated run that reaches no verdict must refuse the push and
# never fall through to the local aggregate. A host that cannot read the gates
# kubeconfig (a Fabro sandbox) and the gate pod itself exit `enabled` non-zero
# and run `just check` below.
if uv run python -m livespec_dev_tooling.gate_remote_delegate enabled; then
    echo ":: pre-push: delegating the gate to the remote executor"
    exec uv run python -m livespec_dev_tooling.gate_remote_delegate run
fi

just check
