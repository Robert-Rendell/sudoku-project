import os

from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
)
from constructs import Construct

DEFAULT_CALLBACK_URL = "https://robrendellwebsite.onrender.com/sudoku/add/callback"

# The lambda's own source lives at the repo root of sudoku-project (one level
# up from this cdk/ directory), alongside this CDK app, tests and generated
# artifacts that shouldn't be packaged into the deployed function.
LAMBDA_SOURCE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
LAMBDA_ASSET_EXCLUDES = [
    "cdk",
    "cdk.out",
    ".git",
    ".gitignore",
    "test_sudoku.py",
    "example-event.json",
    "robrendellwebsite-generate-sudoku.yaml",
    "__pycache__",
    "*.pyc",
    ".venv",
    "venv",
    ".pytest_cache",
]


class SudokuStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        security_key = self.node.try_get_context(
            "sudokuGenSecurityKey"
        ) or os.environ.get("SUDOKU_GEN_SECURITY_KEY")
        if not security_key:
            raise ValueError(
                "SUDOKU_GEN_SECURITY_KEY must be provided before deploying "
                "(set the SUDOKU_GEN_SECURITY_KEY env var, or pass "
                "-c sudokuGenSecurityKey=<value> to cdk deploy). This must "
                "match the value the website's SUDOKU_GEN_SECURITY_KEY env "
                "var checks against on the /sudoku/add/callback route."
            )

        callback_url = (
            self.node.try_get_context("sudokuGenCallback")
            or os.environ.get("SUDOKU_GEN_CALLBACK")
            or DEFAULT_CALLBACK_URL
        )

        # Holds the short-lived generation-request JSON files that trigger
        # the Lambda. Objects are tiny and transient, but retain the bucket
        # itself by default so a stack teardown can't silently delete it.
        requests_bucket = s3.Bucket(
            self,
            "GenerationRequestsBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN,
        )

        generate_fn = _lambda.Function(
            self,
            "GenerateSudokuFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(
                LAMBDA_SOURCE_DIR, exclude=LAMBDA_ASSET_EXCLUDES
            ),
            memory_size=128,
            timeout=Duration.seconds(30),
            environment={
                "SUDOKU_GEN_CALLBACK": callback_url,
                "SUDOKU_GEN_SECURITY_KEY": security_key,
            },
        )
        generate_fn.configure_async_invoke(
            retry_attempts=0,
            max_event_age=Duration.hours(6),
        )

        # Execution-role-based read access replaces the static ACCESS_KEY /
        # SECRET_KEY environment variables the hand-deployed function used.
        requests_bucket.grant_read(generate_fn)

        requests_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(generate_fn),
            s3.NotificationKeyFilter(suffix=".json"),
        )

        CfnOutput(
            self,
            "GenerationRequestsBucketName",
            value=requests_bucket.bucket_name,
            description=(
                "Set the website's SUDOKU_GEN_BUCKET_JSON env var to this value"
            ),
        )
        CfnOutput(
            self,
            "GenerateSudokuFunctionName",
            value=generate_fn.function_name,
        )
