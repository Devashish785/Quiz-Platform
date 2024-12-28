# quiz_app.py
from flask import Flask, render_template, request, session, redirect, url_for
import json
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

class Question:
    def __init__(self, question_text, options, correct_answers):
        self.question_text = question_text
        self.options = options
        self.correct_answers = correct_answers
        self.is_multiple = len(correct_answers) > 1

    def calculate_score(self, user_answers):
        if not user_answers:
            return 0
        
        if self.is_multiple:
            if set(user_answers) == set(self.correct_answers):
                return 2
            return -1
        else:
            if user_answers[0] == self.correct_answers[0]:
                return 1
            return -0.5
            
    def get_max_score(self):
        return 2 if self.is_multiple else 1

class Quiz:
    def __init__(self):
        self.questions = []
        self.load_questions()

    def load_questions(self):
        # Sample questions - you can expand this
        sample_questions = [
            
            {
                "question": "Which of these are prime numbers?",
                "options": ["2", "4", "7", "11"],
                "correct_answers": [0, 2, 3]  # Multiple correct answers
            },
            {
                "question" : "What is the value of x in the equation 3x + 7 = 22?",
                "options" : ["3", "5", "6", "4"],
                "correct_answers" : [1]
            },
            {
                "question" : "Identify the multiples of 4 from the following set of numbers: {8, 10, 12, 14, 16}.",
                "options" : ["8", "10", "12", "16"],
                "correct_answers" : [0, 2, 3]
            },
            {
                "question" : "What is the slope of the line that passes through the points (2,3) and (5,11)?",
                "options" : ["2", "3", "4", "5"],
                "correct_answers" : [1]
            },
            {
                "question" : "What is the sum of the interior angles of a hexagon?",
                "options" : ["540", "720", "900", "1080"],
                "correct_answers" : [1]
            },
            {
                "question" : "If the perimeter of a rectangle is 50 cm and the length is 15 cm, what is the width?",
                "options" : ["10", "12.5", "20", "10.5"],
                "correct_answers" : [0]
            },
            {
                "question" : "What is the factorial of 0 and 5 respectively?",
                "options" : ["0, 210", "1, 210", "1, 120", "0, 120"],
                "correct_answers" : [2]
            }
        ]
        
        for q in sample_questions:
            self.questions.append(
                Question(q["question"], q["options"], q["correct_answers"])
            )

    def get_total_questions(self):
        return len(self.questions)

    def calculate_total_score(self, user_answers):
        total_score = 0
        for q_idx, answers in user_answers.items():
            score = self.questions[int(q_idx)].calculate_score(answers)
            total_score += score
        return total_score
    
    def get_max_possible_score(self):
        return sum(question.get_max_score() for question in self.questions)
    
    def calculate_percentage(self, user_answers):
        total_score = self.calculate_total_score(user_answers)
        max_possible = self.get_max_possible_score()
        
        # Handle negative scores gracefully
        if total_score < 0:
            return 0
        
        # Calculate percentage, ensuring we don't divide by zero
        if max_possible > 0:
            percentage = (total_score / max_possible) * 100
            return max(0, min(100, percentage))  # Clamp between 0 and 100
        return 0

app = Flask(__name__)
app.secret_key = 'your_secret_key'
quiz = Quiz()

@app.route('/')
def home():
    session.clear()
    return render_template('index.html')

@app.route('/start_quiz')
def start_quiz():
    session['current_question'] = 0
    session['user_answers'] = {}
    return redirect(url_for('question'))

@app.route('/question', methods=['GET', 'POST'])
def question():
    if 'current_question' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Store answers
        selected = request.form.getlist('answer')
        q_idx = session['current_question']
        session['user_answers'][str(q_idx)] = [int(x) for x in selected]
        
        # Move to next question
        session['current_question'] += 1
        
        if session['current_question'] >= quiz.get_total_questions():
            return redirect(url_for('results'))
            
    return render_template(
        'question.html',
        question=quiz.questions[session['current_question']],
        question_number=session['current_question'] + 1
    )

@app.route('/results')
def results():
    if 'user_answers' not in session:
        return redirect(url_for('home'))
        
    total_score = quiz.calculate_total_score(session['user_answers'])
    percentage = quiz.calculate_percentage(session['user_answers'])
    max_possible = quiz.get_max_possible_score()
    
    return render_template(
        'results.html',
        score=total_score,
        max_possible=max_possible,
        percentage=percentage,
        answers=session['user_answers']
    )

if __name__ == '__main__':
    app.run(debug=True)