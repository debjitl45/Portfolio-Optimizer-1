from flask import Flask, request, render_template, url_for, flash, redirect, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from user import User, create_dict, creates_dict


from calculate import Calculate_portfolio

from database import get_user, save_user_info, save_portfolio_info, get_portfolio

# Application Setup
app = Flask(__name__)
app.secret_key = b'hdhcbchhh'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

ticker = []
min_weigh = []
max_weigh = []

# Home Page
@app.route('/')   
def home():
    return render_template('home.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html', title='About')

# To handle portfolio calculations
@app.route('/calculate', methods=['POST','GET'])
def calculate():
    if request.method == "POST":
        tickers = request.form["tickers"]
        maxll, minll, max_weights, min_weights = Calculate_portfolio(tickers)
        min_weigh.append(min_weights)
        max_weigh.append(max_weights)
        ticker.append(tickers)
        
        flash("Portfolio generated successfully!", "info")
        flash( "Your optimal portfolio distribution for minimum risk is: " + str(maxll), "info")
        flash( "Your optimal portfolio distribution for maximum return is: " + str(minll), "info")
        
        data = create_dict(tickers, max_weights)
        labels = data.keys()
        values = data.values()
        print(list(labels))
        print(list(values))
        val=list(values)
        val = [x * 100 for x in val]
        return render_template('pie.html', labels = list(labels), values = val)
        
       # return redirect(url_for('home'))
             
        


# To handle user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash ('You are already Logged in!')
        return redirect(request.referrer)
    else:
        message = ""
        if request.method == 'POST':
            username = request.form['username']
            password_input = request.form['password']
            user = get_user(username)
            if user and user.check_password(password_input):
                login_user(user)
                return redirect(url_for('home'))
            else:
                message = 'Invalid Credentials. Failed to login!'
    return render_template('login.html', message=message)

# To handle user signup
@app.route('/signup', methods=['POST','GET'])
def signup():
    message = ""
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password_input = request.form['password']
        if(get_user(username)!=None):
            message = 'Username already exists! Please try a different username.'
            return render_template('signup.html', message=message) 
        else:
            save_user_info(username, email, password_input)
            return redirect(url_for('login'))
    else:
        return render_template('signup.html')

# To handle user logout
@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    else:
        flash("You're not Logged in!")
    return redirect(url_for('home'))

# # To handle 'save portfolio' operation
@app.route('/save', methods=['POST','GET'])
@login_required
def save_portfolio():
    if(len(max_weigh)!=0):
        weights = max_weigh.pop()
        tickers = ticker.pop()
        username = current_user.get_id()
        tickers = tickers.split()
        portfolio_dict = creates_dict(tickers, weights)
        save_portfolio_info(username, portfolio_dict)
        flash('Portfolio saved Successfully!')
    else:
        flash('Please create a portfolio first!')
    return redirect(url_for('home'))

# To view 'My Account'
@app.route('/account', methods=['POST','GET'])
@login_required
def account():
    username = current_user.get_id()
    stocks = get_portfolio(username)
    return render_template('account.html', data = stocks)


@login_manager.user_loader
def load_user(username):
    return get_user(username)


# Running in debug mode
if __name__=='__main__':
    app.run(debug=True,host="0.0.0.0",port = 5000) 