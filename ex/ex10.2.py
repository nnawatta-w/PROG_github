def calculate_final_score(quiz_score: float, exam_score: float, bonus: float):
    mean_score = (quiz_score + exam_score) / 2
    return mean_score + bonus


def print_course_result(quiz_score: float, exam_score: float, bonus: float):
    final_score = calculate_final_score(quiz_score, exam_score, bonus)

    print(f"Final score: {final_score:.2f}")

    if final_score >= 50.0:
        print("Result: Pass")
    else:
        print("Result: Fail")


print_course_result(78.0, 86.0, 4.0)