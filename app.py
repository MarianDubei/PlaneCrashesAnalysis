from flask import Flask, render_template, request
from module.accidentdata import AccidentData

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    criteria_category = request.form.get('button')
    criteria_obj = request.form.get('criteria')
    button_str = '<a href="/"><button type="button" class="btn btn-primary btn-lg">Return to main page</button></a>'
    try:
        accidents = AccidentData(criteria_category, criteria_obj)
        accidents.get_data()
        graphics = accidents.show_infographics() + button_str
    except:
        start_str = '<div class="row mb-3"><div class="col-md-12">'
        end_str = '</div></div>'
        content_str = '<p><b>Error! Please, enter proper value!</b></p>'
        graphics = start_str + content_str + button_str + end_str

    f = open("templates/analysis.html", "w")
    begin_str = '{% extends "layout.html" %}{% block body %}'
    end_str = '{% endblock %}'
    body_str = f'<div class="col-md-8 col-md-offset-2" style="border-radius:25px;background:white;height:auto;padding:20px 40px 20px 60px;">{graphics}</div>'
    page_str = begin_str + body_str + end_str
    f.write(page_str)
    f.close()
    return render_template("analysis.html")


if __name__ == '__main__':
    app.run(debug=True)