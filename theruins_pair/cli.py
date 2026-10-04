from implementation import analyze_scores


print("Student Score Analyzer")

user_input = input("Enter scores separated by spaces: ")

try:
    scores = [float(score) for score in user_input.split()]
    
    if len(scores) == 0:
        print("Invalid input")

    elif any(score < 0 or score > 100 for score in scores):
        print("Invalid input: scores must be between 0 and 100")

    else:
        result = analyze_scores(scores)

        print("Number of scores:", result["count"])
        print(f"Average score: {result['average']:.2f}")
        print(f"Highest score: {result['highest']:.2f}")
        print(f"Lowest score: {result['lowest']:.2f}")

except ValueError:
    print("Invalid input: please enter numbers only")