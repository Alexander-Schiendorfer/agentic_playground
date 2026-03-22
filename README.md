# agentic_playground

## Multiple Choice Quiz

A simple command-line multiple choice quiz implemented in Python.

### Running the quiz

```bash
python quiz.py
```

Answer each question by typing the corresponding letter (`A`, `B`, `C`, …) or the
1-based number (`1`, `2`, `3`, …) and pressing **Enter**.  
After every question you receive instant feedback, and a final score is shown at
the end.

### Running the tests

```bash
python -m pytest test_quiz.py -v
```

### Extending the quiz

Add your own questions by editing the `SAMPLE_QUESTIONS` list in `quiz.py`, or
create a `Quiz` object programmatically:

```python
from quiz import Question, Quiz, run_quiz

quiz = Quiz(questions=[
    Question(
        text="What is the speed of light (approx)?",
        choices=["300 000 km/s", "150 000 km/s", "450 000 km/s"],
        correct_index=0,
    ),
])
run_quiz(quiz)
```