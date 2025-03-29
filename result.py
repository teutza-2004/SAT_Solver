class TestResult:
    def __init__(self, time: float = 0.0, timeout: float = 0.0,
                 verdict: bool = False, ref_verdict: bool = False,
                 valid: bool = True):
        self.time: float = time
        self.timeout: float = timeout
        self.verdict: bool = verdict
        self.ref_verdict: bool = ref_verdict

        # This is more than (verdict == ref_verdict); when the answer is
        # correctly identified as SAT, this shows whether the model is correct.
        self.valid: bool = valid

        # Everything below are just cached values that can be recalculated from
        # the test results
        self.tle: bool = self.time > self.timeout
        self.correct: bool = self.verdict == self.ref_verdict and self.valid
        self.score = 2 * self.timeout if self.tle else self.time

    def __str__(self) -> str:
        if self.tle:
            return "TLE"
        elif self.correct:
            return f"OK ({self.time:.2f})"
        else:
            return "WRONG"


class LevelResult:
    def __init__(self) -> None:
        self.test_results: list[TestResult] = []

        # Everything below are just cached values that can be recalculated from
        # the test results
        self.valid: bool = True
        self.passed: bool = True

        self.tests_run: int = 0
        self.sat_run: int = 0
        self.unsat_run: int = 0

        self.solved: int = 0
        self.sat_solved: int = 0
        self.unsat_solved: int = 0

        self.tles: int = 0
        self.sat_tles: int = 0
        self.unsat_tles: int = 0

        self.time: float = 0.0
        self.sat_time: float = 0.0
        self.unsat_time: float = 0.0

        self.score: float = 0.0
        self.sat_score: float = 0.0
        self.unsat_score: float = 0.0

    def update(self, test_result: TestResult) -> None:
        self.test_results.append(test_result)
        self.tests_run += 1
        self.tles += test_result.tle
        self.score += test_result.score
        if test_result.tle:
            test_time = test_result.timeout
        else:
            test_time = test_result.time

        self.time += test_time

        if test_result.ref_verdict:
            self.sat_run += 1
            self.sat_tles += test_result.tle
            self.sat_score += test_result.score
            self.sat_time += test_time
            self.sat_solved += test_result.correct
        else:
            self.unsat_run += 1
            self.unsat_tles += test_result.tle
            self.unsat_score += test_result.score
            self.unsat_time += test_time
            self.unsat_solved += test_result.correct

        self.solved += test_result.correct

        # The validity of TLE tests is undefined
        if not test_result.tle and not test_result.correct:
            self.valid = False
            self.passed = False

    def batch_update(self, test_results: list[TestResult]) -> None:
        for test_result in test_results:
            self.update(test_result)


class FinalResult(LevelResult):
    def __init__(self):
        super().__init__()
        self.level_reached: int = 0

    def __str__(self) -> str:
        return f"{'OK' if self.valid else 'DISQUALIFIED'}\n" \
               f"Level reached: {self.level_reached}\n" \
               f"Tests run: {self.tests_run} (SAT: {self.sat_run}, UNSAT: {self.unsat_run})\n" \
               f"Tests solved: {self.solved} (SAT: {self.sat_solved}, UNSAT: {self.unsat_solved})\n" \
               f"Time: {self.time:.2f} (SAT: {self.sat_time:.2f}, UNSAT: {self.unsat_time:.2f})\n" \
               f"TLEs: {self.tles} (SAT: {self.sat_tles}, UNSAT: {self.unsat_tles})\n" \
               f"Score: {self.score:.2f} (SAT: {self.sat_score:.2f}, UNSAT: {self.unsat_score:.2f})"

    def toJSON(self) -> dict:
        return {
            "levels_passed": self.level_reached,
            "tests_run": self.tests_run,
            "sat_run": self.sat_run,
            "unsat_run": self.unsat_run,
            "solved": self.solved,
            "sat_solved": self.sat_solved,
            "unsat_solved": self.unsat_solved,
            "time": self.time,
            "sat_time": self.sat_time,
            "unsat_time": self.unsat_time,
            "tle": self.tles,
            "sat_tle": self.sat_tles,
            "unsat_tle": self.unsat_tles,
            "score": self.score,
            "sat_score": self.sat_score,
            "unsat_score": self.unsat_score,
        }
