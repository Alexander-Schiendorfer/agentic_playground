"""Unit tests for the multiple choice quiz."""

import pytest

from quiz import Question, Quiz, parse_answer


# ---------------------------------------------------------------------------
# Question tests
# ---------------------------------------------------------------------------


class TestQuestion:
    def test_correct_answer_property(self) -> None:
        q = Question(text="Pick one", choices=["A", "B", "C"], correct_index=1)
        assert q.correct_answer == "B"

    def test_is_correct_true(self) -> None:
        q = Question(text="Pick one", choices=["A", "B", "C"], correct_index=2)
        assert q.is_correct(2) is True

    def test_is_correct_false(self) -> None:
        q = Question(text="Pick one", choices=["A", "B", "C"], correct_index=2)
        assert q.is_correct(0) is False

    def test_display_contains_question_text(self) -> None:
        q = Question(
            text="What is 2+2?", choices=["3", "4", "5", "6"], correct_index=1
        )
        display = q.display(1)
        assert "What is 2+2?" in display
        assert "A)" in display
        assert "B)" in display

    def test_requires_at_least_two_choices(self) -> None:
        with pytest.raises(ValueError, match="at least two choices"):
            Question(text="Only one choice", choices=["Only"], correct_index=0)

    def test_correct_index_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="valid index"):
            Question(text="Test", choices=["X", "Y"], correct_index=5)


# ---------------------------------------------------------------------------
# Quiz tests
# ---------------------------------------------------------------------------


class TestQuiz:
    def _make_quiz(self) -> Quiz:
        return Quiz(
            questions=[
                Question(text="Q1", choices=["Yes", "No"], correct_index=0),
                Question(text="Q2", choices=["True", "False"], correct_index=1),
            ]
        )

    def test_initial_score_is_zero(self) -> None:
        quiz = self._make_quiz()
        assert quiz.score == 0

    def test_total_equals_question_count(self) -> None:
        quiz = self._make_quiz()
        assert quiz.total == 2

    def test_correct_answer_increments_score(self) -> None:
        quiz = self._make_quiz()
        quiz.submit_answer(0, 0)  # correct for Q1
        assert quiz.score == 1

    def test_wrong_answer_does_not_increment_score(self) -> None:
        quiz = self._make_quiz()
        quiz.submit_answer(0, 1)  # wrong for Q1
        assert quiz.score == 0

    def test_submit_answer_returns_correct_flag(self) -> None:
        quiz = self._make_quiz()
        assert quiz.submit_answer(0, 0) is True
        assert quiz.submit_answer(1, 0) is False

    def test_result_summary_perfect_score(self) -> None:
        quiz = self._make_quiz()
        quiz.submit_answer(0, 0)
        quiz.submit_answer(1, 1)
        summary = quiz.result_summary()
        assert "2/2" in summary
        assert "100%" in summary

    def test_result_summary_zero_score(self) -> None:
        quiz = self._make_quiz()
        quiz.submit_answer(0, 1)
        quiz.submit_answer(1, 0)
        summary = quiz.result_summary()
        assert "0/2" in summary
        assert "0%" in summary

    def test_duplicate_submission_is_ignored(self) -> None:
        quiz = self._make_quiz()
        quiz.submit_answer(0, 0)  # correct
        result = quiz.submit_answer(0, 0)  # re-submit same correct answer
        assert result is False
        assert quiz.score == 1  # score must not increase again


        quiz = Quiz()
        assert quiz.total == 0
        quiz.add_question(Question(text="Q", choices=["Yes", "No"], correct_index=0))
        assert quiz.total == 1

    def test_empty_quiz_result_summary(self) -> None:
        quiz = Quiz()
        summary = quiz.result_summary()
        assert "0/0" in summary


# ---------------------------------------------------------------------------
# parse_answer tests
# ---------------------------------------------------------------------------


class TestParseAnswer:
    def test_letter_a_returns_zero(self) -> None:
        assert parse_answer("A", 4) == 0

    def test_lowercase_letter(self) -> None:
        assert parse_answer("b", 4) == 1

    def test_letter_out_of_range(self) -> None:
        assert parse_answer("E", 4) is None

    def test_number_one_returns_zero(self) -> None:
        assert parse_answer("1", 4) == 0

    def test_number_two_returns_one(self) -> None:
        assert parse_answer("2", 4) == 1

    def test_number_zero_is_invalid(self) -> None:
        assert parse_answer("0", 4) is None

    def test_number_out_of_range(self) -> None:
        assert parse_answer("5", 4) is None

    def test_empty_string_is_invalid(self) -> None:
        assert parse_answer("", 4) is None

    def test_whitespace_stripped(self) -> None:
        assert parse_answer("  C  ", 4) == 2

    def test_invalid_text_is_none(self) -> None:
        assert parse_answer("yes", 4) is None
