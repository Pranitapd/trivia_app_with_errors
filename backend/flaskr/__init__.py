import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import func

from models import setup_db, Question, Category
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions

QUESTIONS_PER_PAGE = 10

# app.config['TRAP_HTTP_EXCEPTIONS']=True
# app.register_error_handler(Exception, defaultHandler)

def paginate(request,selection):
    pages = request.args.get('page',1,type=int)
    starts = (pages - 1) * QUESTIONS_PER_PAGE
    end = starts + QUESTIONS_PER_PAGE
    questions = [ que.format() for que in selection]
    current_questions = questions[starts:end]
    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  setup_db(app)
  cors = CORS(app, resources={r"*/api/*": {"origins": "*"}})
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin','*')
    response.headers.add('Access-Control-Allow-Headers', 'Origin,Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    return jsonify({
      'success':True,
      'categories':get_category_list(),
      'total_categories':len(Category.query.all())
    })
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  def get_category_list():
    categories = {}
    for category in Category.query.all():
        categories[category.id] = category.type
    return categories

  @app.route('/questions')
  def get_questions():
    all_questions = Question.query.all()
    current_questions = paginate(request,all_questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success'  : True,
      'questions':current_questions,
      'total_questions':len(all_questions),
      'categories':get_category_list(),
      'current_category':None
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
  
    que = Question.query.filter(Question.id == question_id).one_or_none()
    if que:
      que.delete()
    
      all_questions = Question.query.order_by(Question.id).all()
      current_questions = paginate(request,all_questions)

      return jsonify({
        'success'  : True,
        'questions':current_questions,
        'total_questions':len(Question.query.all()),
        'categories':get_category_list(),
        'current_category':None
        })

    abort(404)#,description='not found')
    

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST']) 
  def add_question():
    try:
      head = request.get_json()
      new_question = head['question']
      new_answer = head['answer']
      new_category = head['category']
      new_difficulty = head['difficulty']

      # new_question = head.get('question')
      # new_answer = head.get('answer')
      # new_category = head.get('category')
      # new_difficulty = head.get('difficulty')
      if ((new_question == '') or (new_answer == '') or (new_difficulty == '') or (new_category == '')):
        abort(422)

    
      que = Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
      que.insert()

      # all_questions = Question.query.order_by(Question.id).all()
      # current_questions = paginate(request,all_questions)

      return jsonify({
        'success':True,
        # 'created':que.id,
        # 'questions':current_questions,
        # 'total_questions':len(Question.query.all())
      })
    except:
      abort(405)

  # '''
  # @TODO: 
  # Create a POST endpoint to get questions based on a search term. 
  # It should return any questions for whom the search term 
  # is a substring of the question. 

  # TEST: Search by any phrase. The questions list will update to include 
  # only question that include that string within their question. 
  # Try using the word "title" to start. 
  # '''
  @app.route('/questions/search',methods=['POST','GET'])
  def search_questions():
    try:
      head = request.get_json()
      search_term = head['searchTerm']
      searched_question = Question.query.filter(Question.question.ilike("%{}%".format(search_term))).all()

      questions = paginate(request,searched_question)

      return jsonify({
        'success':True,
        'questions':questions,
        'total_questions':len(Question.query.all()),
        'current_category': None
      })
    except:
      abort(404)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    try: 
      selected_cat_que = Question.query.filter(Question.category == str(category_id))
      current_questions = paginate(request,selected_cat_que)
      current_category = Category.query.get(category_id)
      return jsonify({
        'success':True,
        'questions':current_questions,
        'total_questions':len(Question.query.all()),
        'current_category': current_category.type
      })
    except:
      abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST','GET'])
  def get_random_questions():
    head = request.get_json()
    previous_questions = head['previous_questions']
    quiz_category = head['quiz_category']['id']
    
    all_questions = Question.query.filter(Question.category == quiz_category).all()
  
    all_question_ids=[]
    visited=[]
    for a in all_questions:
      all_question_ids.append(a.id)

    if previous_questions is None:
      # random_question = Question.query.filter(Question.category == quiz_category['id']).order_by(func.random()).limit(1)
      random_question_id = random.choice(all_question_ids)
      return jsonify({
        'success':True,
        'question':(Question.query.get(random_question_id)).format()
      })
    else:
      while(1):
        random_id = random.choice(all_question_ids)
        if (random_id in previous_questions) and (random_id not in visited):
          visited.append(random_id)
          continue
        elif random_id not in previous_questions:
          return jsonify({
            'success':True,
            'question':(Question.query.get(random_id)).format()
          })
        elif len(visited) == len(previous_questions):
          return jsonify({
            'success':True,
            'question':False
          })
              
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  # @app.errorhandler(Exception)
  # def handle_error(e):
  #   code = 500
  #   if isinstance(e, HTTPException):
  #       code = e.code
  #   return jsonify(error=str(e)), code

    # for ex in default_exceptions:
    #   app.register_error_handler(ex, handle_error)
    
  # @app.errorhandler(Exception)
  # def handle_error(e):
  #   code = 500
  #   if isinstance(e,HTTPException):
  #     if e.code == 400:
  #       code = e.code
  #       return jsonify({
  #         'success':False,
  #         'error':404,
  #         'message':'not found'
  #       })

  @app.errorhandler(404)
  def not_found(error):
    print('error is'+ str(error))
    print('I am in errorhandler')
    return jsonify({
      'success':False,
      'error':404,
      "message": 'not found'
    }),404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success':False,
      'error':422,
      'message':'unprocessable'
    }),422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success':False,
      'error':400,
      'message':'bad request'
    }),400
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success':False,
      'error':405,
      'message':'methon not allowed'
    }),405
  return app

    