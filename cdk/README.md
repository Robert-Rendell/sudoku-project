# Sudoku generator — CDK

Deploys the sudoku-generation pipeline:

```
S3 bucket (generation-request JSON) --ObjectCreated:*.json--> Lambda --HTTP POST--> website callback
```

## First-time setup

```bash
cd sudoku-project/cdk
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

CDK is already bootstrapped in this account/region (`CDKToolkit` stack in
eu-west-1), so `cdk bootstrap` shouldn't be needed. If deploying to a new
account/region, run `cdk bootstrap` first.

## Deploy

The security key must match the website's `SUDOKU_GEN_SECURITY_KEY` (the
callback handler at `/sudoku/add/callback` rejects mismatches with a 401):

```bash
export SUDOKU_GEN_SECURITY_KEY=<value used by the website>
cdk deploy
```

Optionally override the callback URL (defaults to
`https://robrendellwebsite.onrender.com/sudoku/add/callback`):

```bash
export SUDOKU_GEN_CALLBACK=https://example.com/sudoku/add/callback
```

`cdk deploy` prints the generated bucket name as an output
(`GenerationRequestsBucketName`). Point the website's
`SUDOKU_GEN_BUCKET_JSON` env var (locally in `env.development`, and in the
Render dashboard for production) at that bucket name.

## Cutting over from the old hand-deployed resources

The Lambda and bucket previously existed in AWS as manually-created
resources (not CloudFormation-managed) named `robrendellwebsite-generate-sudoku`
and `robrendellwebsite-generate-sudoku-json`, and the Lambda's env vars held a
static IAM access key (`ACCESS_KEY`/`SECRET_KEY`) used only so boto3 could
read the triggering S3 object. This stack replaces that with role-based S3
access, so once you've:

1. Deployed this stack.
2. Updated `SUDOKU_GEN_BUCKET_JSON` everywhere (local env + Render) to the
   new bucket name from the stack output.
3. Verified generation end-to-end (upload a request JSON, confirm a callback
   POST arrives and the puzzle shows up on the site).

...you can delete the old `robrendellwebsite-generate-sudoku` Lambda and
`robrendellwebsite-generate-sudoku-json` bucket, and **deactivate the leaked
IAM access key** (it was visible in plaintext in the old Lambda's
configuration).

## Useful commands

* `cdk diff` — compare deployed stack with current state
* `cdk synth` — emit the synthesized CloudFormation template
* `cdk destroy` — tear down the stack (the bucket has `RemovalPolicy.RETAIN`,
  so it survives a destroy and must be deleted manually if truly unwanted)
