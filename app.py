#!/usr/bin/env python3
import os

import aws_cdk as cdk

from retro_pie_stats.retro_pie_stats_stack import RetroPieStatsStack

# Read certificate ARN from file
with open("certificate_arn.txt") as f:
    certificate_arn = f.read().strip()

app = cdk.App()
RetroPieStatsStack(app, "RetroPieStatsStack", certificate_arn=certificate_arn)

app.synth()
