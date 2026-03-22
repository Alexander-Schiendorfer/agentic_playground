"""Multiple choice quiz application."""

from dataclasses import dataclass, field


@dataclass
class Question:
    """Represents a single multiple choice question."""

    text: str
    choices: list[str]
    correct_index: int

    def __post_init__(self) -> None:
        if len(self.choices) < 2:
            raise ValueError("A question must have at least two choices.")
        if not (0 <= self.correct_index < len(self.choices)):
            raise ValueError("correct_index must be a valid index into choices.")

    @property
    def correct_answer(self) -> str:
        return self.choices[self.correct_index]

    def is_correct(self, answer_index: int) -> bool:
        return answer_index == self.correct_index

    def display(self, number: int) -> str:
        """Return a formatted string representation of the question."""
        lines = [f"Q{number}. {self.text}"]
        for i, choice in enumerate(self.choices):
            label = chr(ord("A") + i)
            lines.append(f"  {label}) {choice}")
        return "\n".join(lines)


@dataclass
class Quiz:
    """Manages a sequence of multiple choice questions and tracks the score."""

    questions: list[Question] = field(default_factory=list)
    _score: int = field(default=0, init=False, repr=False)
    _answers: list[int | None] = field(default_factory=list, init=False, repr=False)

    def add_question(self, question: Question) -> None:
        self.questions.append(question)

    def submit_answer(self, question_index: int, answer_index: int) -> bool:
        """Record the answer for a question and return whether it is correct.

        Each question may only be answered once; subsequent calls for the same
        question_index are ignored and return False.
        """
        # Extend answers list if needed
        while len(self._answers) <= question_index:
            self._answers.append(None)

        # Do not allow re-submission
        if self._answers[question_index] is not None:
            return False

        question = self.questions[question_index]
        correct = question.is_correct(answer_index)
        self._answers[question_index] = answer_index
        if correct:
            self._score += 1
        return correct

    @property
    def score(self) -> int:
        return self._score

    @property
    def total(self) -> int:
        return len(self.questions)

    def result_summary(self) -> str:
        percentage = (self._score / self.total * 100) if self.total > 0 else 0
        return (
            f"Quiz complete! You scored {self._score}/{self.total} "
            f"({percentage:.0f}%)."
        )


SAMPLE_QUESTIONS: list[Question] = [
    Question(
        text="What is the capital of France?",
        choices=["Berlin", "Madrid", "Paris", "Rome"],
        correct_index=2,
    ),
    Question(
        text="Which planet is closest to the Sun?",
        choices=["Venus", "Mercury", "Earth", "Mars"],
        correct_index=1,
    ),
    Question(
        text="What is 12 × 12?",
        choices=["124", "144", "132", "148"],
        correct_index=1,
    ),
    Question(
        text="Who wrote 'Romeo and Juliet'?",
        choices=["Charles Dickens", "Mark Twain", "Jane Austen", "William Shakespeare"],
        correct_index=3,
    ),
    Question(
        text="What is the chemical symbol for water?",
        choices=["O2", "H2O", "CO2", "NaCl"],
        correct_index=1,
    ),
]


def parse_answer(raw: str, num_choices: int) -> int | None:
    """Parse a user's answer (letter or 1-based number) into a 0-based index.

    Returns None if the input is invalid.
    """
    raw = raw.strip().upper()
    if not raw:
        return None
    # Accept letter (A, B, C, ...)
    if len(raw) == 1 and raw.isalpha():
        index = ord(raw) - ord("A")
        if 0 <= index < num_choices:
            return index
    # Accept 1-based number (1, 2, 3, ...)
    if raw.isdigit():
        index = int(raw) - 1
        if 0 <= index < num_choices:
            return index
    return None


def run_quiz(quiz: Quiz) -> None:
    """Run an interactive quiz on the command line."""
    print("=" * 50)
    print("       Welcome to the Multiple Choice Quiz!")
    print("=" * 50)
    word = "question" if quiz.total == 1 else "questions"
    print(f"This quiz has {quiz.total} {word}. Good luck!\n")

    for i, question in enumerate(quiz.questions):
        print(question.display(i + 1))
        print()

        answer_index: int | None = None
        while answer_index is None:
            raw = input("Your answer (e.g. A, B, C ...): ")
            answer_index = parse_answer(raw, len(question.choices))
            if answer_index is None:
                print(
                    f"  Invalid input. Please enter a letter between A and "
                    f"{chr(ord('A') + len(question.choices) - 1)}."
                )

        correct = quiz.submit_answer(i, answer_index)
        if correct:
            print("  ✓ Correct!\n")
        else:
            correct_label = chr(ord("A") + question.correct_index)
            print(
                f"  ✗ Wrong. The correct answer was "
                f"{correct_label}) {question.correct_answer}\n"
            )

    print("=" * 50)
    print(quiz.result_summary())
    print("=" * 50)


def main() -> None:
    quiz = Quiz(questions=list(SAMPLE_QUESTIONS))
    run_quiz(quiz)


if __name__ == "__main__":
    main()
