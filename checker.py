#!/usr/bin/env python3
import argparse
import json
import logging
import os
import subprocess
import sys
import time

import requests

import helpers
from result import FinalResult, LevelResult, TestResult
import validate


logger = logging.getLogger(__name__)

TESTDIR = "tests/"
INFOBASENAME = "info.json"

MAX_TESTNAME_WIDTH = 60

# For the assignment
MAX_SCORE = 90
POINTS_PER_TEST = 3

LEADERBOARD_URL = ""
LEADERBOARD_AUTH_TOKEN = ""


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[bytes]:
    cmdstr = " ".join(cmd)
    logger.debug(f"Running command:\n\t{cmdstr}")
    try:
        proc = subprocess.run(cmd, capture_output=True)
        if proc.returncode != 0 and proc.returncode != 137:
            logger.error(f"Command:\n    {cmdstr}\nfailed with code "
                         f"{proc.returncode}!")
            sys.exit(1)

        logger.debug(f"STDOUT:\n{proc.stdout.decode('utf-8')}")
        logger.debug(f"STDERR:\n{proc.stderr.decode('utf-8')}")
    except Exception as e:
        estr = helpers.format_exception(e)
        logger.error(f"Error while running:\n{estr}")
        sys.exit(1)

    return proc


def run_solver(inpath: str, outpath: str, timeout: float) -> float:
    cmd = ["/usr/bin/time", "--format=\"%U,%S\"",
           "timeout", "--signal=KILL", f"{timeout:.3f}",
           "make", "run", f"INPUT={inpath}", f"OUTPUT={outpath}"]

    proc = run_cmd(cmd)

    if proc.returncode == 137:  # timeout sent KILL
        logger.info(f"Time limit ({timeout} s) exceeded for '{inpath}'!")
        time = float("inf")
    else:
        time_line = proc.stderr.decode("utf-8").splitlines()[-1]
        time = sum(map(float, time_line.strip("\"").split(",")))

    return time


def get_level_info(testsubdir: str) -> dict:
    testsubdirpath = os.path.join(TESTDIR, "in", testsubdir)
    infopath = os.path.join(testsubdirpath, INFOBASENAME)
    try:
        with open(infopath) as fin:
            info = json.load(fin)
    except FileNotFoundError:
        logger.error(f"Test directory {testsubdir} missing info file!")
        sys.exit(1)

    if ("timeout" not in info) or ("tests" not in info):
        logger.error(f"Bad format for {infopath}!")
        sys.exit(1)

    return info


def evaluate_level(testsubdir: str, competition: bool) -> LevelResult:
    info = get_level_info(testsubdir)
    testsubdirpath = os.path.join(TESTDIR, "in", testsubdir)
    level_result = LevelResult()
    timeout = info["timeout"]
    for test, ref_verdict in info["tests"].items():
        stem = os.path.splitext(test)[0]
        answerfile = f"{stem}.answer"
        out_subdir = os.path.join(TESTDIR, "out", testsubdir)
        os.makedirs(out_subdir, exist_ok=True)
        inpath = os.path.join(testsubdirpath, test)
        outpath = os.path.join(out_subdir, answerfile)

        time = run_solver(inpath, outpath, timeout)
        if time > timeout:
            verdict, valid = False, False  # irrelevant, actually
        else:
            verdict, valid = validate.validate(inpath, outpath, ref_verdict)

        result = TestResult(time, timeout, verdict, ref_verdict, valid)
        level_result.update(result)
        if not competition:
            prefix = f"Running {test}"
            ndots = MAX_TESTNAME_WIDTH - len(prefix)
            dots = "." * ndots
            print(f"{prefix}  {dots}  {result}")
        elif not level_result.passed:
            return level_result

    if level_result.tles > info.get("timeouts_allowed", 0):
        level_result.passed = False

    return level_result


