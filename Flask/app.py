from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/form/')
def form_page():
    return render_template("form.html")


@app.route('/foobar')
def foobar():
    return 'Hi there, foobar!'


if __name__ == '__main__':
    app.run(debug=True)