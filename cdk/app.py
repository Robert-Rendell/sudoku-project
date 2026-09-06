#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.sudoku_stack import SudokuStack

app = cdk.App()

SudokuStack(
    app,
    "SudokuGeneratorStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION", "eu-west-1"),
    ),
)

app.synth()
