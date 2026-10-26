# Prepared staging architecture and gated promotion
Target: one existing small Linux VM running API, worker and static web containers, with
private PostgreSQL and HTTPS ingress. This is a cost-conscious single-environment design;
no Kubernetes, broker or platform-specific cloud infrastructure is needed. The repository
does not provision a VM, database, registry, DNS, identity or paid service. High availability
and managed database operations are future production decisions.

## External bootstrap prerequisites (not activated)
An operator must provision/approve the target separately. Install Docker Compose and
Python on the existing host. Under /opt/revenueops/staging place the reviewed
infra/staging.compose.yaml as compose.yaml, scripts/staging_host.py, a private runtime.env,
an EXISTING_STAGING_ONLY marker, recovery/ directory, and .release.env containing the
currently deployed known-good API_IMAGE and WEB_IMAGE digest pair. The initial deployment
must already exist; promotion deliberately refuses a blank target. runtime.env must set
production mode, demo disabled, a random JWT secret, explicit HTTPS origin, private DB
credentials, baseline or explicitly approved local-model configuration. Apply compatible
migrations and test a backup restore separately. Promotion does not run schema changes.

Configure GitHub environment staging with required reviewers, prevent self-review,
selected branches allowing only main, and no administrative bypass as normal practice.
Set STAGING_ENABLED=true, STAGING_HOST, STAGING_USER, STAGING_URL (HTTPS). Secrets:
STAGING_SSH_KEY and STAGING_KNOWN_HOSTS. Pin verified host keys out-of-band; never use
ssh-keyscan as a trust decision during a release. Use a dedicated deployment account,
network allowlisting and restricted SSH command access; Docker administration is privileged.
This generic VM target has no cloud OIDC API to obtain SSH credentials. A scoped rotated
SSH key is used; prefer short-lived SSH certificates when an existing issuer is available.
Registry pull credentials are separately provisioned on the host; workflow GITHUB_TOKEN
has job-only package publishing rights. No secret values belong in Git or manifests.

## Fail-closed workflow
Manual deploy-staging.yml dispatch only from main. Requires full lowercase source SHA,
DEPLOY STAGING confirmation, schema/backup compatibility assertion. Read-only preflight
checks source ancestry, exact successful verify.yml push-on-main run, protected environment
reviewers and branch restriction. The gated job then checks actual independent approval
history before any registry publish or SSH mutation. Missing environment protection fails.

Capture and upload the prior digest pair first. Build verified source with revision labels,
push uniquely named images and consume immutable output digests. Manifest validation
permits only this repository's API/web image paths and SHA-256 references. Host rejects
baseline drift, takes an exclusive promotion lock, saves a recovery manifest, pulls and
checks each image's revision label against the verified source SHA, then atomically updates
desired digest references and restarts only API/worker/web. Running container image
references must match the target pair. HTTPS smoke checks database health and anonymous
401. These checks do not certify all financial workflows or live model quality.

## Rollback and partial failures
Dispatch operation=rollback with the previous full source SHA (also successful main CI),
its API/web sha256 digests from a recorded release pair, and renewed independent review.
The same registry, label, schema and drift checks apply. No rebuilding and no automatic
schema downgrade. Keep backward-compatible migrations; restore a tested backup only by
an explicit incident decision. Failed pulls leave recovery evidence; failed restarts can
leave a partially updated pair. Inspect host recovery/, the uploaded staging-before and
release manifests and container states before reviewed rollback. A failed promotion is
never reported as deployed. Do not reset a staging DB merely to restore an image.

## Verification status
Release guard/manifest safety logic tested locally using synthetic responses. Workflow
syntax checked with official actionlint. No environment, key, host or registry credentials
were configured. Read-only remote inspection found zero Actions runs and zero GitHub
environments at the time of implementation. No workflow dispatch, push or deployment
was authorised or executed. Hosted CI and staging are prepared, not live verified.
