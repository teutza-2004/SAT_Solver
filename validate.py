#!/usr/bin/env python3
import argparse
import logging
import sys

import helpers
import dimacs_parser
from literal import Literal
from clause import Clause
from formula import Formula
from model import Model


logger = logging.getLogger(__name__)


def evaluate_literal(lit: Literal, model: Model) -> bool:
    return model[lit.var.idx] == lit.pos


def evaluate_clause(cl: Clause, model: Model) -> bool:
    return any(evaluate_literal(lit, model) for lit in cl.literals)


def evaluate_formula(phi: Formula, model: Model) -> bool:
    return all(evaluate_clause(cl, model) for cl in phi.clauses)


def validate_model(phi: Formula, model: Model) -> bool:
    try:
        return evaluate_formula(phi, model)
    except KeyError as e:
        logger.error(f"Model provides no value for variable: {e.args[0]}")
        return False


def validate(formulapath: str, anspath: str,
             ref_verdict: bool) -> tuple[bool, bool]:
    """Return (given_verdict, correct)"""
    formula_parser = dimacs_parser.FormulaParser(logger)
    formula_parser.set_path(formulapath)
    formula = formula_parser.parse()
    if formula is None:
        logger.error("Failed to parse the formula file!")
        sys.exit(1)

    ans_parser = dimacs_parser.AnswerParser(logger)
    ans_parser.set_path(anspath)
    answer = ans_parser.parse()
    if answer is None:
        logger.error("Failed to parse the answer file!")
        sys.exit(1)

    verdict, model = answer
    if verdict != ref_verdict:
        logger.info("Wrong verdict given!")
        return verdict, False

    if verdict:
        if model is None:
            logger.info("No model provided!")
            sys.exit(1)

        valid = validate_model(formula, model)
        return verdict, valid
    else:
        return verdict, True


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('formula-file', type=str)
    argparser.add_argument('answer-file', type=str)
    argparser.add_argument('reference-answer', type=bool)
    argparser.add_argument("--logdir", type=str, default="logs",
                           help="Name of the log directory (default: "
                                "%(default)s)")
    argparser.add_argument("--loglevel", type=str, default="INFO",
                           help="Lowest log level for which to record "
                                "messages (default: %(default)s)")
    argparser.add_argument("--logquiet", action="store_true",
                           help="Do not print logs to stderr")

    args = argparser.parse_args()
    global logger
    logger = helpers.setup_logging(args.logdir, args.logquiet, args.loglevel)

    valid = validate(args.formula_file, args.answer_file,
                     args.reference_answer)
    if valid:
        print("Answer is correct!")
    else:
        print("Answer is incorrect!")


if __name__ == "__main__":
    main()