def check(competition) -> FinalResult:
    testspath = os.path.join(TESTDIR, "in")
    infopath = os.path.join(testspath, INFOBASENAME)
    try:
        with open(infopath) as fin:
            info = json.load(fin)
    except FileNotFoundError:
        logger.error(f"Missing info file ({infopath}) in tests directory!")
        sys.exit(1)

    final_result = FinalResult()
    if competition:
        levels = info["levels"]
    else:
        levels = [info["levels"][0]]

    for level in levels:
        level_result = evaluate_level(level, competition)
        final_result.batch_update(level_result.test_results)
        final_result.level_reached += 1
        if competition and not level_result.valid:
            logger.info("Model is disqualified for giving the wrong answer!")
            return final_result

        if competition and not level_result.passed:
            logger.info(f"Too many timeouts ({level_result.tles})! Evaluation "
                        "stopped!")
            return final_result

    return final_result


def run_all(competition: bool) -> FinalResult:
    run_cmd(["make", "build"])
    final_result = check(competition)
    return final_result


def submit_result(final_result: FinalResult) -> None:
    submit_url = LEADERBOARD_URL + "/submit"
    json_request = final_result.toJSON()
    json_request["auth_token"] = LEADERBOARD_AUTH_TOKEN

    # Hackish, but we don't seem to have a way to retrieve the LDAP ID
    if "CI_COMMIT_REF_NAME" not in os.environ:
        logger.error("'CI_COMMIT_REF_NAME' missing from env! (not running on "
                     "vmchecker?)")
        sys.exit(1)

    branch_name = os.environ["CI_COMMIT_REF_NAME"]
    student_id = branch_name[:branch_name.find("-2024-")]
    json_request["user_id"] = student_id
    logger.debug(f"Posting request:\n{json_request}")

    attempts = 3
    while attempts:
        try:
            pasresponse = requests.post(submit_url, json=json_request,
                                        timeout=10)
            logger.debug(f"Got response:\n{pasresponse}")
            return
        except requests.exceptions.ReadTimeout:
            attempts -= 1
            logger.error("Timeout while submitting result, retrying...")
            time.sleep(10)

    logger.error("Failed to submit result after 3 attempts!")


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--competition", action="store_true",
                           help="Evaluate according to competition rules")
    argparser.add_argument("--submit", action="store_true",
                           help="Submit the result to the server")
    argparser.add_argument("--logdir", type=str, default="logs",
                           help="Name of the log directory (default: "
                                "%(default)s)")
    argparser.add_argument("--loglevel", type=str, default="WARN",
                           help="Lowest log level for which to record "
                                "messages (default: %(default)s)")
    argparser.add_argument("--logquiet", action="store_true",
                           help="Do not print logs to stderr")

    args = argparser.parse_args()
    global logger
    logger = helpers.setup_logging(args.logdir, args.logquiet, args.loglevel)

    if args.submit:
        global LEADERBOARD_URL, LEADERBOARD_AUTH_TOKEN
        if "LEADERBOARD_URL" not in os.environ:
            logger.error("No leaderboard URL provided!")
            sys.exit(1)

        LEADERBOARD_URL = os.environ["LEADERBOARD_URL"]
        if "LEADERBOARD_AUTH_TOKEN" not in os.environ:
            logger.error("No leaderboard auth token provided!")
            sys.exit(1)

        LEADERBOARD_AUTH_TOKEN = os.environ["LEADERBOARD_AUTH_TOKEN"]

        # Prevent intentional or accidental leakage
        del os.environ["LEADERBOARD_AUTH_TOKEN"]

    final_result = run_all(args.competition)
    if args.competition:
        logger.info("Result:")
        print(final_result)

        if args.submit:
            submit_result(final_result)
    else:
        score = 0
        for result in final_result.test_results:
            if result.correct:
                score += POINTS_PER_TEST

        print(f"\nTotal: {score}/{MAX_SCORE}")


if __name__ == "__main__":
    main()
